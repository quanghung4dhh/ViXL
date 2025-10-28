import serial
import serial.tools.list_ports
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from collections import deque
import csv
import sys

# ====== CONFIG ======
BAUD = 9600
PORT = "/dev/ttyUSB0"
WINDOW_S = 8            # seconds to show in window
SAMPLE_RATE = 250       # expected sampling rate in Hz (match ESP32)
MAX_SAMPLES = WINDOW_S * SAMPLE_RATE
CSV_OUT = "ecg_capture.csv"

# ====== OPEN SERIAL ======
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  # allow device to reset
except Exception as e:
    print("Không thể mở cổng serial:", e)
    sys.exit(1)

# ====== FILTER DESIGN (bandpass for ECG) ======
def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

b_bp, a_bp = butter_bandpass(0.5, 40.0, SAMPLE_RATE, order=3)  # typical ECG band

# ====== BUFFERS & PLOT SETUP ======
xs = deque(maxlen=MAX_SAMPLES)
ys = deque(maxlen=MAX_SAMPLES)

plt.ion()
fig, ax = plt.subplots(figsize=(10,4))
line, = ax.plot([], [], lw=0.8)
ax.set_xlabel("Time (s)")
ax.set_ylabel("ADC (raw)")
ax.set_title("Live ECG (AD8232)")

start_time = None

# ====== CSV SETUP ======
csv_file = open(CSV_OUT, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["timestamp_ms", "adc_raw"])

print("Bắt đầu nhận dữ liệu... Ctrl+C để dừng.")

# ====== READ LOOP ======
try:
    while True:
        ln = ser.readline().decode('utf-8', errors='ignore').strip()
        if not ln:
            continue
        # expect lines like: "12345,2048"
        try:
            t_ms_str, raw_str = ln.split(',', 1)
            t_ms = int(t_ms_str)
            raw = int(raw_str)
        except ValueError:
            # skip malformed lines
            continue

        if start_time is None:
            start_time = t_ms

        # append
        xs.append((t_ms - start_time) / 1000.0)  # seconds since start
        ys.append(raw)
        csv_writer.writerow([t_ms, raw])

        # update plot periodically
        if len(xs) >= 3:
            x_arr = np.array(xs)
            y_arr = np.array(ys).astype(np.float64)

            # detrend (remove mean) to help filtering
            y_detrend = y_arr - np.mean(y_arr)

            # apply bandpass filter if we have enough samples
            try:
                y_filt = filtfilt(b_bp, a_bp, y_detrend)
            except Exception:
                y_filt = y_detrend

            # show last window
            t_window = x_arr - x_arr[-1]
            line.set_xdata(t_window)
            line.set_ydata(y_filt)
            ax.relim()
            ax.autoscale_view()
            ax.set_xlim(t_window[0], 0)  # show negative-to-zero window (past -> present)
            plt.pause(0.001)
except KeyboardInterrupt:
    print("\nDừng, đóng file và cổng serial.")
finally:
    csv_file.close()
    ser.close()
    plt.ioff()
    plt.show()
