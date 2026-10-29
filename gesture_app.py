#!/usr/bin/env python3
"""
gesture_app.py
Mac Hand Gesture Controller
Control your Mac with hand gestures using your built-in webcam.
Inspired by the viral reel: "No mouse. No trackpad. Just vibes 🖐️✨"
"""

import sys
import os
import time
import math
import numpy as np
import cv2

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hand_tracking import HandDetector
from mac_controller import MacController


class GestureApp:
    def __init__(self, camera_idx=0, width=1280, height=720):
        self.cam_width = width
        self.cam_height = height
        self.camera_idx = camera_idx

        # Detection zone margins (so you can reach screen corners easily)
        self.margin_x = 140
        self.margin_y = 100

        # Smoothing factor (higher = smoother, lower = more instant)
        self.smooth_factor = 4.0
        self.prev_x, self.prev_y = 0.0, 0.0
        self.curr_x, self.curr_y = 0.0, 0.0

        # Scroll tracking
        self.prev_scroll_y = None
        self.scroll_threshold = 12

        # Drag state
        self.drag_active = False

        # Mode and UI
        self.mode = "READY"
        self.show_help = True
        self.mirror_mode = True

        # FPS calculation
        self.prev_time = time.time()
        self.fps = 0

        # Initialize detector and controller
        print("Initializing MediaPipe Hand Tracking...")
        self.detector = HandDetector(max_hands=1, detection_con=0.75, track_con=0.75)
        print("Initializing macOS Native CoreGraphics Controller...")
        self.controller = MacController()
        self.screen_w, self.screen_h = self.controller.get_screen_size()
        print(f"Detected Display Resolution: {self.screen_w} x {self.screen_h}")

    def run(self):
        cap = cv2.VideoCapture(self.camera_idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)

        if not cap.isOpened():
            print(f"Error: Unable to open webcam at index {self.camera_idx}.")
            print("Please ensure Terminal has Camera permission in macOS System Settings > Privacy & Security > Camera.")
            return

        print("\n=== Gesture Controller Running ===")
        print("🖐️  Index finger up: Move cursor")
        print("👌  Pinch Index + Thumb: Left Click")
        print("✌️   Index + Middle up: Scroll up / down")
        print("🤙  Thumb + Pinky: Volume control")
        print("✊  Closed Fist: Drag and drop")
        print("🖐️  All 5 fingers wide: Mission Control")
        print("⌨️   Press 'Q' to quit | 'H' for help | 'M' to toggle mirror\n")

        cv2.namedWindow("Mac Gesture Control - Live Feed", cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow("Mac Gesture Control - Live Feed", 960, 540)

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    print("Waiting for camera feed...")
                    time.sleep(0.1)
                    continue

                if self.mirror_mode:
                    frame = cv2.flip(frame, 1)

                h, w, c = frame.shape

                # Calculate FPS
                curr_time = time.time()
                dt = curr_time - self.prev_time
                self.fps = int(1.0 / dt) if dt > 0 else 30
                self.prev_time = curr_time

                # Detect hands & draw neon skeleton
                frame = self.detector.find_hands(frame, draw=True)
                lm_list = self.detector.find_position(frame)

                # Draw interactive tracking boundary zone
                cv2.rectangle(
                    frame,
                    (self.margin_x, self.margin_y),
                    (w - self.margin_x, h - self.margin_y),
                    (60, 60, 60),
                    1,
                    cv2.LINE_AA
                )

                if len(lm_list) >= 21:
                    # Index fingertip (8), Thumb tip (4), Middle tip (12), Pinky tip (20)
                    x1, y1 = lm_list[8][1], lm_list[8][2]
                    x2, y2 = lm_list[4][1], lm_list[4][2]
                    x3, y3 = lm_list[12][1], lm_list[12][2]
                    x5, y5 = lm_list[20][1], lm_list[20][2]

                    fingers = self.detector.fingers_up(lm_list)
                    # fingers: [Thumb, Index, Middle, Ring, Pinky]

                    # 1. Closed Fist -> DRAG & DROP
                    if not any(fingers[1:]):  # Index, Middle, Ring, Pinky are all down
                        self.mode = "DRAG"
                        if not self.drag_active:
                            self.controller.start_drag()
                            self.drag_active = True
                        cv2.circle(frame, (x1, y1), 16, (0, 0, 255), cv2.FILLED)

                    # Release drag if not in drag mode
                    elif self.drag_active:
                        self.controller.stop_drag()
                        self.drag_active = False

                    # 2. Left Click Gesture -> Pinch Index + Thumb
                    dist_click, click_mid, _ = self.detector.find_distance(4, 8, lm_list, draw=False)
                    dist_right_click, rclick_mid, _ = self.detector.find_distance(4, 12, lm_list, draw=False)

                    if dist_click < 38 and fingers[1]:
                        self.mode = "CLICK"
                        clicked = self.controller.left_click()
                        cv2.circle(frame, click_mid, 18, (0, 255, 255), cv2.FILLED)
                        cv2.circle(frame, click_mid, 24, (255, 255, 0), 2)

                    # 3. Right Click Gesture -> Pinch Middle + Thumb
                    elif dist_right_click < 38 and fingers[2]:
                        self.mode = "RIGHT CLICK"
                        self.controller.right_click()
                        cv2.circle(frame, rclick_mid, 18, (255, 0, 255), cv2.FILLED)

                    # 4. Scroll Mode -> Index + Middle fingers UP (peace sign)
                    elif fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
                        self.mode = "SCROLL"
                        avg_y = (y1 + y3) // 2
                        cv2.circle(frame, ((x1 + x3) // 2, avg_y), 12, (255, 200, 0), cv2.FILLED)

                        if self.prev_scroll_y is not None:
                            diff_y = self.prev_scroll_y - avg_y
                            if abs(diff_y) > self.scroll_threshold:
                                scroll_amount = int(diff_y / 4.0)
                                self.controller.scroll(scroll_amount)
                                self.prev_scroll_y = avg_y
                        else:
                            self.prev_scroll_y = avg_y

                    # 5. Volume Control -> Shaka sign (Thumb + Pinky open, other 3 down)
                    elif fingers[0] and fingers[4] and not fingers[1] and not fingers[2] and not fingers[3]:
                        self.mode = "VOLUME"
                        vol_dist = math.hypot(x5 - x2, y5 - y2)
                        # Hand moving up/down adjusts volume
                        if y2 < h * 0.4:
                            self.controller.adjust_volume(+2)
                            cv2.putText(frame, "VOL +", (w - 180, 100), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 0), 2)
                        elif y2 > h * 0.6:
                            self.controller.adjust_volume(-2)
                            cv2.putText(frame, "VOL -", (w - 180, 100), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 2)

                    # 6. Mission Control -> All 5 fingers extended wide
                    elif all(fingers):
                        self.mode = "MISSION CONTROL"
                        # Quick gesture check: hand in top third
                        if y1 < h * 0.3:
                            self.controller.mission_control()
                            time.sleep(0.4)

                    # 7. Cursor Movement Mode -> Index finger UP
                    elif fingers[1] and not fingers[2]:
                        self.mode = "MOVE"
                        self.prev_scroll_y = None

                        # Map camera coordinates to full screen resolution
                        target_x = np.interp(x1, (self.margin_x, w - self.margin_x), (0, self.screen_w))
                        target_y = np.interp(y1, (self.margin_y, h - self.margin_y), (0, self.screen_h))

                        # Exponential Moving Average Smoothing
                        self.curr_x = self.prev_x + (target_x - self.prev_x) / self.smooth_factor
                        self.curr_y = self.prev_y + (target_y - self.prev_y) / self.smooth_factor

                        self.controller.move_to(self.curr_x, self.curr_y)
                        self.prev_x, self.prev_y = self.curr_x, self.curr_y

                        # Draw pointer target reticle
                        cv2.circle(frame, (x1, y1), 10, (0, 255, 80), 2)
                        cv2.circle(frame, (x1, y1), 4, (0, 255, 255), cv2.FILLED)

                    else:
                        self.mode = "STANDBY"
                        self.prev_scroll_y = None

                else:
                    self.mode = "NO HAND"
                    self.prev_scroll_y = None
                    if self.drag_active:
                        self.controller.stop_drag()
                        self.drag_active = False

                # Render Top-Left HUD (Matching exact reel layout: "move  29 fps")
                self._draw_hud(frame, w, h)

                # Show frame
                cv2.imshow("Mac Gesture Control - Live Feed", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Q or ESC to quit
                    break
                elif key == ord('h'):
                    self.show_help = not self.show_help
                elif key == ord('m'):
                    self.mirror_mode = not self.mirror_mode

        finally:
            if self.drag_active:
                self.controller.stop_drag()
            cap.release()
            cv2.destroyAllWindows()
            print("Session ended cleanly.")

    def _draw_hud(self, frame, w, h):
        """Draws aesthetic cyberpunk HUD overlay."""
        # Top-left status badge: e.g. "move  29 fps"
        badge_text = f"{self.mode.lower()}   {self.fps} fps"
        text_size = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_DUPLEX, 0.75, 2)[0]

        # Dark glass background pill
        pad_x, pad_y = 16, 12
        rx, ry = 25, 25
        rw, rh = text_size[0] + pad_x * 2, text_size[1] + pad_y * 2

        overlay = frame.copy()
        cv2.rectangle(overlay, (rx, ry), (rx + rw, ry + rh), (15, 15, 15), cv2.FILLED)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        # Mode glow color
        mode_color = (0, 255, 80) if self.mode == "MOVE" else (
            (0, 255, 255) if self.mode == "CLICK" else (
                (255, 200, 0) if self.mode == "SCROLL" else (
                    (0, 0, 255) if self.mode == "DRAG" else (200, 200, 200)
                )
            )
        )

        cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), mode_color, 1, cv2.LINE_AA)
        cv2.putText(
            frame,
            badge_text,
            (rx + pad_x, ry + rh - pad_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.75,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # Top banner inspired by reel
        reel_text = "No mouse. No trackpad. Just vibes"
        rt_size = cv2.getTextSize(reel_text, cv2.FONT_HERSHEY_DUPLEX, 0.65, 1)[0]
        banner_x = (w - rt_size[0]) // 2
        cv2.putText(frame, reel_text, (banner_x, 35), cv2.FONT_HERSHEY_DUPLEX, 0.65, (240, 240, 240), 1, cv2.LINE_AA)

        # Optional bottom help legend
        if self.show_help:
            legend = "Index: Move | Pinch: Click | 2-Fingers: Scroll | Fist: Drag | Q: Quit"
            l_size = cv2.getTextSize(legend, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
            cv2.putText(frame, legend, ((w - l_size[0]) // 2, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)


if __name__ == "__main__":
    app = GestureApp()
    app.run()
