import time
from core.utils import distance
import config


class ClickGesture:

    def __init__(self):

        self.last_click_time = 0

    def detect(self, hand_landmarks):

        thumb = hand_landmarks.landmark[4]
        index = hand_landmarks.landmark[8]

        dist = distance(thumb, index)

        if dist < config.CLICK_THRESHOLD:

            current_time = time.time()

            if current_time - self.last_click_time > config.CLICK_COOLDOWN:

                self.last_click_time = current_time
                return True

        return False