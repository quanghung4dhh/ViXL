#include <Arduino.h>

// --- KHAI BÁO CHÂN (PIN DEFINITIONS) ---
// AD8232 OUTPUT nối với GPIO 34 (ADC1)
// Lưu ý: GPIO 34, 35, 36, 39 trên ESP32 là chân "Input Only", đọc Analog rất tốt.
#define SENSOR_PIN  34 

// Chân phát hiện tuột miếng dán (Leads Off)
#define LO_PLUS     33
#define LO_MINUS    32

void setup() {
  // Khởi động Serial
  Serial.begin(115200);
  
  // Cấu hình chân Input
  pinMode(SENSOR_PIN, INPUT);
  pinMode(LO_PLUS, INPUT);
  pinMode(LO_MINUS, INPUT);

  // In thông báo khởi động (Chỉ in 1 lần)
  Serial.println("System Ready: AD8232 reading...");
}

void loop() {
  // 1. Kiểm tra xem miếng dán có bị tuột không
  // LO+ hoặc LO- lên mức cao tức là điện cực bị hở
  if ((digitalRead(LO_PLUS) == HIGH) || (digitalRead(LO_MINUS) == HIGH)) {
    // Gửi giá trị 0 hoặc ký tự cảnh báo để Python xử lý
    Serial.println(0); 
  } 
  else {
    // 2. Đọc giá trị Analog (0 - 4095)
    int sensorValue = analogRead(SENSOR_PIN);
    
    // Gửi giá trị thô lên Serial
    Serial.println(sensorValue);
  }

  // 3. Delay để giữ tốc độ lấy mẫu ổn định
  // 10ms ~ 100 mẫu/giây (đủ cho ECG cơ bản)
  delay(10);
}