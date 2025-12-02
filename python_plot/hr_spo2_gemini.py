import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from scipy.signal import find_peaks

# --- CẤU HÌNH ---
SERIAL_PORT = 'COM3'  # Sửa lại đúng cổng COM của bạn
BAUD_RATE = 115200
MAX_SAMPLES = 200     

# Buffer dữ liệu
ir_data = deque([0] * MAX_SAMPLES, maxlen=MAX_SAMPLES)
red_data = deque([0] * MAX_SAMPLES, maxlen=MAX_SAMPLES)

# --- THIẾT LẬP GIAO DIỆN ---
fig, (ax_ir, ax_red, ax_info) = plt.subplots(3, 1, figsize=(10, 10))
plt.subplots_adjust(hspace=0.4) # Tăng khoảng cách giữa các đồ thị

# 1. Đồ thị IR
line_ir, = ax_ir.plot([], [], 'b-', linewidth=1.5, label='IR (Heartbeat)')
ax_ir.set_title('IR Signal')
ax_ir.set_ylabel('Amplitude')
ax_ir.grid(True, linestyle='--', alpha=0.5)
ax_ir.legend(loc='upper right')

# 2. Đồ thị RED
line_red, = ax_red.plot([], [], 'r-', linewidth=1.5, label='Red Signal')
ax_red.set_title('Red Signal')
ax_red.set_ylabel('Amplitude')
ax_red.grid(True, linestyle='--', alpha=0.5)
ax_red.legend(loc='upper right')

# 3. Khu vực hiển thị Text (Đã sửa lỗi chồng chữ)
ax_info.set_xlim(0, 1) # Cố định hệ tọa độ từ 0 đến 1
ax_info.set_ylim(0, 1)
ax_info.axis('off')    # Tắt khung viền

# Đặt vị trí chữ cách xa nhau rõ ràng
text_bpm_label = ax_info.text(0.2, 0.7, 'BPM', fontsize=20, ha='center', color='green')
text_bpm = ax_info.text(0.2, 0.4, '--', fontsize=40, ha='center', color='green', fontweight='bold')

text_spo2_label = ax_info.text(0.8, 0.7, 'SpO2', fontsize=20, ha='center', color='#d62728')
text_spo2 = ax_info.text(0.8, 0.4, '-- %', fontsize=40, ha='center', color='#d62728', fontweight='bold')

text_status = ax_info.text(0.5, 0.1, 'Status: Connecting...', fontsize=12, ha='center', color='gray')

# Kết nối Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}")
    ser.reset_input_buffer()
except Exception as e:
    print(f"Error: {e}")
    exit()

def calculate_vital_signs(ir_arr, red_arr):
    if np.mean(ir_arr) < 50000:
        return 0, 0, "No Finger Detected"

    # Tính BPM
    peaks, _ = find_peaks(ir_arr, distance=15, prominence=300)
    bpm = 0
    if len(peaks) > 1:
        avg_diff = np.mean(np.diff(peaks))
        sampling_rate_est = 30 
        bpm = (60 * sampling_rate_est) / avg_diff

    # Tính SpO2
    dc_red = np.mean(red_arr)
    ac_red = np.std(red_arr)
    dc_ir = np.mean(ir_arr)
    ac_ir = np.std(ir_arr)

    if dc_red == 0 or dc_ir == 0:
        return bpm, 0, "Calculating..."

    R = (ac_red / dc_red) / (ac_ir / dc_ir)
    spo2 = 110 - 25 * R
    spo2 = np.clip(spo2, 80, 100)

    return bpm, spo2, "Measuring"

def update(frame):
    while ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if ',' in line:
                parts = line.split(',')
                if len(parts) == 2:
                    red_val = float(parts[0])
                    ir_val = float(parts[1])
                    ir_data.append(ir_val)
                    red_data.append(red_val)
        except ValueError:
            pass

    ir_arr = np.array(ir_data)
    red_arr = np.array(red_data)

    if len(ir_arr) == 0:
        return line_ir, line_red, text_bpm, text_spo2

    x_axis = range(len(ir_arr))
    line_ir.set_data(x_axis, ir_arr)
    line_red.set_data(x_axis, red_arr)
    
    # --- AUTO SCALE THÔNG MINH (Sửa lỗi đồ thị bị cắt) ---
    # Thay vì mean +/- 1000, ta dùng min/max thực tế + khoảng đệm (padding)
    if len(ir_arr) > 10:
        # Scale IR
        min_ir, max_ir = np.min(ir_arr), np.max(ir_arr)
        margin_ir = (max_ir - min_ir) * 0.1 # Đệm thêm 10%
        if margin_ir == 0: margin_ir = 100
        ax_ir.set_ylim(min_ir - margin_ir, max_ir + margin_ir)
        ax_ir.set_xlim(0, MAX_SAMPLES)

        # Scale Red
        min_red, max_red = np.min(red_arr), np.max(red_arr)
        margin_red = (max_red - min_red) * 0.1
        if margin_red == 0: margin_red = 100
        ax_red.set_ylim(min_red - margin_red, max_red + margin_red)
        ax_red.set_xlim(0, MAX_SAMPLES)

    # Tính toán BPM/SpO2
    if frame % 5 == 0 and len(ir_arr) == MAX_SAMPLES:
        bpm, spo2, status = calculate_vital_signs(ir_arr, red_arr)
        
        if status == "No Finger Detected":
            text_bpm.set_text("--")
            text_spo2.set_text("-- %")
            text_status.set_text(status)
            text_status.set_color('red')
        else:
            text_bpm.set_text(f"{bpm:.0f}")
            text_spo2.set_text(f"{spo2:.1f} %")
            text_status.set_text(status)
            text_status.set_color('blue')

    return line_ir, line_red, text_bpm, text_spo2, text_status

ani = FuncAnimation(fig, update, interval=30)
plt.show()
ser.close()