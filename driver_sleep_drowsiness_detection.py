import cv2
import dlib
import winsound
import time
from scipy.spatial import distance as dist
from imutils import face_utils

# ================= GLOBAL VARIABLES =================
current_ear = 0
drowsy_state = False

# ================= EAR FUNCTION =================
def calculate_ear(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# ================= MAR FUNCTION =================
def calculate_mar(mouth):
    A = dist.euclidean(mouth[13], mouth[19])
    B = dist.euclidean(mouth[14], mouth[18])
    C = dist.euclidean(mouth[15], mouth[17])
    D = dist.euclidean(mouth[12], mouth[16])
    return (A + B + C) / (2.0 * D)

# ================= THRESHOLDS =================
EAR_THRESHOLD_NORMAL = 0.23
EAR_THRESHOLD_WARNING = 0.20
EAR_THRESHOLD_CRITICAL = 0.15

MAR_THRESHOLD = 0.6
MAR_CONSEC_FRAMES = 15

FRAME_WARNING = 10
FRAME_CRITICAL = 20

# ================= STATE MACHINE =================
class EyeTrackerSystem:
    def __init__(self):
        self.state = "NORMAL"
        self.low_frame_count = 0

    def update(self, ear):
        if ear >= EAR_THRESHOLD_NORMAL:
            self.state = "NORMAL"
            self.low_frame_count = 0

        elif ear >= EAR_THRESHOLD_WARNING:
            self.low_frame_count += 1
            if self.low_frame_count >= FRAME_WARNING:
                self.state = "WARNING"

        else:
            self.low_frame_count += 1
            if self.low_frame_count >= FRAME_CRITICAL:
                self.state = "CRITICAL"

        return self.state

# ================= LOAD MODELS =================
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# ================= GENERATE FRAMES =================
def generate_frames():
    global current_ear, drowsy_state

    cap = cv2.VideoCapture(0)
    tracker = EyeTrackerSystem()

    prev_time = 0
    yawn_count = 0  #  MAR counter

    while True:
        success, frame = cap.read()
        if not success:
            break

        # FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
        prev_time = current_time

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        ear = 0
        mar = 0

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # ===== EYES =====
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            ear = (calculate_ear(leftEye) + calculate_ear(rightEye)) / 2.0

            # ===== MOUTH =====
            mouth = shape[mStart:mEnd]
            mar = calculate_mar(mouth)

            # ===== STATE UPDATE =====
            state = tracker.update(ear)

            # ===== YAWN DETECTION =====
            if mar > MAR_THRESHOLD:
                yawn_count += 1

                if yawn_count >= MAR_CONSEC_FRAMES:
                    cv2.putText(frame, "YAWNING ALERT!", (50, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                    drowsy_state = True
            else:
                yawn_count = 0

            # ===== FINAL DROWSY STATE =====
            drowsy_state = (state in ["WARNING", "CRITICAL"]) or (mar > MAR_THRESHOLD)

            # ===== DRAW =====
            cv2.drawContours(frame, [cv2.convexHull(leftEye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(mouth)], -1, (255, 0, 0), 1)

            # TEXT
            cv2.putText(frame, f"EAR: {ear:.2f}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            cv2.putText(frame, f"MAR: {mar:.2f}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            # STATE DISPLAY
            if state == "NORMAL":
                color = (0, 255, 0)
                msg = "NORMAL"
            elif state == "WARNING":
                color = (0, 255, 255)
                msg = "WARNING"
            else:
                color = (0, 0, 255)
                msg = "CRITICAL"
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

            cv2.putText(frame, msg, (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        #  IMPORTANT (for graph)
        current_ear = ear

        # FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (30, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
