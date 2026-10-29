#!/usr/bin/env bash
# run.sh - Quick launcher for Mac Gesture Control
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🖐️  Mac Hand Gesture Controller (Vibes Edition)"
echo "   'No mouse. No trackpad. Just vibes 🖐️✨'"
echo "=========================================================="

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install opencv-python mediapipe numpy
fi

# Check permissions
echo "Checking macOS permissions..."
"$DIR/venv/bin/python" "$DIR/check_permissions.py" || true

echo "Starting Gesture Controller..."
echo "Press 'Q' inside the camera feed window to quit."
echo "=========================================================="

"$DIR/venv/bin/python" "$DIR/gesture_app.py"
