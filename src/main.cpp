#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"

MAX30105 particleSensor;

void setup() {
  Wire.begin(22, 23);
  Serial.begin(9600);
  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found. Check wiring/power.");
    while (1);
  }
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x1F);   // stronger LED for SPO2
  particleSensor.setPulseAmplitudeIR(0x1F);
  particleSensor.setPulseAmplitudeGreen(0);
}

void loop() {
  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();

  // send comma-separated values over serial
  Serial.print(irValue);
  Serial.print(",");
  Serial.println(redValue);

  delay(20); // 50 Hz
}
