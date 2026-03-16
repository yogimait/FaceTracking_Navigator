import mediapipe as mp
import cv2


class FaceTracker:

    def __init__(self):

        self.mp_face = mp.solutions.face_mesh

        self.face_mesh = self.mp_face.FaceMesh(
            refine_landmarks=True
        )

    def get_eye_data(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        face = results.multi_face_landmarks[0]

        left_iris = face.landmark[468]
        right_iris = face.landmark[473]

        iris_x = (left_iris.x + right_iris.x) / 2
        iris_y = (left_iris.y + right_iris.y) / 2

        nose = face.landmark[1]
        
        # Calculate Eye Aspect Ratio (EAR) for blink detection
        # Left eye landmarks: 33, 160, 158, 133, 153, 144
        # Right eye landmarks: 362, 385, 387, 263, 373, 380
        
        def calc_ear(eye_points):
            # Vertical distances
            v1 = ((eye_points[1].x - eye_points[5].x)**2 + (eye_points[1].y - eye_points[5].y)**2)**0.5
            v2 = ((eye_points[2].x - eye_points[4].x)**2 + (eye_points[2].y - eye_points[4].y)**2)**0.5
            # Horizontal distance
            h = ((eye_points[0].x - eye_points[3].x)**2 + (eye_points[0].y - eye_points[3].y)**2)**0.5
            if h == 0:
                return 0
            return (v1 + v2) / (2.0 * h)

        left_eye_indices = [33, 160, 158, 133, 153, 144]
        left_eye_pts = [face.landmark[i] for i in left_eye_indices]
        left_ear = calc_ear(left_eye_pts)

        right_eye_indices = [362, 385, 387, 263, 373, 380]
        right_eye_pts = [face.landmark[i] for i in right_eye_indices]
        right_ear = calc_ear(right_eye_pts)

        avg_ear = (left_ear + right_ear) / 2.0

        return (iris_x, iris_y), nose, avg_ear