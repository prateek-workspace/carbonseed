# ESP32 Sensor Integration

Arduino sketch for ESP32-based edge devices to send sensor data to Carbonseed backend.

## Setup Instructions

### 1. Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### 2. Add ESP32 Board Support
- Open Arduino IDE
- Go to File → Preferences
- Add to "Additional Board Manager URLs":
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
- Go to Tools → Board → Boards Manager
- Search "ESP32" and install

### 3. Configure the Sketch
Edit `carbonseed_sensor.ino`:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://your-backend-url:8000/ingest";
const char* deviceId = "ESP32-SF-001"; // Unique per device
```

### 4. Upload to ESP32
- Connect ESP32 via USB
- Select board: Tools → Board → ESP32 Dev Module
- Select port: Tools → Port → (your COM port)
- Click Upload

### 5. Monitor Serial Output
- Open Serial Monitor (Tools → Serial Monitor)
- Set baud rate to 115200
- You should see connection status and sensor readings

## Data Transmission

The ESP32 sends data every 5 minutes (configurable) to the backend API endpoint `/ingest`.

### JSON Payload Format
```json
{
  "device_id": "ESP32-SF-001",
  "temperature": 25.5,
  "humidity": 45.2,
  "gas_index": 320.0,
  "vibration_x": 2.1,
  "vibration_y": 1.8,
  "vibration_z": 2.3,
  "power_consumption": 32.5
}
```

## Customization

### Change Transmission Interval
```cpp
const unsigned long sendInterval = 300000; // milliseconds (5 minutes)
```

### Add More Sensors
1. Define pin in the sketch
2. Read sensor value in `sendSensorData()`
3. Add to JSON payload
4. Update backend schema if needed

### Power Optimization
For battery operation, use deep sleep:
```cpp
esp_sleep_enable_timer_wakeup(300 * 1000000); // 5 minutes
esp_deep_sleep_start();
```

## Production Deployment

For factory deployment:

1. **Enclosure**: Use industrial-grade IP-rated enclosure
2. **Power**: Stable 5V power supply or battery with solar panel
3. **Mounting**: Secure mounting near monitored equipment
4. **WiFi**: Consider mesh network or industrial WiFi for coverage
5. **Security**: Implement device authentication (API keys)
6. **Monitoring**: Add watchdog timer for reliability
7. **Updates**: Plan OTA (Over-The-Air) firmware update mechanism
