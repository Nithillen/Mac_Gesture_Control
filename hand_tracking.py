"""
hand_tracking.py
Real-time hand detection, landmark extraction, and gesture recognition
powered by Google MediaPipe Tasks API and OpenCV.
Optimized for Apple Silicon Neural Engine / Metal GPU acceleration.
"""

import os
import sys
import math
import time
import urllib.request
import numpy as np
import cv2

# Set writable directory for matplotlib cache to avoid warnings
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import HandLandmarksConnections

MODEL_FILENAME = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


class HandDetector:
    def __init__(self, model_path=None, max_hands=1, detection_con=0.7, track_con=0.7):
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # Resolve model path
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(base_dir, MODEL_FILENAME)
        else:
            self.model_path = model_path

        # Auto-download model if missing
        if not os.path.exists(self.model_path):
            print(f"Downloading MediaPipe model to {self.model_path}...")
            urllib.request.urlretrieve(MODEL_URL, self.model_path)
            print("Model download complete.")

        # Initialize MediaPipe HandLandmarker
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

        # Neon color palette matching the viral reel
        self.neon_green = (0, 255, 80)
        self.neon_cyan = (255, 255, 0)
        self.neon_yellow = (0, 220, 255)
        self.neon_magenta = (255, 0, 255)

        self.connections = HandLandmarksConnections.HAND_CONNECTIONS
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None

    def find_hands(self, img, draw=True):
        """Processes frame through MediaPipe and draws neon skeleton lines and nodes."""
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.results = self.detector.detect(mp_image)

        if self.results.hand_landmarks and draw:
            h, w, _ = img.shape
            for hand_lms in self.results.hand_landmarks:
                # 1. Draw glowing neon skeleton lines
                for conn in self.connections:
                    lm1 = hand_lms[conn.start]
                    lm2 = hand_lms[conn.end]
                    cx1, cy1 = int(lm1.x * w), int(lm1.y * h)
                    cx2, cy2 = int(lm2.x * w), int(lm2.y * h)
                    # Glowing effect: thicker base + bright neon core
                    cv2.line(img, (cx1, cy1), (cx2, cy2), (0, 180, 40), 3, cv2.LINE_AA)
                    cv2.line(img, (cx1, cy1), (cx2, cy2), self.neon_green, 2, cv2.LINE_AA)

                # 2. Draw landmark joints
                for idx, lm in enumerate(hand_lms):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if idx in self.tip_ids:
                        # Highlight fingertip halos
                        cv2.circle(img, (cx, cy), 8, self.neon_yellow, 2, cv2.LINE_AA)
                        cv2.circle(img, (cx, cy), 4, self.neon_green, cv2.FILLED, cv2.LINE_AA)
                    else:
                        cv2.circle(img, (cx, cy), 4, self.neon_green, cv2.FILLED, cv2.LINE_AA)

        return img

    def find_position(self, img, hand_no=0):
        """Returns list of all 21 landmark positions in pixel coordinates [id, cx, cy, x_norm, y_norm]."""
        lm_list = []
        if self.results and self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                my_hand = self.results.hand_landmarks[hand_no]
                h, w, _ = img.shape
                for idx, lm in enumerate(my_hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([idx, cx, cy, lm.x, lm.y])
        return lm_list

    def fingers_up(self, lm_list):
        """
        Detects which fingers are extended (open).
        Returns list of 5 booleans [Thumb, Index, Middle, Ring, Pinky].
        """
        if len(lm_list) < 21:
            return [False, False, False, False, False]

        fingers = []

        # Thumb: compare tip (4) with MCP/IP joints relative to pinky base (17)
        thumb_tip_dist = math.hypot(lm_list[4][1] - lm_list[17][1], lm_list[4][2] - lm_list[17][2])
        thumb_ip_dist = math.hypot(lm_list[3][1] - lm_list[17][1], lm_list[3][2] - lm_list[17][2])
        fingers.append(thumb_tip_dist > thumb_ip_dist * 1.15)

        # 4 Fingers: Tip Y must be above (smaller value in screen coords) PIP joint (tip_id - 2)
        for tip_id in [8, 12, 16, 20]:
            if lm_list[tip_id][2] < lm_list[tip_id - 2][2]:
                fingers.append(True)
            else:
                fingers.append(False)

        return fingers

    def find_distance(self, p1, p2, lm_list, img=None, draw=True):
        """Calculates distance between two landmarks p1 and p2."""
        if len(lm_list) < max(p1, p2) + 1:
            return 999, (0, 0), img

        x1, y1 = lm_list[p1][1], lm_list[p1][2]
        x2, y2 = lm_list[p2][1], lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)

        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), self.neon_cyan, 2, cv2.LINE_AA)
            cv2.circle(img, (x1, y1), 6, self.neon_yellow, cv2.FILLED, cv2.LINE_AA)
            cv2.circle(img, (x2, y2), 6, self.neon_yellow, cv2.FILLED, cv2.LINE_AA)
            cv2.circle(img, (cx, cy), 6, self.neon_cyan, cv2.FILLED, cv2.LINE_AA)

        return length, (cx, cy), img
