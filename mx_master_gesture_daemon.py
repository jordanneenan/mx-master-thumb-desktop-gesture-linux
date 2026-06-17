#!/usr/bin/env python3
import evdev
import time
import select
from evdev import UInput, AbsInfo, ecodes as e

# Configurable Settings
# ---------------------
PIXELS_PER_TICK = -280  # Lowered so it doesn't fly past 2 desktops on a fast flick
SCROLL_TIMEOUT = 0.045  # 45ms timeout. The "Goldilocks" zone: long enough to link slow rolls together, short enough to preserve momentum when you stop.

# 1. Find the Logitech MX Master 3 device
target_name = "Logitech MX Master 3 for Mac"
device = None

for path in evdev.list_devices():
    dev = evdev.InputDevice(path)
    if dev.name == target_name and e.EV_REL in dev.capabilities():
        caps = dev.capabilities()[e.EV_REL]
        if e.REL_HWHEEL in caps or e.REL_HWHEEL_HI_RES in caps:
            device = dev
            break

if not device:
    print(f"Error: Could not find '{target_name}' with HWHEEL capabilities.")
    exit(1)

print(f"Listening to device: {device.path} ({device.name})")

# 2. Define the capabilities of our Virtual Trackpad
capabilities = {
    e.EV_KEY: [e.BTN_TOUCH, e.BTN_TOOL_DOUBLETAP, e.BTN_TOOL_TRIPLETAP],
    e.EV_ABS: [
        # Trackpad size: 20,000 units (enough for ~5 workspaces in a continuous roll)
        (e.ABS_X, AbsInfo(value=0, min=0, max=20000, fuzz=0, flat=0, resolution=40)),
        (e.ABS_Y, AbsInfo(value=0, min=0, max=20000, fuzz=0, flat=0, resolution=40)),
        (e.ABS_MT_POSITION_X, AbsInfo(value=0, min=0, max=20000, fuzz=0, flat=0, resolution=40)),
        (e.ABS_MT_POSITION_Y, AbsInfo(value=0, min=0, max=20000, fuzz=0, flat=0, resolution=40)),
        (e.ABS_MT_SLOT, AbsInfo(value=0, min=0, max=4, fuzz=0, flat=0, resolution=0)),
        (e.ABS_MT_TRACKING_ID, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
        (e.ABS_MT_TOOL_TYPE, AbsInfo(value=0, min=0, max=2, fuzz=0, flat=0, resolution=0)),
    ]
}

# 3. Create the Virtual Device
ui = UInput(
    events=capabilities, 
    name="Virtual Gesture Trackpad", 
    version=0x3,
    input_props=[e.INPUT_PROP_POINTER, e.INPUT_PROP_BUTTONPAD]
)

# State Management
x_pos = 10000.0
y_pos = 10000.0
tracking_id_start = 1
fingers_down = False
last_scroll_time = 0

def press_fingers():
    global fingers_down, tracking_id_start
    if fingers_down:
        return
    ui.write(e.EV_KEY, e.BTN_TOUCH, 1)
    ui.write(e.EV_KEY, e.BTN_TOOL_TRIPLETAP, 1)
    for slot in range(3):
        ui.write(e.EV_ABS, e.ABS_MT_SLOT, slot)
        ui.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, tracking_id_start + slot)
        ui.write(e.EV_ABS, e.ABS_MT_POSITION_X, int(x_pos))
        ui.write(e.EV_ABS, e.ABS_MT_POSITION_Y, int(y_pos))
    ui.syn()
    fingers_down = True
    tracking_id_start += 3
    if tracking_id_start > 10000:
        tracking_id_start = 1

def release_fingers():
    global fingers_down
    if not fingers_down:
        return
    ui.write(e.EV_KEY, e.BTN_TOUCH, 0)
    ui.write(e.EV_KEY, e.BTN_TOOL_TRIPLETAP, 0)
    for slot in range(3):
        ui.write(e.EV_ABS, e.ABS_MT_SLOT, slot)
        ui.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, -1)
    ui.syn()
    fingers_down = False

def update_fingers(delta_x):
    global x_pos
    x_pos += delta_x
    # Clamp
    x_pos = max(0.0, min(x_pos, 20000.0))
    for slot in range(3):
        ui.write(e.EV_ABS, e.ABS_MT_SLOT, slot)
        ui.write(e.EV_ABS, e.ABS_MT_POSITION_X, int(x_pos))
        if slot == 0:
            ui.write(e.EV_ABS, e.ABS_X, int(x_pos))
            ui.write(e.EV_ABS, e.ABS_Y, int(y_pos))
    ui.syn()

try:
    while True:
        r, w, x = select.select([device], [], [], 0.01)
        
        if r:
            for event in device.read():
                if event.type == e.EV_REL and (event.code == e.REL_HWHEEL or event.code == e.REL_HWHEEL_HI_RES):
                    last_scroll_time = time.time()
                    val = event.value
                    if event.code == e.REL_HWHEEL_HI_RES:
                        val = val / 120.0
                    
                    delta = val * PIXELS_PER_TICK
                    press_fingers()
                    update_fingers(delta)
        else:
            # If 30ms pass without a scroll tick, instantly release fingers to trigger GNOME's native momentum/snap
            if fingers_down and (time.time() - last_scroll_time) > SCROLL_TIMEOUT:
                release_fingers()
                x_pos = 10000.0

except KeyboardInterrupt:
    release_fingers()
    ui.close()
    device.close()
    print("\nExiting.")
