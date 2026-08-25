import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)

    if denominator == 0:
        return 0

    cosine_angle = np.dot(ba, bc) / denominator
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    return np.degrees(np.arccos(cosine_angle))


model_path = "../models/pose_landmarker_full.task"

base_options = python.BaseOptions(
    model_asset_path=model_path
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

landmarker = vision.PoseLandmarker.create_from_options(options)

video = cv2.VideoCapture("../videos/test.mp4")

fps = video.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

frame_number = 0
reps = 0
stage = "up"
detected_frames = 0

while True:
    success, frame = video.read()

    if not success:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp = int((frame_number / fps) * 1000)

    result = landmarker.detect_for_video(
        mp_image,
        timestamp
    )

    angle = 0

    if result.pose_landmarks:
        detected_frames += 1

        landmarks = result.pose_landmarks[0]

        hip = landmarks[23]
        knee = landmarks[25]
        ankle = landmarks[27]

        angle = calculate_angle(
            [hip.x, hip.y],
            [knee.x, knee.y],
            [ankle.x, ankle.y]
        )

        if angle < 100:
            stage = "down"

        elif angle > 160 and stage == "down":
            stage = "up"
            reps += 1

    cv2.rectangle(
        frame,
        (15, 15),
        (300, 155),
        (255, 255, 255),
        -1
    )

    cv2.putText(
        frame,
        f"Reps: {reps}",
        (30, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 0),
        2
    )

    cv2.putText(
        frame,
        f"Knee Angle: {angle:.1f}",
        (30, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2
    )

    cv2.putText(
        frame,
        f"Stage: {stage}",
        (30, 135),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2
    )

    cv2.imshow("Sports Talent Assessment", frame)

    frame_number += 1

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
landmarker.close()
cv2.destroyAllWindows()

print(f"Total frames: {frame_number}")
print(f"Detected frames: {detected_frames}")
print(f"Total reps: {reps}")
