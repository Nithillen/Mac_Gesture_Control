# Mac Gesture Control

Control macOS cursor movement, clicks, scrolling, and system shortcuts using your webcam and hand gestures. 

Built using Google MediaPipe for hand landmark detection and Apple's native CoreGraphics (`CGEvent`) API via `ctypes` for low-latency cursor tracking without third-party mouse drivers.

---

## Gestures

| Gesture | Action | Notes |
|---|---|---|
| **Index finger up** | Move Cursor | Moves cursor across display with smoothing |
| **Index + Thumb pinch** | Left Click | Pinch and release to click |
| **Middle + Thumb pinch** | Right Click | Opens context menu |
| **Index + Middle fingers up** | Scroll | Peace sign; move hand up/down to scroll |
| **Closed fist** | Drag & Drop | Clench fist to hold click, open hand to release |
| **Thumb + Pinky extended** | Volume Control | Move hand up to raise volume, down to lower |
| **Open hand (all fingers up)** | Mission Control | Move hand upward into top third of frame |

---

## Requirements

- macOS 12+ (Apple Silicon or Intel)
- Python 3.9+
- Built-in FaceTime HD camera or external webcam

---

## Setup & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nithillen/Mac_Gesture_Control.git
   cd Mac_Gesture_Control
   ```

2. **Run the start script:**
   ```bash
   ./run.sh
   ```
   *The script sets up a local virtual environment, installs dependencies (`opencv-python`, `mediapipe`, `numpy`), and starts the app.*

Alternatively, install and run manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python gesture_app.py
```

---

## macOS Permissions

The application requires two permissions in macOS:

1. **Camera**: Prompted automatically on first launch.
2. **Accessibility**: Required by macOS to allow `CGEvent` to control the cursor.
   - Go to **System Settings > Privacy & Security > Accessibility**.
   - Enable your terminal application (e.g. `Terminal`, `iTerm2`, or `VS Code`).
   - If not enabled, `check_permissions.py` will prompt and open this settings window for you.

---

## In-App Controls

- **Q** or **ESC**: Quit
- **H**: Toggle help overlay
- **M**: Toggle camera mirror mode
