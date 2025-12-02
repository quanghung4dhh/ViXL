import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections

# --- CẤU HÌNH ---
# Thay đổi thành cổng COM của ESP32 (Windows: COMx, Mac/Linux: /dev/ttyUSBx)
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200
MAX_SAMPLES = 200     # Số lượng điểm hiển thị trên đồ thị

# Khởi tạo Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.flushInput()
except Exception as e:
    print(f"Lỗi kết nối Serial: {e}")
    exit()

# Hàng đợi dữ liệu (tự động xóa dữ liệu cũ khi đầy)
data_q = collections.deque(maxlen=MAX_SAMPLES)
# Khởi tạo dữ liệu ban đầu là 0
for _ in range(MAX_SAMPLES):
    data_q.append(0)

# Thiết lập biểu đồ
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

# Trang trí biểu đồ
ax.set_ylim(0, 4095)  # ESP32 ADC là 12-bit (0-4095)
ax.set_xlim(0, MAX_SAMPLES)
ax.set_title('Tín hiệu AD8232 Raw (ECG)')
ax.set_xlabel('Mẫu (Time)')
ax.set_ylabel('Biên độ (ADC Value)')
ax.grid(True)


def update(frame):
    try:
        if ser.in_waiting > 0: # Kiểm tra xem có dữ liệu không
            # Đọc và decode, bỏ khoảng trắng thừa
            raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # Chỉ xử lý nếu chuỗi là số nguyên
            if raw_line.isdigit():
                value = int(raw_line)
                data_q.append(value)
                line.set_data(range(MAX_SAMPLES), data_q)
    except Exception as e:
        print(f"Error: {e}")
    
    return line,


# Chạy animation
ani = FuncAnimation(fig, update, interval=20, blit=True)  # interval=20ms
plt.show()

# Đóng serial khi tắt cửa sổ
ser.close()
