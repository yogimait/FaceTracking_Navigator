# gestures/scroll_gesture.py

import pyautogui
import time

pyautogui.PAUSE = 0


class ScrollGesture:

    def __init__(self):
        self.last_scroll = 0
        self.scroll_speed = 35

    def detect(self, hand_landmarks):
        current_time = time.time()
        
        wrist = hand_landmarks.landmark[0]

        def get_dist(lm1, lm2):
            return ((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)**0.5

        # Helper to check if a finger is folded into the palm
        def is_folded(tip_idx, pip_idx):
            return get_dist(hand_landmarks.landmark[tip_idx], wrist) < get_dist(hand_landmarks.landmark[pip_idx], wrist)

        # Scroll gestures are only intended when ring and pinky are folded out of the way
        if not is_folded(16, 14) or not is_folded(20, 18):
            return

        # Check if Index and Middle fingers are EXTENDED (Image 2 - Straight Up)
        # or CURLED (Image 1 - Hooked/Pinched shape)
        
        idx_tip = hand_landmarks.landmark[8]
        idx_pip = hand_landmarks.landmark[6]
        mid_tip = hand_landmarks.landmark[12]
        mid_pip = hand_landmarks.landmark[10]

        # In an extended finger, the tip is further from the wrist than the PIP joint
        idx_extended = get_dist(idx_tip, wrist) > get_dist(idx_pip, wrist) + 0.02
        mid_extended = get_dist(mid_tip, wrist) > get_dist(mid_pip, wrist) + 0.02

        # In a completely curled/hooked finger, the tip folds inward and is closer to the wrist than PIP
        idx_curled = get_dist(idx_tip, wrist) < get_dist(idx_pip, wrist)
        mid_curled = get_dist(mid_tip, wrist) < get_dist(mid_pip, wrist)

        if idx_extended and mid_extended:
            # Gesture 2: Fingers straight -> Scroll UP
            if current_time - self.last_scroll > 0.05:
                pyautogui.scroll(self.scroll_speed)
                self.last_scroll = current_time

        elif idx_curled and mid_curled:
            # Gesture 1: Fingers curled -> Scroll DOWN
            if current_time - self.last_scroll > 0.05:
                pyautogui.scroll(-self.scroll_speed)
                self.last_scroll = current_time