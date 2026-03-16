# control/mouse_controller.py

import pyautogui


class MouseController:

    def left_click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.rightClick()