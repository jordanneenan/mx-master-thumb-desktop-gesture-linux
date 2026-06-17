# MX Master Gesture Driver for Linux

A lightweight python daemon that intercepts the horizontal thumb wheel on the Logitech MX Master 3 and translates it into smooth, 1-to-1 native multi-touch trackpad swipe gestures on Linux (Wayland/X11).

This brings the buttery smooth, momentum-based workspace switching experience found on Mac OS straight to your Linux desktop.

## Why this exists
Standard mouse tools like `logiops` (`logid`) map the thumb wheel to discrete keyboard shortcuts (like `Ctrl+Alt+Right`). A keyboard press is binary, meaning your desktop environment plays the entire workspace switching animation at a fixed speed, resulting in jerky, uncontrollable skipping. 

This driver works around that by creating a virtual kernel trackpad (`uinput`) and spoofing a 3-finger swipe gesture, tricking GNOME into using its native trackpad physics engine.

## Prerequisites
- Linux (Works on Ubuntu, Fedora, Arch, etc. Tested on Wayland with GNOME/KDE)
- `python3-evdev`
- A Logitech MX Master 3 (or similar mouse with an independent horizontal scroll wheel)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/mx-master-thumb-desktop-gesture-linux.git
   cd mx-master-thumb-desktop-gesture-linux
   ```
2. Run the install script as root:
   ```bash
   sudo ./install.sh
   ```

*(Note: The `install.sh` script currently uses `apt-get` for Ubuntu/Debian. If you are on Fedora or Arch, you may need to install `python3-evdev` manually via `dnf` or `pacman` first).*

The script will automatically install the python dependencies, copy the daemon to `/usr/local/bin`, and enable the background `systemd` service.

## Tuning the Sensitivity & Momentum
You can easily adjust the "feel" of the scrolling.
1. Open `/usr/local/bin/mx_master_gesture_daemon.py`
2. At the top of the file, modify the configurable settings:
   - `PIXELS_PER_TICK`: Increase absolute value (e.g. `-350` to `-450`) to move further per roll. Flip the sign to invert the scroll direction.
   - `SCROLL_TIMEOUT`: Controls the momentum. A shorter timeout (e.g., `0.02s`) guarantees that the virtual fingers lift while moving fast, triggering GNOME's native "flick" momentum. A slightly longer timeout (e.g., `0.045s`) helps bridge the gap between slow ratchet clicks.
3. Restart the service to apply changes:
   ```bash
   sudo systemctl restart mx-master-gesture
   ```

## Uninstallation
Run the uninstaller script as root:
```bash
sudo ./uninstall.sh
```
