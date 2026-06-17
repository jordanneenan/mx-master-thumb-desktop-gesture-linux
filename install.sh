#!/bin/bash
# MX Master Linux Gesture Driver - Installer

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

echo "Installing python3-evdev dependency..."
apt-get update
apt-get install -y python3-evdev

echo "Installing daemon to /usr/local/bin..."
cp mx_master_gesture_daemon.py /usr/local/bin/
chmod +x /usr/local/bin/mx_master_gesture_daemon.py

echo "Installing systemd service..."
cp mx-master-gesture.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now mx-master-gesture

echo "Installation complete! The gesture daemon is now running in the background."
