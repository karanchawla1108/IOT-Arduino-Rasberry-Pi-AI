#include <WiFiS3.h>
#include <ThingSpeak.h>
#include <DHT.h>
#include <SoftwareSerial.h>

// ---------------- WiFi credentials ----------------
char ssid[] = "Wifi-Username"; // Wifi Address
char pass[] = "Wifi-Password"; // Wifi Password

// ---------------- ThingSpeak ----------------
unsigned long channelID = 3215354; // Think speak Channel Id 
const char* writeAPIKey = "NGCB9JOU2QPA0E2F"; // Think speak write API
WiFiClient client;

// ---------------- DHT11 ----------------
#define DHT_PIN 4
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

// ---------------- PIR / LED / Buzzer ----------------
const int pirPin = 3;
const int ledPin = 6;
const int buzzerPin = 8;

int pirState = LOW;
unsigned long buzzerStartTime = 0;
unsigned long lastThingSpeakTime = 0;

const unsigned long buzzerDuration = 100;      // ms
const unsigned long thingSpeakInterval = 20000; // ms

// ---------------- Bluetooth (HC-05) ----------------
SoftwareSerial btSerial(10, 11); // RX, TX

void setup() {
  Serial.begin(9600);
  btSerial.begin(9600);

  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  digitalWrite(ledPin, LOW);
  noTone(buzzerPin);

  Serial.println("System starting...");
  btSerial.println("BT_STATUS: Arduino ready");

  dht.begin();
  delay(2000);

  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  ThingSpeak.begin(client);
}

void loop() {
  unsigned long currentTime = millis();

  // -------- PIR SENSOR --------
  int val = digitalRead(pirPin);

  // Motion started
  if (val == HIGH && pirState == LOW) {
    pirState = HIGH;

    digitalWrite(ledPin, HIGH);
    tone(buzzerPin, 3000);
    buzzerStartTime = currentTime;

    Serial.println("Motion Detected");
    btSerial.println("EVENT:MOTION_STARTED");
  }

  // Motion ended
  if (val == LOW && pirState == HIGH) {
    pirState = LOW;

    digitalWrite(ledPin, LOW);
    noTone(buzzerPin);

    Serial.println("Motion Ended");
    btSerial.println("EVENT:MOTION_ENDED");
  }

  // Stop buzzer after short duration
  if (currentTime - buzzerStartTime >= buzzerDuration) {
    noTone(buzzerPin);
  }

  // -------- DHT11 + ThingSpeak --------
  if (currentTime - lastThingSpeakTime >= thingSpeakInterval) {
    lastThingSpeakTime = currentTime;

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (!isnan(temperature) && !isnan(humidity)) {

      btSerial.print("DATA:");
      btSerial.print(temperature);
      btSerial.print(",");
      btSerial.println(humidity);

      ThingSpeak.setField(1, temperature);
      ThingSpeak.setField(2, humidity);

      int response = ThingSpeak.writeFields(channelID, writeAPIKey);

      Serial.print("Temp: ");
      Serial.print(temperature);
      Serial.print(" °C | Humidity: ");
      Serial.print(humidity);
      Serial.print(" % | ThingSpeak: ");

      if (response == 200) {
        Serial.println("OK");
      } else {
        Serial.println("Error " + String(response));
      }
    } else {
      Serial.println("DHT11 read failed");
    }
  }
}
