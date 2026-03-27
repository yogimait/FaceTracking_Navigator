# gestures/gesture_manager.py

import time
import cv2
import pyautogui

from gestures import click_config
from gestures.scroll_gesture import ScrollGesture
from core.utils import distance


class GestureManager:

    def __init__(self):

        self.scroll = ScrollGesture()

        self.pinch_threshold = click_config.PINCH_THRESHOLD
        self.debounce_frames = click_config.DEBOUNCE_FRAMES
        self.stability_frames = click_config.STABILITY_FRAMES
        self.move_threshold = click_config.MOVE_THRESHOLD
        self.left_click_activation_time = click_config.LEFT_CLICK_ACTIVATION_TIME
        self.right_click_activation_time = click_config.RIGHT_CLICK_ACTIVATION_TIME
        self.double_click_enabled = click_config.DOUBLE_CLICK_ENABLED
        self.double_click_hold = click_config.DOUBLE_CLICK_HOLD
        self.global_cooldown = click_config.GLOBAL_COOLDOWN
        self.feedback_duration = click_config.FEEDBACK_DURATION

        self.last_action_time = 0.0
        self.prev_index_tip = None
        self.stable_frame_count = 0

        self.index_pinch_count = 0
        self.middle_pinch_count = 0

        self.left_pinch_started = False
        self.left_pinch_start_time = 0.0
        self.left_action_fired = False
        self.right_pinch_started = False
        self.right_pinch_start_time = 0.0
        self.gesture_latched = False

        self.feedback_text = ''
        self.feedback_until = 0.0

    def _cooldown_ready(self, current_time):
        return (current_time - self.last_action_time) > self.global_cooldown

    def _set_feedback(self, text, current_time):
        self.feedback_text = text
        self.feedback_until = current_time + self.feedback_duration

    def _reset_left_pinch_state(self):
        self.left_pinch_started = False
        self.left_pinch_start_time = 0.0
        self.left_action_fired = False

    def _reset_right_pinch_state(self):
        self.right_pinch_started = False
        self.right_pinch_start_time = 0.0

    def _trigger(self, action, mouse, current_time):
        if action == 'LEFT CLICK':
            mouse.left_click()
        elif action == 'RIGHT CLICK':
            mouse.right_click()
        elif action == 'DOUBLE CLICK':
            if hasattr(mouse, 'double_click'):
                mouse.double_click()
            else:
                pyautogui.doubleClick()

        self.last_action_time = current_time
        self.gesture_latched = True
        self._set_feedback(action, current_time)

    def _draw_feedback(self, frame, thumb, index, middle, index_pinch, middle_pinch, current_time):
        if frame is None:
            return

        frame_h, frame_w = frame.shape[:2]

        def to_px(lm):
            return int(lm.x * frame_w), int(lm.y * frame_h)

        thumb_px = to_px(thumb)
        index_px = to_px(index)
        middle_px = to_px(middle)

        idle_color = (255, 200, 0)
        index_color = (0, 255, 0) if index_pinch else idle_color
        middle_color = (0, 128, 255) if middle_pinch else idle_color

        cv2.circle(frame, thumb_px, 8, idle_color, -1)
        cv2.circle(frame, index_px, 8, index_color, -1)
        cv2.circle(frame, middle_px, 8, middle_color, -1)

        if current_time < self.feedback_until and self.feedback_text:
            cv2.putText(
                frame,
                self.feedback_text,
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

    def process(self, hand_landmarks, mouse, frame=None):
        self.scroll.detect(hand_landmarks)

        current_time = time.time()

        thumb = hand_landmarks.landmark[4]
        index = hand_landmarks.landmark[8]
        middle = hand_landmarks.landmark[12]

        index_pinch = distance(thumb, index) < self.pinch_threshold
        middle_pinch = distance(thumb, middle) < self.pinch_threshold

        if not index_pinch and not middle_pinch:
            self.gesture_latched = False

        if self.prev_index_tip is None:
            movement = 0.0
        else:
            dx = index.x - self.prev_index_tip[0]
            dy = index.y - self.prev_index_tip[1]
            movement = (dx * dx + dy * dy) ** 0.5

        self.prev_index_tip = (index.x, index.y)

        if movement < self.move_threshold:
            self.stable_frame_count += 1
        else:
            self.stable_frame_count = 0

        click_zone_active = self.stable_frame_count >= self.stability_frames

        if not click_zone_active:
            self.index_pinch_count = 0
            self.middle_pinch_count = 0
            self._reset_left_pinch_state()
            self._reset_right_pinch_state()
            self._draw_feedback(frame, thumb, index, middle, index_pinch, middle_pinch, current_time)
            return

        self.index_pinch_count = self.index_pinch_count + 1 if index_pinch else 0
        self.middle_pinch_count = self.middle_pinch_count + 1 if middle_pinch else 0

        right_pinch_valid = self.middle_pinch_count >= self.debounce_frames
        left_pinch_valid = self.index_pinch_count >= self.debounce_frames
        cooldown_ready = self._cooldown_ready(current_time)

        if right_pinch_valid and not self.gesture_latched:
            if not self.right_pinch_started:
                self.right_pinch_started = True
                self.right_pinch_start_time = current_time
            right_hold_time = current_time - self.right_pinch_start_time
            if cooldown_ready and right_hold_time >= self.right_click_activation_time:
                self._trigger('RIGHT CLICK', mouse, current_time)
                self._reset_left_pinch_state()
                self._reset_right_pinch_state()
                self._draw_feedback(frame, thumb, index, middle, index_pinch, middle_pinch, current_time)
                return
        else:
            self._reset_right_pinch_state()

        if left_pinch_valid and not self.gesture_latched:
            if not self.left_pinch_started:
                self.left_pinch_started = True
                self.left_pinch_start_time = current_time
                self.left_action_fired = False
            if not self.left_action_fired and cooldown_ready:
                left_hold_time = current_time - self.left_pinch_start_time
                if self.double_click_enabled:
                    # With double-click enabled, wait while pinched.
                    # Long hold -> double click, release before hold -> single left click.
                    if left_hold_time >= self.double_click_hold:
                        self._trigger('DOUBLE CLICK', mouse, current_time)
                        self.left_action_fired = True
                elif left_hold_time >= self.left_click_activation_time:
                    self._trigger('LEFT CLICK', mouse, current_time)
                    self.left_action_fired = True
        else:
            if self.left_pinch_started and not self.left_action_fired and cooldown_ready:
                left_hold_time = current_time - self.left_pinch_start_time
                if left_hold_time >= self.left_click_activation_time:
                    self._trigger('LEFT CLICK', mouse, current_time)
            self._reset_left_pinch_state()

        self._draw_feedback(frame, thumb, index, middle, index_pinch, middle_pinch, current_time)