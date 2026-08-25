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
angles = []

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

    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]

        hip = landmarks[23]
        knee = landmarks[25]
        ankle = landmarks[27]

        angle = calculate_angle(
            [hip.x, hip.y],
            [knee.x, knee.y],
            [ankle.x, ankle.y]
        )

        angles.append(angle)

        if angle < 100:
            stage = "down"

        elif angle > 160 and stage == "down":
            stage = "up"
            reps += 1

    frame_number += 1

video.release()
landmarker.close()

if angles:
    min_angle = min(angles)
    max_angle = max(angles)
    average_angle = sum(angles) / len(angles)
    rom = max_angle - min_angle

    print()
    print("SPORTS PERFORMANCE ANALYSIS")
    print("---------------------------")
    print(f"Total Reps: {reps}")
    print(f"Minimum Knee Angle: {min_angle:.2f}")
    print(f"Maximum Knee Angle: {max_angle:.2f}")
    print(f"Average Knee Angle: {average_angle:.2f}")
    print(f"Range of Motion: {rom:.2f}")
else:
    print("No pose detected.")
