# Sports Talent Assessment — Computer Vision

pose_detection.py module performs human pose detection using OpenCV and MediaPipe Pose Landmarker.

## Tech Stack

- Python 3.13
- OpenCV
- MediaPipe
- NumPy
- MediaPipe Pose Landmarker Full Model

## Project Structure

```text
Sports-Talent-Assessment/
│
├── ai/
│   ├── pose_detection.py
│   └── README.md
│
├── models/
│   └── pose_landmarker_full.task
│
├── videos/
│   └── test.mp4
│
└── requirements.txt

Installation

Check Python:

python --version

Install required packages:

pip install opencv-python mediapipe numpy
MediaPipe Model

This project uses the MediaPipe Pose Landmarker Full model.

The model file must be:

pose_landmarker_full.task

Place it inside:

C:\Sports Talent\models\pose_landmarker_full.task
Test Video

Place a full-body test video inside:

C:\Sports Talent\videos\test.mp4
Run the Project

Open PowerShell and run:

cd "C:\Sports Talent\ai"

Then:

python pose_detection.py

A video window will open and MediaPipe will detect the person's body landmarks.

Press:

Q

to exit the video.

Current Pipeline
Input Video
     ↓
OpenCV
     ↓
RGB Conversion
     ↓
MediaPipe Pose Landmarker
     ↓
Pose Detection
     ↓
Body Landmarks
     ↓
Visualization
Current Status
 Python setup
 OpenCV installed
 MediaPipe installed
 NumPy installed
 Pose Landmarker model downloaded
 Video input working
 Pose detection working
 Body landmarks visualized
