#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include "soil_svm.h"

// =========================
// PIN DEFINITIONS
// =========================

// Soil moisture (potentiometer)
#define SOIL_PIN 34

// DHT22
#define DHT_PIN 4
#define DHT_TYPE DHT22

// OLED
#define OLED_SDA 21
#define OLED_SCL 22
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDRESS 0x3C

// =========================
// OBJECTS
// =========================

DHT dht(DHT_PIN, DHT_TYPE);

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  -1
);

// =========================
// SETUP
// =========================

void setup() {

  Serial.begin(115200);

  // ADC resolution
  analogReadResolution(12);

  // Start DHT22
  dht.begin();

  // Start OLED
  Wire.begin(OLED_SDA, OLED_SCL);

  if (!display.begin(
        SSD1306_SWITCHCAPVCC,
        OLED_ADDRESS
      )) {

    Serial.println("OLED not detected!");

    while (true);
  }

  // Initial OLED screen
  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.println("AI SOIL MONITOR");

  display.setCursor(0, 20);
  display.println("Initializing...");

  display.display();

  delay(2000);
}

// =========================
// LOOP
// =========================

void loop() {

  // -------------------------
  // READ SOIL MOISTURE
  // -------------------------

  int soilRaw = analogRead(SOIL_PIN);

  // Convert raw ADC to percentage
  int soilMoisture = map(
    soilRaw,
    0,
    4095,
    0,
    100
  );

  soilMoisture = constrain(
    soilMoisture,
    0,
    100
  );

  // -------------------------
  // READ DHT22
  // -------------------------

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check DHT22
  if (isnan(temperature) || isnan(humidity)) {

    Serial.println("DHT22 reading failed!");

    display.clearDisplay();

    display.setCursor(0, 0);
    display.println("AI SOIL MONITOR");

    display.setCursor(0, 20);
    display.println("DHT22 ERROR");

    display.display();

    delay(2000);

    return;
  }

  // -------------------------
  // DETERMINE STATUS
  // -------------------------

  // Trained RBF SVM inference runs directly on the ESP32.
  String status = predictSoil(soilMoisture, temperature, humidity);

  // =========================
  // SERIAL MONITOR
  // =========================

  Serial.println("========================");

  Serial.print("Soil Raw: ");
  Serial.println(soilRaw);

  Serial.print("Soil Moisture: ");
  Serial.print(soilMoisture);
  Serial.println("%");

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println("%");

  Serial.print("Status: ");
  Serial.println(status);

  // =========================
  // OLED DISPLAY
  // =========================

  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // Title
  display.setCursor(0, 0);
  display.println("AI SOIL MONITOR");

  // Soil
  display.setCursor(0, 14);
  display.print("Soil: ");
  display.print(soilMoisture);
  display.println("%");

  // Temperature
  display.setCursor(0, 26);
  display.print("Temp: ");
  display.print(temperature, 1);
  display.println(" C");

  // Humidity
  display.setCursor(0, 38);
  display.print("Hum:  ");
  display.print(humidity, 1);
  display.println("%");

  // Status
  display.setCursor(0, 52);
  display.print("Status: ");
  display.println(status);

  display.display();

  delay(2000);
}