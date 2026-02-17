import cv2
import dlib
import winsound
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

# ================= CONSTANTS =================

EAR_THRESHOLD = 0.21
CONSECUTIVE_FRAMES = 15

# ================= LOAD MODELS =================

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# ================= GENERATE FRAMES =================

def generate_frames():
    global current_ear, drowsy_state

    cap = cv2.VideoCapture(0)

    count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            ear = (calculate_ear(leftEye) + calculate_ear(rightEye)) / 2.0
            current_ear = ear

            cv2.drawContours(frame, [cv2.convexHull(leftEye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)

            cv2.putText(frame, f"EAR: {ear:.2f}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            if ear < EAR_THRESHOLD:
                count += 1
                if count >= CONSECUTIVE_FRAMES:
                    drowsy_state = True

                    cv2.putText(frame, "DROWSINESS ALERT!", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            else:
                count = 0
                drowsy_state = False

        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

