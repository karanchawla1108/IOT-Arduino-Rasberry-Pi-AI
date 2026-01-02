# IoT + Edge AI Home Security System

The project develops a home security system using the Internet of Things (IoT) with the incorporation of Edge Artificial Intelligence with the aim of eliminating the problem of False Alarm Rates, ensuring the user’s privacy, as well as ensuring minimal operational costs, contrary to cloud-based security systems.

The system is able to capture images on demand, and human vs. non-human classification is performed on the raspberry Pi using an efficient YOLO-based model. Environment data is uploaded to the cloud and alerting happens via push notification using NTFY. The system is able to detect motion using a PIR sensor.

This project was created for the COM6017M - Internet of Things module offered by York St John University.
## System Architecture
The system follows a distributed IoT architecture with a clear separation of responsibilities:

- Arduino – sensing and local control

- Raspberry Pi – edge computing, image capture, and AI inference

- Cloud services – data storage, visualisation, and notifications

An event-driven approach ensures that computationally intensive tasks are only performed when motion is detected.

## Hardware Components
- Arduino Uno

- Raspberry Pi

- PIR Motion Sensor

- DHT11 Temperature & Humidity Sensor

- HC-05 Bluetooth Module

- Raspberry Pi Camera Module

- LED / Buzzer 

## Software Technologies
- Arduino IDE – microcontroller programming

- Python – edge device software

- YOLOv8n – lightweight object detection model for Edge AI

- OpenCV – image handling

- ThingSpeak – cloud data storage and visualisation

- NTFY – internet-based push notification service

- Bluetooth (HC-05) – machine-to-machine (M2M) communication

## How the System Works
- The PIR sensor continuously monitors for motion.

- On detection of motion, the Arduino triggers an event, which is sent to  the Raspberry Pi through Bluetooth.

- The Raspberry Pi turns on the camera and takes a picture.

- The edge AI inference operation classifies the picture as human or non-human.

- It sends a real-time alert notification with an image taken and classification via the message NTFY. https://ntfy.sh/

- The temperatures and humidity information are periodically collected and sent to ThingSpeak for processing. 

## Edge AI Functionality
The classification of human vs. non-human is done on the Raspberry Pi itself using the YOLOv8n model. Performing the task on the device cuts down on the latency, as well as not having to send the sensitive image to the cloud unnecessarily.

## Data Analytics & Cloud Integration
Data pertaining to the environmental parameters collected using the DHT11 sensor is then uploaded to ThingSpeak, and the data isprocessed and displayed as Time-series plots on ThingSpeak.

Event data, such as motion events, and the results of classifications, serve in proving the efficacy of Edge AI in false alarm reduction.

## Push Notifications (NTFY)
The system relies on the use of NTFY to transmit real-time push notifications to the user via the internet. The notifications will contain contextual data such as motion timestamps, classification, and images captured. The choice of NTFY was influenced by its light-weighted nature and the fact that it is easy to integrate, without necessarily requiring the development of a smartphone app.

## Repository Structure


```
  |--Arduino Architecture.fzz (Fritzing file)
  |
  |--Rasberry Architecture.fzz (Fritzing file)
  |
  |-- Main codes (Rasberry Pie codes)
  |   └── bt_connect.sh
  |    └── motion_camera_notify2.py (Without Ai )
  |   └── motion_camera_notify3.py (With Ai)
  |
  |-- Arduino Code
      └── sketch_dec30b_update_PIR_sensor
 
```

## How to Run

   1. Upload the Arduino sketch using the Arduino IDE.
      
   2. Upload the Rasberry Codes sketch using the Rasberry Pie.
      ```
      ./ bt_connect.sh
      Python motion_camera_notify3.py
      Python motion_camera_notify3.py

      ```

   3. Pair the HC-05 Bluetooth module with the Raspberry Pi.
       ```
      ./ bt_connect.sh
      ```

   4. Connect and enable the Raspberry Pi camera module.
       ```
      Python motion_camera_notify2.py
      ```

   5. Run the edge AI script on the Raspberry Pi:
       ```
      
      Python motion_camera_notify3.py
      ```
  
   
  6. Monitor alerts via NTFY and sensor data via ThingSpeak.

---
 

## Author

Karan Chawla

BSc (Hons) Computer Science
York St John University

---

## Disclaimer

This project was completed for academic purposes as part of a university assessment. The findings should not be considered as production-ready without further validation and testing.