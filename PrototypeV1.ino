#include <WiFiNINA.h>
#include <Firebase_Arduino_WiFiNINA.h>
#include <WiFiUdp.h>

// Firebase configuration
#define FIREBASE_HOST "waste-management-system-841c1-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "kBb9EAonV23wNiccVA3GMJwFrdONZ9nxewbwabRM"
#define WIFI_SSID "Mathen"
#define WIFI_PASSWORD "mathen24"

FirebaseData firebaseData;
WiFiUDP udp; // For NTP

// NTP Configuration
const char* ntpServer = "pool.ntp.org";
const int ntpPort = 123;
const int timeZoneOffset = 28800; // Offset in seconds for your timezone (e.g., 8 hours for UTC+8)

// Ultrasonic sensor pins
const int sensor1TrigPin = 2;
const int sensor1EchoPin = 3;
const int sensor2TrigPin = 4;
const int sensor2EchoPin = 5;
const int thresholdDistance = 5;

float duration, distance, level;

// Firebase base path
String basePath = "/Devices/LevelSensorArduinoBin/Level";

void setup() {
  Serial.begin(9600);
  Serial.println("Initializing...");

  pinMode(sensor1TrigPin, OUTPUT);
  pinMode(sensor1EchoPin, INPUT);
  pinMode(sensor2TrigPin, OUTPUT);
  pinMode(sensor2EchoPin, INPUT);

  // Connect to Wi-Fi
  Serial.print("Connecting to WiFi...");
  int status = WL_IDLE_STATUS;
  int retries = 5;
  while (status != WL_CONNECTED && retries > 0) {
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print(".");
    delay(1000);
    retries--;
  }
  if (status == WL_CONNECTED) {
    Serial.println(" Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connection failed!");
  }

  // Initialize Firebase
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH, WIFI_SSID, WIFI_PASSWORD);
  Firebase.reconnectWiFi(true);

  // Initialize NTP
  udp.begin(ntpPort);
}

void loop() {
  if (IsBinClosed()) {
    Serial.println("Bin is closed.");
    delay(1000);
    measureWasteLevel();
    if (!updateFirebaseWithRetry()) {
      logErrorToFirebase("Failed to update Firebase after retries.");
    }
  } else {
    Serial.println("Bin is open. Please wait for it to close.");
  }

  delay(15000); // Delay 15 seconds before the next measurement
}

void measureWasteLevel() {
  digitalWrite(sensor1TrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(sensor1TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensor1TrigPin, LOW);

  duration = pulseIn(sensor1EchoPin, HIGH);
  distance = duration * 0.034 / 2;
  level = (35 - distance) * 100 / 35;

  if (level < 0) level = 0;
  if (level > 100) level = 100;

  Serial.print("Measured waste level: ");
  Serial.print(level);
  Serial.println(" %");
}

bool IsBinClosed() {
  digitalWrite(sensor2TrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(sensor2TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(sensor2TrigPin, LOW);

  duration = pulseIn(sensor2EchoPin, HIGH);
  distance = duration * 0.034 / 2;

  Serial.print("Sensor 2 distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  return (distance <= thresholdDistance);
}

bool updateFirebaseWithRetry() {
  unsigned long unixTimestamp = getNTPTime(); // Get the accurate UNIX timestamp

  if (unixTimestamp == 0) {
    Serial.println("Failed to obtain NTP time");
    return false;
  }

  String timestampStr = String(unixTimestamp);
  String path = basePath + "/" + timestampStr;

  int retries = 3;
  while (retries > 0) {
    if (Firebase.setInt(firebaseData, path + "/Value", (int)level)) {
      Serial.println("Waste level updated successfully in Firebase.");
      Serial.print("Path: ");
      Serial.println(path);
      Serial.print("Value: ");
      Serial.println((int)level);
      return true;
    } else {
      Serial.print("Retrying Firebase update... ");
      retries--;
      delay(2000); // Wait 2 seconds before retrying
    }
  }

  Serial.println("Failed to update Firebase after retries.");
  return false;
}

void logErrorToFirebase(String errorMessage) {
  String path = "/SystemLogs/LastError";
  if (Firebase.setString(firebaseData, path, errorMessage)) {
    Serial.println("Error logged to Firebase successfully.");
  } else {
    Serial.print("Failed to log error to Firebase: ");
    Serial.println(firebaseData.errorReason());
  }
}

unsigned long getNTPTime() {
  udp.beginPacket(ntpServer, ntpPort);
  byte packetBuffer[48] = {0};
  packetBuffer[0] = 0b11100011;
  udp.write(packetBuffer, 48);
  udp.endPacket();

  delay(1000);

  int cb = udp.parsePacket();
  if (cb == 0) {
    Serial.println("No NTP response");
    return 0;
  }

  udp.read(packetBuffer, 48);
  unsigned long highWord = word(packetBuffer[40], packetBuffer[41]);
  unsigned long lowWord = word(packetBuffer[42], packetBuffer[43]);
  unsigned long secsSince1900 = (highWord << 16 | lowWord);
  unsigned long epoch = secsSince1900 - 2208988800UL + timeZoneOffset;

  return epoch;
}

// Function to put the microcontroller into sleep mode
/*
void enterSleepMode() {
  set_sleep_mode(SLEEP_MODE_IDLE);  // Set sleep mode to idle
  sleep_enable();                   // Enable sleep mode
  sleep_mode();                     // Put the microcontroller to sleep

  // The microcontroller will wake up from sleep when the next interrupt occurs (e.g., timer or serial).
  sleep_disable();                  // Disable sleep after wake-up
}
*/
