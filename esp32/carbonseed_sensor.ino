/*
  ESP32 Sensor Integration for Carbonseed
  
  This Arduino sketch reads data from multiple sensors and sends it 
  to the Carbonseed backend API.
  
  Hardware Required:
  - ESP32 Dev Board
  - DHT22 (Temperature & Humidity)
  - MQ-135 (Gas/Air Quality)
  - MPU6050 (Accelerometer for vibration)
  - ACS712 (Current sensor for power monitoring)
  
  Libraries Required:
  - WiFi
  - HTTPClient
  - ArduinoJson
  - DHT sensor library
  - Adafruit MPU6050
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// API endpoint
const char* serverUrl = "http://your-backend-url:8000/ingest";

// Device ID (unique per ESP32)
const char* deviceId = "ESP32-SF-001";

// Pin definitions
#define DHTPIN 4
#define DHTTYPE DHT22
#define GAS_SENSOR_PIN 34
#define CURRENT_SENSOR_PIN 35

// Sensor objects
DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu;

// Timing
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 300000; // 5 minutes in milliseconds

void setup() {
  Serial.begin(115200);
  
  // Initialize WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Initialize sensors
  dht.begin();
  
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
  }
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastSendTime >= sendInterval) {
    sendSensorData();
    lastSendTime = currentTime;
  }
  
  delay(1000);
}

void sendSensorData() {
  // Read sensors
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  int gasRaw = analogRead(GAS_SENSOR_PIN);
  float gasIndex = map(gasRaw, 0, 4095, 0, 500);
  
  int currentRaw = analogRead(CURRENT_SENSOR_PIN);
  float current = (currentRaw - 2048) * 0.0244; // Convert to Amps
  float powerConsumption = current * 230; // Assuming 230V
  
  // Read accelerometer
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Create JSON payload
  StaticJsonDocument<512> doc;
  doc["device_id"] = deviceId;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["gas_index"] = gasIndex;
  doc["vibration_x"] = a.acceleration.x;
  doc["vibration_y"] = a.acceleration.y;
  doc["vibration_z"] = a.acceleration.z;
  doc["power_consumption"] = powerConsumption;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send HTTP POST
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error sending data: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("WiFi disconnected");
  }
  
  // Print sensor readings
  Serial.println("\n--- Sensor Readings ---");
  Serial.println("Temperature: " + String(temperature) + "°C");
  Serial.println("Humidity: " + String(humidity) + "%");
  Serial.println("Gas Index: " + String(gasIndex));
  Serial.println("Vibration X: " + String(a.acceleration.x));
  Serial.println("Vibration Y: " + String(a.acceleration.y));
  Serial.println("Vibration Z: " + String(a.acceleration.z));
  Serial.println("Power: " + String(powerConsumption) + "W");
  Serial.println("----------------------\n");
}
