# Mac Hand Gesture Controller 🖐️✨

> *"No mouse. No trackpad. Just vibes 🖐️✨"*  
> Inspired by the viral Instagram Reel showing mid-air hand gesture control for MacBook using AI computer vision.

![Mac Gesture Control](https://img.shields.io/badge/Platform-macOS-black?style=flat&logo=apple)
![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00c853?style=flat)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=flat&logo=opencv)

Control your entire Mac without touching your mouse, keyboard, or trackpad. Using your built-in FaceTime / MacBook webcam, real-time hand tracking tracks 21 skeletal landmarks to move your cursor, click, drag, scroll, and adjust system volume through mid-air gestures.

---

## ✨ Features

- **Blazing Fast Native macOS Control:** Driven directly by Apple's `CoreGraphics` / `ApplicationServices` via C-types (60–120 FPS ProMotion cursor tracking without heavy bloatware).
- **Jitter-Free Exponential Moving Average (EMA):** Smooths out human micro-tremors for pinpoint cursor precision.
- **Neon Cyberpunk HUD:** Real-time visual overlay displaying hand skeleton nodes, active mode badges (`move 29 fps`, `click`, `scroll`), and detection zones.
- **Zero Mouse/Trackpad Needed:** Full control of clicks, right-clicks, scrolling, dragging, volume, and Mission Control.

---

## 🖐️ Gesture Cheat Sheet

| Gesture | Action | Description |
| :--- | :--- | :--- |
| ☝️ **Index Finger Up** | **Move Cursor** | Point and move your index finger in the camera frame to control the cursor. |
| 👌 **Index + Thumb Pinch** | **Left Click** | Pinch your index fingertip and thumb tip together to click. |
| 🤏 **Middle + Thumb Pinch** | **Right Click** | Pinch your middle fingertip and thumb tip together to open context menus. |
| ✌️ **Index + Middle Up** | **Smooth Scroll** | Keep both fingers up like a peace sign; move your hand up/down to scroll. |
| ✊ **Closed Fist** | **Drag & Drop** | Make a fist to grab and drag windows/files. Open hand to drop. |
| 🤙 **Shaka Sign** *(Thumb + Pinky)* | **Volume Control** | Move hand up to raise volume, move down to lower volume. |
| 🖐️ **5 Fingers Open Wide** | **Mission Control** | Raise all five fingers up to open macOS Mission Control. |

---

## 🚀 Quick Start

### 1. Requirements
- macOS (Apple Silicon M1/M2/M3/M4 or Intel)
- Python 3.9+
- Built-in FaceTime HD camera or external webcam

### 2. Run with One Command
Clone and run the launcher script:

```bash
git clone https://github.com/Nithillen/mac-gesture-control.git
cd mac-gesture-control
./run.sh
```

The script will automatically set up the virtual environment, install dependencies, verify macOS permissions, and launch the application.

---

## 🔐 macOS Permissions Setup

For security, macOS requires two permissions:
1. **Camera Permission:** macOS will prompt you when the camera activates. Click **Allow**.
2. **Accessibility Permission (for cursor control):**
   - Go to **System Settings > Privacy & Security > Accessibility**.
   - Ensure your terminal (e.g. `Terminal`, `iTerm2`, or `VS Code`) is toggled **ON**.
   - If not already enabled, `run.sh` will automatically open the settings window for you.

---

## ⌨️ Keyboard Shortcuts (Inside App)

- `Q` or `ESC`: Quit application
- `H`: Toggle bottom help legend
- `M`: Toggle camera mirror mode
