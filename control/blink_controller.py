import time
import config

class BlinkController:

    def __init__(self):
        self.blink_threshold = 0.25  # Increased EAR threshold (easier to trigger)
        self.is_blinking = False
        
        self.blink_count = 0
        self.last_blink_time = 0
        
        self.double_blink_window = 0.5  # Increased time window for double blinks
        self.click_processed = True

    def process(self, ear, mouse):
        current_time = time.time()
        
        # Detect blink state transition (falling edge)
        if ear < self.blink_threshold:
            if not self.is_blinking:
                self.is_blinking = True
        else:
            if self.is_blinking:
                self.is_blinking = False
                # Blink completed (rising edge)
                self.blink_count += 1
                self.last_blink_time = current_time
                self.click_processed = False

        # Process blinks after the window has expired
        if not self.click_processed and (current_time - self.last_blink_time > self.double_blink_window):
            if self.blink_count == 1:
                mouse.left_click()
            elif self.blink_count >= 2:
                # Right click maps to double blink
                # Instead of holding a reference to pyautogui here natively, 
                # we assume mouse controller has a right_click method
                if hasattr(mouse, 'right_click'):
                    mouse.right_click()
                elif hasattr(mouse, 'left_click'):
                    # Fallback if mouse hasn't been updated yet
                    import pyautogui
                    pyautogui.rightClick()
                    
            # Reset counters
            self.blink_count = 0
            self.click_processed = True
