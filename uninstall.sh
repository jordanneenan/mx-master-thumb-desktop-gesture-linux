#!/bin/bash
# MX Master Linux Gesture Driver - Uninstaller

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./uninstall.sh)"
  exit 1
fi

echo "Stopping and disabling service..."
systemctl disable --now mx-master-gesture

echo "Removing files..."
rm -f /usr/local/bin/mx_master_gesture_daemon.py
rm -f /etc/systemd/system/mx-master-gesture.service

systemctl daemon-reload

echo "Uninstallation complete."
