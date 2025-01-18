# WasteForecasting

- ForecastingWebApplication: 
https://wasteforecasting-jjca749rrdzm6b6hhvbvwx.streamlit.app/

- Web Application: 
https://waste-management-system-841c1.web.app/

# Overview
This project aims to empower stakeholders to make informed decisions through proactive planning, resource allocation, and effective garbage collection, encouraging sustainable waste management practices and contributing to Malaysia's environmental preservation efforts

# Features
1. # Web Application
   - Built using HTML, CSS & JavaScript
   - Hosted on Firebase Hosting
   - Native Frontend Framework: HTML and CSS
     HTML and CSS are used to design and structure the web application, providing a clean and responsive interface. These foundational web technologies enable custom page-by-page development, ensuring the application aligns with       
     specific project requirements while seamlessly integrating real-time data from Firebase for user interactions.

   - Backend: Firebase Hosting
     Firebase Hosting serves as the backend platform, offering a secure, scalable, and fast environment to host the web application. It simplifies the deployment process, ensuring smooth delivery of static assets like HTML, CSS, and           JavaScript files to users worldwide.

   - Database: Firebase Realtime Database
     Firebase Realtime Database is the primary data management tool, offering real-time synchronization between the web application and stored telemetry data. This ensures efficient storage and retrieval of sensor data, enabling dynamic       updates and smooth functionality for the application.
   
2. Forecasting Web Application
   - Built using Python
   - Hosted on Streamlit Cloud
   - Prediction Algorithm Used: Prophet
   - Allows relevant stakeholders to visualize and analyze waste accumulation data effectively. 
   
3. Mobile Application
   - Built using HTML, CSS & JavaScript
   - Hosted on Firebase Hosting
   - To develop this mobile app, the system will leverage Progressive Web App (PWA) technology, which involves transforming an existing web application into a mobile-friendly and app-like experience. 
   - By utilizing PWA principles, the app will benefit from responsive design techniques that ensure optimal display and functionality across various devices, including smartphones and tablets.

4. Waste Sensor Prototype
   - Built using Arduino UNO Wi-Fi Rev 2 & Two Ultrasonic Sensors
   - Compiled in C language in Arduino IDE
   - Essentially, the waste sensor prototpye will:
       - Connect to WiFi
       - Connect Firebase using the host and authentication token
       - Check whether the bin is closed
       - Only activate the waste level measurement if the bin is closed
       - Publish telemetry to Firebase

  
# Limitation
- Low Power Mode:
    - Essentially, while planning to connect the "bin" to a power source, while this may overcome the power concerns of the Arduino Device it does not seem too practical.
    - Further improvements should be made on how to tackle the low power modes of Arduino Device.
 
# Usage
1. Web Application
   - Access the web application link to enter the web application
   - Login with credentials to access the web application
   - Access into the web application achieved
   - User Manual Available in the Dashboard Page of the web application

2. Forecasting Web Application
   - Access the link to be redirected to the web application from the dashboard page
   - Choose from available Level Sensors for forecasting
   - Choose between time range of 1 week, 1 month, and 1 year to be forecasted
   - Click "Forecast Now"
   - User can view forecasted waste levels and line chart of forecasted levels for chosen time range

3. Web Application
   - Similar to Web Application
   - To host and deploy app in firebase:
      - Install Node.js and npm: Download and install Node.js, which includes npm.
      - Install Firebase CLI: Open your terminal and run:    
         ```bash
         pip install requests tkinter matplotlib
         ```
      - Login to firebase in CLI
        ```bash
        firebase login
        ```
      - Initialize Firebase
        ```bash
        firebase init
        ```
      - Choose your application and follow guide
      - Deploy app to firebase
        ```bash
        firebase deploy
        ```
        
# Code Highlights
## Waste Bin Prototype (WiFi Connection Setup)
```python
// Wi-Fi configuration
#define WIFI_SSID "Mathen"
#define WIFI_PASSWORD "mathen24"

// Attempt to connect to Wi-Fi
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
```

## Ultrasonic Sensor Reading
```python
// Measure waste level using Sensor 1
void measureWasteLevel() {
    digitalWrite(sensor1TrigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(sensor1TrigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(sensor1TrigPin, LOW);

    duration = pulseIn(sensor1EchoPin, HIGH);
    distance = duration * 0.034 / 2; // Distance in cm
    level = (35 - distance) * 100 / 35; // Convert to percentage

    if (level < 0) level = 0;
    if (level > 100) level = 100;

    Serial.print("Measured waste level: ");
    Serial.print(level);
    Serial.println(" %");
}

// Check if the bin is closed using Sensor 2
bool IsBinClosed() {
    digitalWrite(sensor2TrigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(sensor2TrigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(sensor2TrigPin, LOW);

    duration = pulseIn(sensor2EchoPin, HIGH);
    distance = duration * 0.034 / 2; // Distance in cm

    Serial.print("Sensor 2 distance: ");
    Serial.print(distance);
    Serial.println(" cm");

    return (distance <= thresholdDistance);
}
```

## Main Logic (Loop)
```python
void loop() {
    if (IsBinClosed()) {
        Serial.println("Bin is closed.");
        delay(1000); // Wait for a moment before measuring
        measureWasteLevel();
        if (!updateFirebaseWithRetry()) {
            logErrorToFirebase("Failed to update Firebase after retries.");
        }
    } else {
        Serial.println("Bin is open. Please wait for it to close.");
    }

    delay(15000); // Delay 15 seconds before the next measurement
}
```

## Updating Firebase
```python
// Update waste level in Firebase with retries
bool updateFirebaseWithRetry() {
    unsigned long unixTimestamp = getNTPTime(); // Get accurate timestamp
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

// Log errors to Firebase
void logErrorToFirebase(String errorMessage) {
    String path = "/SystemLogs/LastError";
    if (Firebase.setString(firebaseData, path, errorMessage)) {
        Serial.println("Error logged to Firebase successfully.");
    } else {
        Serial.print("Failed to log error to Firebase: ");
        Serial.println(firebaseData.errorReason());
    }
}
```

# References
Firebase:
- https://firebase.google.com/docs

Streamlit:
- https://docs.streamlit.io/


