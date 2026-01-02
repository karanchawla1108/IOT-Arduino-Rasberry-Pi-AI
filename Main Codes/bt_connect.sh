#!/bin/bash

MAC="20:25:05:00:B1:3B"

echo "Connecting to HC-05..."
sudo rfcomm release 0 >/dev/null 2>&1
sudo rfcomm bind 0 $MAC

sleep 2

if [ -e /dev/rfcomm0 ]; then
    echo "Bluetooth serial connected at /dev/rfcomm0"
else
    echo "Failed to create rfcomm0"
fi