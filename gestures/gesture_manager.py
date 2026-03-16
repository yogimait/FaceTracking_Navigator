# gestures/gesture_manager.py

import time
import pyautogui

from gestures.click_gesture import ClickGesture
from gestures.scroll_gesture import ScrollGesture
from core.utils import distance


class GestureManager:

    def __init__(self):

        self.last_right_click = 0

        self.left_click = ClickGesture()
        self.scroll = ScrollGesture()

    def process(self, hand_landmarks, mouse):
        # Hand-based left/right clicks have been removed to prevent 
        # accidental clicks messing up the scroll gesture. 
        # Hover/Cursor is controlled by face tracking.
        # Clicking is controlled by blink detection.
        # Scrolling is controlled by static hand gestures here.
        
        self.scroll.detect(hand_landmarks)