import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from collections import deque

# ==== CONFIG ====
PORT = "COM3"     # Change to your port
BAUD = 9600
WINDOW = 500      # Number of samples for display
FS = 50           # Sampling rate (Hz)
REFRESH_RATE = 0.05  # seconds between plot updates

# ==== SERIAL SETUP ====
ser = serial.Serial(PORT, BAUD)
time.sleep(2)

ir_values = deque([0]*WINDOW, maxlen=WINDOW)
red_values = deque([0]*WINDOW, maxlen=WINDOW)

# ==== PLOT SETUP ====
plt.ion()
fig, ax = plt.subplots()
line_ir, = ax.plot(ir_values, label="IR", color='red')
line_red, = ax.plot(red_values, label="Red", color='orange', alpha=0.6)
ax.legend()
ax.set_title("MAX30102 PPG with HR & SpO2")
ax.set_xlabel("Samples")
ax.set_ylabel("Signal")

bpm_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
spo2_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)


def calculate_hr(ir_signal):
    peaks, _ = find_peaks(ir_signal, distance=FS*0.5)  # min 0.5s apart
    if len(peaks) > 1:
        peak_intervals = np.diff(peaks) / FS
        avg_period = np.mean(peak_intervals)
        bpm = 60.0 / avg_period
        return bpm
    return None


def calculate_spo2(ir_signal, red_signal):
    # AC: remove DC offset (mean)
    ir_ac = ir_signal - np.mean(ir_signal)
    red_ac = red_signal - np.mean(red_signal)
    ir_dc = np.mean(ir_signal)
    red_dc = np.mean(red_signal)

    ratio = (red_ac / red_dc) / (ir_ac / ir_dc)
    R = np.mean(np.abs(ratio))
    spo2 = 110 - 25 * R   # empirical formula
    return np.clip(spo2, 0, 100)


try:
    last_update = time.time()
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        try:
            ir, red = map(int, line.split(','))
            ir_values.append(ir)
            red_values.append(red)

            # Periodically update plot & calculations
            if time.time() - last_update > REFRESH_RATE:
                ir_arr = np.array(ir_values)
                red_arr = np.array(red_values)

                hr = calculate_hr(ir_arr)
                spo2 = calculate_spo2(ir_arr, red_arr)

                line_ir.set_ydata(ir_arr)
                line_ir.set_xdata(range(len(ir_arr)))
                line_red.set_ydata(red_arr)
                line_red.set_xdata(range(len(red_arr)))
                ax.relim()
                ax.autoscale_view()

                bpm_text.set_text(f'HR: {hr:.1f} BPM' if hr else 'HR: --')
                spo2_text.set_text(f'SpO₂: {spo2:.1f}%')
                plt.pause(0.001)

                last_update = time.time()
        except:
            pass
except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
