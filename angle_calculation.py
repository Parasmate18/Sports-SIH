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

    cosine_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )

    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    return np.degrees(np.arccos(cosine_angle))


model_path = "../models/pose_landmarker_full.task"

base_options = python.BaseOptions(
    model_asset_path=model_path
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1
)

landmarker = vision.PoseLandmarker.create_from_options(options)

video = cv2.VideoCapture("../videos/test.mp4")

fps = video.get(cv2.CAP_PROP_FPS)
frame_number = 0

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

    result = landmarker.detect_for_video(mp_image, timestamp)

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

        print(f"Knee Angle: {angle:.2f}")

    frame_number += 1

video.release()
landmarker.close()
