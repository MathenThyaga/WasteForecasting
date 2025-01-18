# WasteForecasting

- ForecastingWebApplication: 
https://wasteforecasting-jjca749rrdzm6b6hhvbvwx.streamlit.app/

- Web Application: 
https://waste-management-system-841c1.web.app/

# Overview
This project aims to empower stakeholders to make informed decisions through proactive planning, resource allocation, and effective garbage collection, encouraging sustainable waste management practices and contributing to Malaysia's environmental preservation efforts

# Features
1. Web Application
   - Built using HTML, CSS & JavaScript
   - Hosted on Firebase Hosting
   - Native Frontend Framework: HTML and CSS
     HTML and CSS are used to design and structure the web application, providing a clean and responsive interface. These foundational web technologies enable custom page-by-page development, ensuring the application aligns with specific      project requirements while seamlessly integrating real-time data from Firebase for user interactions.

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

# Dependencies
# Python Libraries:
- `os`
- `requests`
- `tkinter`
- `matplotlib`
- `re`
- External SDKs: `inference_sdk`

# File Structure

# Usage
# API Configuration
# Code Highlights

# References



