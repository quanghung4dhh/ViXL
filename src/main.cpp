#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h" // This library works for MAX30102 as well

MAX30105 particleSensor;

// Define your custom I2C pins
#define I2C_SDA 23
#define I2C_SCL 22

void setup()
{
  Serial.begin(115200);
  
  // Initialize I2C with your specific pins
  Wire.begin(I2C_SDA, I2C_SCL);

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) // Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30102 was not found. Please check wiring/power. ");
    while (1);
  }

  // Setup the sensor for high sensitivity
  byte ledBrightness = 60; // Options: 0=Off to 255=50mA
  byte sampleAverage = 4; // Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 2; // Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  int sampleRate = 100; // Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; // Options: 69, 118, 215, 411
  int adcRange = 4096; // Options: 2048, 4096, 8192, 16384

  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
}

void loop()
{
  // Read the IR and Red values
  // We generally use IR for heart rate as it detects blood flow changes better
  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();

  // Print to serial in a format Python can easily parse: "Red,IR"
  // We check for 0 to avoid plotting noise if finger is removed
  if (irValue > 50000) { 
      Serial.print(redValue);
      Serial.print(",");
      Serial.println(irValue);
  } else {
      Serial.println("0,0"); // Finger removed
  }
}