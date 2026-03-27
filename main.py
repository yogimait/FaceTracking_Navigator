# main.py

import cv2

from core.camera import Camera
from gestures.gesture_manager import GestureManager
from vision.face_tracker import FaceTracker
from vision.hand_tracker import HandTracker
from core.calibration import FaceCalibration
from control.cursor_controller import CursorController
from control.mouse_controller import MouseController


def main():

    camera = Camera()

    face_tracker = FaceTracker()
    hand_tracker = HandTracker()

    cursor = CursorController()
    mouse = MouseController()
    gesture_manager = GestureManager()

    calibration = FaceCalibration()
    cursor.set_calibration(calibration)

    while True:

        frame = camera.read()

        if frame is None:
            break

        # Eye cursor
        eye_data = face_tracker.get_eye_data(frame)

        nose = None

        if eye_data is not None:
            iris, nose, _ = eye_data
            cursor.move(iris, nose)
        
        key = cv2.waitKey(1) & 0xFF

        if nose is not None:

            if key == ord('c'):
                calibration.set_center(nose)
                print("Center calibrated")

            elif key == ord('a'):
                calibration.set_left(nose)
                print("Left calibrated")

            elif key == ord('d'):
                calibration.set_right(nose)
                print("Right calibrated")

            elif key == ord('w'):
                calibration.set_up(nose)
                print("Up calibrated")

            elif key == ord('s'):
                calibration.set_down(nose)
                print("Down calibrated")

        # Hand gesture
        hand = hand_tracker.get_landmarks(frame)

        if hand:
            gesture_manager.process(hand, mouse, frame)

        cv2.imshow("Hands Free Mouse", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        input("Press Enter to exit...")