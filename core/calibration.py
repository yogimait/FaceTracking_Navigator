# core/calibration.py

class FaceCalibration:

    def __init__(self):

        self.center = None
        self.left = None
        self.right = None
        self.up = None
        self.down = None

    def set_center(self, nose):
        self.center = (nose.x, nose.y)

    def set_left(self, nose):
        self.left = nose.x

    def set_right(self, nose):
        self.right = nose.x

    def set_up(self, nose):
        self.up = nose.y

    def set_down(self, nose):
        self.down = nose.y

    def is_ready(self):

        return all([
            self.center,
            self.left,
            self.right,
            self.up,
            self.down
        ])