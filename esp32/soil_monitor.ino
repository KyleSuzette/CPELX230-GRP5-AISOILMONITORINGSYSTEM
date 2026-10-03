#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// PIN DEFINITIONS
// =========================
#define SOIL_PIN 34
#define DHT_PIN 4
#define DHT_TYPE DHT22

#define OLED_SDA 21
#define OLED_SCL 22
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDRESS 0x3C


// INSTANCES
// =========================
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// NETWORK CONFIGURATION
// =========================
const char* ssid = "Wokwi-GUEST";
const char* password = "";


const char* serverEndpoint ="https://k6mx917q-5000.asse.devtunnels.ms/api/sensor";

void updateOLED(float soil, float temp, float hum, String status) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(0, 0);
  display.println("AI SOIL MONITOR");
  display.println("---------------------");
  
  display.printf("Moisture: %.1f %%\n", soil);
  display.printf("Temp:     %.1f C\n", temp);
  display.printf("Humidity: %.1f %%\n", hum);
  
  display.println("---------------------");
  display.print("Status: ");
  display.println(status);
  display.display();
}

void setup() {
  Serial.begin(115200);

  // Initialize Sensors & Peripherals
  dht.begin();
  analogReadResolution(12); // ESP32 12-bit ADC (0 - 4095)

  Wire.begin(OLED_SDA, OLED_SCL);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed!"));
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 20);
    display.println("Connecting WiFi...");
    display.display();
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[Wi-Fi Connected]");

  updateOLED(0, 0, 0, "System Ready");
}

void loop() {
  // Read Sensors
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int rawSoil = analogRead(SOIL_PIN);

  // Map 12-bit ADC (0 - 4095) to Soil Moisture Percentage (0 - 100%)
  float soilMoisturePct = map(rawSoil, 0, 4095, 0, 100);

  if (isnan(temp) || isnan(hum)) {
    Serial.println("DHT sensor read failed!");
    updateOLED(soilMoisturePct, 0, 0, "Sensor Error");
    delay(2000);
    return;
  }

  Serial.printf("\nTelemetry -> Soil: %.1f%% | Temp: %.1f C | Hum: %.1f%%\n",
                soilMoisturePct, temp, hum);

  String predictionStr = "Connecting...";

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverEndpoint);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> payloadDoc;
    payloadDoc["soil_moisture"] = soilMoisturePct;
    payloadDoc["temperature"] = temp;
    payloadDoc["humidity"] = hum;

    String jsonString;
    serializeJson(payloadDoc, jsonString);

    int httpCode = http.POST(jsonString);
    if (httpCode == 200) {
      String response = http.getString();
      Serial.println("Server Response: " + response);

      StaticJsonDocument<300> resDoc;
      DeserializationError err = deserializeJson(resDoc, response);
      if (err || !resDoc["prediction"].is<const char*>()) {
        predictionStr = "Response Error";
      } else {
        predictionStr = String(resDoc["prediction"].as<const char*>());
      }


    } else {
      Serial.printf("HTTP Error, Code: %d\n", httpCode);
      predictionStr = "API Error";
    }
    http.end();
  } else {
    predictionStr = "No WiFi";
  }

  // Update OLED Display
  updateOLED(soilMoisturePct, temp, hum, predictionStr);

  delay(4000); // 4-second sampling interval
}