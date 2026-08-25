import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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
frame_number = 0
printed = False

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

    if result.pose_landmarks and not printed:
        landmarks = result.pose_landmarks[0]

        points = np.array([
            [landmark.x, landmark.y, landmark.z, landmark.visibility]
            for landmark in landmarks
        ])

        print("Shape:", points.shape)
        print(points)

        printed = True

    frame_number += 1

video.release()
landmarker.close()