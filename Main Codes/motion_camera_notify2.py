# -*- coding: utf-8 -*-
import serial
import subprocess
import time
import os
from datetime import datetime

# --- Configuration ---
BT_PORT = "/dev/rfcomm0"
BAUD = 9600
NTFY_TOPIC = "https://ntfy.sh/DragonBallZ"

# Exact path based on your requirement
# Files will look like: /home/ysj/Desktop/new/Image_20251230_224501.jpg
SAVE_FOLDER = "/home/ysj/Desktop/codes/Image"
FILE_PREFIX = "Image_"

# Create the folder if it does not exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

motion_active = False

def capture_image():
    # Generate timestamped filename starting with Image_
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{FILE_PREFIX}{timestamp}.jpg"
    full_path = os.path.join(SAVE_FOLDER, filename)
    
    print(f"Capturing image to: {full_path}")
    
    try:
        # Capture command
        subprocess.run([
            "rpicam-still",
            "-o", full_path,
            "--width", "640",
            "--height", "480",
            "--quality", "50",
            "--nopreview"
        ], check=True)
        return full_path
    except Exception as e:
        print(f"Camera Error: {e}")
        return None

def send_notification(image_path):
    print("==============================")
    print("Sending ntfy notification...")
    print("==============================")
    try:
        # Send the specific file to ntfy
        subprocess.run([
            "curl",
            "-H", "Title: Raspberry Pi Motion Alert",
            "-H", "Priority: high",
            "-T", image_path,
            NTFY_TOPIC
        ], check=True)
    except Exception as e:
        print(f"Notification Error: {e}")

# Attempt Bluetooth Connection
try:
    ser = serial.Serial(BT_PORT, BAUD, timeout=1)
    if ser.is_open:
        print("Connected to the bluetooth")
        print("==============================")

except Exception as e:
    print(f"Could not connect to bluetooth: {e}")
    print("==============================")
    exit()

print("Listening for motion events...")
print("==============================")
# print("==============================")
while True:
    try:
        # Read and clean serial data
        raw_data = ser.readline().decode(errors="ignore").strip().upper()
        if not raw_data:
            continue

        print(f"Received (raw): {raw_data}")

        # Handling corrupted strings (searching for fragments of 'STARTED')
        if not motion_active and any(fragment in raw_data for fragment in ["STARTED", "OINSA", "OINT"]):
            if not motion_active:
                motion_active = True
                print("==============================")
                print("Motion trigger detected")
                print("==============================")
                saved_file = capture_image()
                if saved_file:
                    send_notification(saved_file)
                    print("==============================")
                    print("Image saved and notification sent")
                    print("==============================")

        # Handling corrupted strings (searching for fragments of 'ENDED')
        elif any(fragment in raw_data for fragment in ["ENDED", "MTO_NE", "OINE"]):
            if motion_active:
                motion_active = False
                print("==============================")
                print("Motion ended - system re-armed")
                print("==============================")

    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
