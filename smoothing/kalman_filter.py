import cv2
import numpy as np

class CursorKalmanFilter:
    def __init__(self):
        # 4 state variables (x, y, dx, dy), 2 measurements (x, y)
        self.kalman = cv2.KalmanFilter(4, 2)
        
        # State Transition Matrix (A)
        # [1 0 1 0]
        # [0 1 0 1]
        # [0 0 1 0]
        # [0 0 0 1]
        self.kalman.transitionMatrix = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], np.float32)

        # Measurement Matrix (H)
        # [1 0 0 0]
        # [0 1 0 0]
        self.kalman.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], np.float32)

        # Process Noise Covariance Matrix (Q)
        # Defines how much we trust our model vs how much we think the model changes
        # Lower = smoother but more lag. Higher = faster response but more jitter.
        self.kalman.processNoiseCov = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], np.float32) * 0.03

        # Measurement Noise Covariance Matrix (R)
        # Defines how much we trust the raw camera measurements.
        # Higher = more smoothing/filtering of the noisy measurements.
        self.kalman.measurementNoiseCov = np.array([
            [1, 0],
            [0, 1]
        ], np.float32) * 0.5 

        # Initial state setup flag
        self.initialized = False

    def predict(self, target_x, target_y):
        # OpenCV Kalman filter requires measurements to be 32-bit floats
        measurement = np.array([[np.float32(target_x)], [np.float32(target_y)]], dtype=np.float32)

        if not self.initialized:
            # Initialize state immediately to avoid slowly floating from 0,0
            # Must explicitly match the type of the matrices (CV_32F)
            state = np.array([[np.float32(target_x)], [np.float32(target_y)], [0.0], [0.0]], dtype=np.float32)
            self.kalman.statePre = state
            self.kalman.statePost = state
            self.initialized = True

        # Run Kalman prediction and correction steps
        self.kalman.predict()
        estimated = self.kalman.correct(measurement)

        return int(estimated[0][0]), int(estimated[1][0])
