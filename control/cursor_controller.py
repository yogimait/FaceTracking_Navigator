import pyautogui
import config

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class CursorController:

    def __init__(self):

        self.screen_w, self.screen_h = pyautogui.size()

        self.prev_x = self.screen_w // 2
        self.prev_y = self.screen_h // 2
        
        # Center the cursor immediately at startup
        pyautogui.moveTo(self.prev_x, self.prev_y)

        self.dead_zone = 0.03
        self.calibration = None

    def set_calibration(self, calibration):
        self.calibration = calibration

    def move(self, iris, nose):

        iris_x, iris_y = iris

        # -----------------------
        # HEAD POSITION MAPPING
        # -----------------------

        if self.calibration and self.calibration.is_ready():
            min_x = self.calibration.left
            max_x = self.calibration.right
            min_y = self.calibration.up
            max_y = self.calibration.down

            # normalize to 0–1
            nx = (nose.x - min_x) / (max_x - min_x)
            ny = (nose.y - min_y) / (max_y - min_y)

            # convert to -1 → +1
            head_x = (nx * 2) - 1      # Face left -> nx smaller -> head_x negative -> target_x left
            head_y = (ny * 2) - 1      # Face up -> ny smaller -> head_y negative -> target_y up

        else:
            # fallback if calibration not done
            head_x = (nose.x - 0.5) * 2  
            head_y = (nose.y - 0.5) * 2  

        # -----------------------
        # SENSITIVITY AMPLIFICATION
        # -----------------------
        
        # Apply a curve to amplify small movements while keeping the sign
        # head_x and head_y are in [-1, 1].
        # By taking the power of (1 / HEAD_SENSITIVITY), small values become larger.
        # Alternatively, direct multiplication by a sensitivity factor, clamped to [-1, 1]
        head_x = head_x * config.HEAD_SENSITIVITY
        head_y = head_y * config.HEAD_SENSITIVITY

        # Clamp to [-1, 1]
        head_x = max(-1.0, min(1.0, head_x))
        head_y = max(-1.0, min(1.0, head_y))

        # -----------------------
        # DEAD ZONE
        # -----------------------

        dead_zone = self.dead_zone * 0.3
        if abs(head_x) < dead_zone:
            head_x = 0
        if abs(head_y) < dead_zone:
            head_y = 0

        # -----------------------
        # SCREEN TARGET
        # -----------------------

        target_x = int((head_x + 1) / 2 * self.screen_w)
        target_y = int((head_y + 1) / 2 * self.screen_h)

        # -----------------------
        # (Eye micro-adjustment removed because it used absolute coordinates 
        #  which caused the cursor to invert and shoot across the screen)
        # -----------------------

        # -----------------------
        # CLAMP TO SCREEN
        # -----------------------

        target_x = max(0, min(self.screen_w - 1, target_x))
        target_y = max(0, min(self.screen_h - 1, target_y))

        # -----------------------
        # SMOOTHING
        # -----------------------

        smooth = max(1.5, config.CURSOR_SMOOTHING * 0.7)  # Reduce smoothing for more responsiveness
        x = int(self.prev_x + (target_x - self.prev_x) / smooth)
        y = int(self.prev_y + (target_y - self.prev_y) / smooth)

        pyautogui.moveTo(x, y)

        self.prev_x = x
        self.prev_y = y