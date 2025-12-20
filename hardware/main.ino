#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h> // You need to install ArduinoJson library

#define DHTPIN 17
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define MQ135_PIN 34

// --- WI-FI SETTINGS ---
const char* ssid = "Redmi Note 11T 5G";
const char* password = "yyyyyytttt";
// REPLACE with your Laptop's Local IP (Run 'ipconfig' on Windows)
const char* serverUrl = "http://10.82.191.201:8080/api/sensor/data"; 

float calibration_factor = 100.0;
#define CO2_LOW 400
#define CO2_HIGH 1000
#define AQI_LOW 0
#define AQI_HIGH 50

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int mq135_value = analogRead(MQ135_PIN);

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read DHT");
    return;
  }

  float ppm = mq135_value / calibration_factor;
  int aqi = map(ppm, CO2_LOW, CO2_HIGH, AQI_LOW, AQI_HIGH);
  aqi = constrain(aqi, AQI_LOW, AQI_HIGH);

  // Send to Server
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Create JSON Payload
    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["mq135_raw"] = mq135_value;
    doc["co2_ppm"] = ppm;
    doc["aqi"] = aqi;

    String jsonStr;
    serializeJson(doc, jsonStr);

    int httpResponseCode = http.POST(jsonStr);
    
    if (httpResponseCode > 0) {
      Serial.print("Data Sent! Response: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error sending data: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

  delay(5000); // Send every 5 seconds
}