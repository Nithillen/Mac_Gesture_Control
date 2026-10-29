"""
hand_tracking.py
Real-time hand detection, landmark extraction, and gesture recognition
powered by MediaPipe Hands and OpenCV.
"""

import math
import time
import numpy as np
import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, mode=False, max_hands=1, detection_con=0.75, track_con=0.75):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Custom high-tech neon drawing style matching the Instagram reel
        self.neon_green = (0, 255, 80)
        self.neon_cyan = (255, 255, 0)
        self.neon_yellow = (0, 220, 255)
        self.neon_magenta = (255, 0, 255)

        self.results = None
        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, img, draw=True):
        """Processes frame through MediaPipe and optionally draws neon skeleton."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                h, w, c = img.shape

                # Draw custom neon green skeleton lines
                connections = self.mp_hands.HAND_CONNECTIONS
                for conn in connections:
                    pt1_idx, pt2_idx = conn
                    lm1 = hand_lms.landmark[pt1_idx]
                    lm2 = hand_lms.landmark[pt2_idx]
                    cx1, cy1 = int(lm1.x * w), int(lm1.y * h)
                    cx2, cy2 = int(lm2.x * w), int(lm2.y * h)
                    # Glowing line effect (thicker dark green base + thinner bright neon core)
                    cv2.line(img, (cx1, cy1), (cx2, cy2), (0, 180, 40), 3)
                    cv2.line(img, (cx1, cy1), (cx2, cy2), self.neon_green, 2)

                # Draw landmark joint nodes
                for idx, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if idx in self.tip_ids:
                        # Highlight fingertips with larger halo circles
                        cv2.circle(img, (cx, cy), 8, self.neon_yellow, 2)
                        cv2.circle(img, (cx, cy), 4, self.neon_green, cv2.FILLED)
                    else:
                        cv2.circle(img, (cx, cy), 4, self.neon_green, cv2.FILLED)

        return img

    def find_position(self, img, hand_no=0):
        """Returns list of all 21 landmark positions in pixel coordinates [id, cx, cy]."""
        lm_list = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, c = img.shape
                for idx, lm in enumerate(my_hand.landmark):
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

        # Thumb: compare tip (4) with IP joint (3) or MCP (2) based on hand orientation
        # Hand is mirrored, so check horizontal distance from wrist or MCP
        is_right_oriented = lm_list[4][1] > lm_list[3][1]
        # Dist from thumb tip to pinky MCP (17) vs thumb IP (3) to pinky MCP
        thumb_tip_dist = math.hypot(lm_list[4][1] - lm_list[17][1], lm_list[4][2] - lm_list[17][2])
        thumb_ip_dist = math.hypot(lm_list[3][1] - lm_list[17][1], lm_list[3][2] - lm_list[17][2])
        fingers.append(thumb_tip_dist > thumb_ip_dist * 1.15)

        # 4 Fingers: Tip Y must be above (lower value on image coordinate) PIP joint Y
        for tip_id in [8, 12, 16, 20]:
            # Tip vs PIP (tip_id - 2)
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
            cv2.line(img, (x1, y1), (x2, y2), self.neon_cyan, 2)
            cv2.circle(img, (x1, y1), 6, self.neon_yellow, cv2.FILLED)
            cv2.circle(img, (x2, y2), 6, self.neon_yellow, cv2.FILLED)
            cv2.circle(img, (cx, cy), 6, self.neon_cyan, cv2.FILLED)

        return length, (cx, cy), img
