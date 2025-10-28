#include <Arduino.h>

const int ECG_PIN = 34;    // ADC1 pin recommended for ESP32
const unsigned long BAUD = 9600;
const unsigned long SAMPLE_MS = 4; // 250Hz sample => 4ms per sample (tune as needed)

void setup() {
  Serial.begin(BAUD);
  // Allow ESP32 to boot fully
  delay(2000);
  // ADC config (optional): attenuation to read wider range
  analogSetPinAttenuation(ECG_PIN, ADC_11db); // read up to ~3.3V
}

void loop() {
  // read raw ADC (0-4095 on 12-bit default)
  int raw = analogRead(ECG_PIN);
  // print timestamp (ms) and value, comma separated
  Serial.print(millis());
  Serial.print(',');
  Serial.println(raw);

  delay(SAMPLE_MS);
}
