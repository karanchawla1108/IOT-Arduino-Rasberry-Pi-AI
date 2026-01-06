# -*- coding: utf-8 -*-
import serial
import subprocess
import time
import os
from datetime import datetime
import cv2
from ultralytics import YOLO

BT_PORT = "/dev/rfcomm0"
BAUD = 9600

NTFY_TOPIC = "https://ntfy.sh/DragonBallZ"
IMAGE_DIR = "/home/ysj/Desktop/codes/Image"

motion_active = False

# Load YOLO model (will download automatically on first run)
print("Using YOLO model...")
model = YOLO('yolov8n.pt')  # nano version - fastest and lightest

# Create image directory if it doesn't exist
os.makedirs(IMAGE_DIR, exist_ok=True)

def capture_image():
    print("Capturing image...")
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(IMAGE_DIR, f"intruder_{timestamp}.jpg")
    
    subprocess.run([
        "rpicam-still",
        "-o", image_path,
        "--width", "640",
        "--height", "480",
        "--quality", "85",  # Increased quality for better YOLO detection
        "--nopreview"
    ], check=True)
    
    return image_path

def analyze_image_with_yolo(image_path):
    """Detect humans using YOLO"""
    print("Analyzing image with YOLO...")
    
    try:
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            print("ERROR: Could not read image")
            return "Image read failed"
        
        # Run YOLO detection
        results = model(img, verbose=False)
        
        # DEBUG: Print all detections
        print(f"Total detections: {len(results[0].boxes)}")
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model.names[cls]
            print(f"  - {class_name}: {conf:.2f}")
        
        # Check for person detection (class 0 is 'person' in COCO dataset)
        human_detected = False
        human_count = 0
        detected_objects = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Get class name
                class_name = model.names[cls]
                
                # Check if person detected with confidence > 0.4 (lowered threshold)
                if cls == 0 and conf > 0.4:
                    human_detected = True
                    human_count += 1
                    print(f"HUMAN FOUND: confidence {conf:.2f}")
                elif conf > 0.4:
                    detected_objects.append(class_name)
        
        # Generate analysis message
        if human_detected:
            if human_count == 1:
                analysis = f"HUMAN DETECTED - 1 person detected"
            else:
                analysis = f"HUMAN DETECTED - {human_count} people detected"
        else:
            if detected_objects:
                objects_str = ", ".join(set(detected_objects[:3]))
                analysis = f"NO HUMAN - Detected: {objects_str}"
            else:
                analysis = "NO HUMAN - No significant objects detected"
        
        print(f"YOLO Analysis: {analysis}")
        return analysis
        
    except Exception as e:
        print(f"YOLO Error: {e}")
        return "Detection failed"
        
def send_notification(message, image_path, ai_analysis):
    print("Sending ntfy notification...")
    
    # Determine if human detected
    if "HUMAN DETECTED" in ai_analysis.upper():
        alert_title = "ALERT: HUMAN DETECTED"
        tags = "warning,skull,human"
    else:
        alert_title = "No Human Detected"
        tags = "white_check_mark,camera"
    
    # Full message with AI analysis
    full_message = f"{message} - {ai_analysis}"
    
    try:
        # Send image with message in header (FIXED: removed -d flag)
        result = subprocess.run([
            "curl",
            "-H", f"Title: {alert_title}",
            "-H", "Priority: high",
            "-H", f"Tags: {tags}",
            "-H", f"Message: {full_message}",
            "-H", "Filename: intruder.jpg",
            "-T", image_path,
            NTFY_TOPIC
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Notification sent successfully")
        else:
            print(f"NTFY Error: {result.stderr}")
            
    except subprocess.CalledProcessError as e:
        print(f"NTFY Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

print("=" * 50)
print("IoT Home Security System - STARTED")
print("=" * 50)
print(f"Listening for Bluetooth motion events on {BT_PORT}")
print(f"Images will be saved to: {IMAGE_DIR}")
print(f"NTFY Topic: {NTFY_TOPIC}")
print("=" * 50)

ser = serial.Serial(BT_PORT, BAUD, timeout=1)


while True:
    try:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            continue

        print("Received (raw):", line)

        # Ignore corrupted data
        if not line.startswith("EVENT:"):
            continue

        if line == "EVENT:MOTION_STARTED" and not motion_active:
            motion_active = True
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print("\n" + "=" * 50)
            print(f"MOTION DETECTED at {timestamp}")
            print("=" * 50)

            # Capture image
            image_path = capture_image()
            print(f"Image saved to: {image_path}")
            
            # Analyze with YOLO
            ai_analysis = analyze_image_with_yolo(image_path)
            
            # Send notification
            send_notification(
                f"Motion detected at {timestamp}",
                image_path,
                ai_analysis
            )

            print("=" * 50 + "\n")

        if line == "EVENT:MOTION_ENDED":
            motion_active = False
            print("Motion ended, system re-armed\n")

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Exiting IoT Security System...")
        print("=" * 50)
        break

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)

