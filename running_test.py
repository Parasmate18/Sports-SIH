import sys
import os
import cv2
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from pose_detector import PoseDetector
from tests.running import RunningAnalyzer


detector = PoseDetector()
analyzer = RunningAnalyzer()

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

timestamp = 0
frames_processed = 0

window = "SIH25073 - Running Test"

cv2.namedWindow(window, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window, 1000, 700)

while camera.isOpened():

    success, frame = camera.read()

    if not success:
        break

    frames_processed += 1

    result = detector.detect(frame, timestamp)
    timestamp += 33

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        data = analyzer.analyze(
            landmarks,
            timestamp
        )

        h, w, _ = frame.shape

        for landmark in landmarks:

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )

        cv2.putText(
            frame,
            "RUNNING TEST",
            (40, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            f"STEPS: {data.get('steps', 0)}",
            (40, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        if "displacement" in data:

            cv2.putText(
                frame,
                f"MOVEMENT: {data['displacement']}",
                (40, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

    cv2.imshow(window, frame)

    if cv2.waitKey(10) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()

result_data = {
    "test": "running",
    "timestamp": datetime.now().isoformat(),
    "person_detected": frames_processed > 0,
    "frames_processed": frames_processed,
    "steps": getattr(analyzer, "steps", 0)
}

with open(
    os.path.join(ROOT, "cv_result.json"),
    "w",
    encoding="utf-8"
) as file:

    json.dump(result_data, file, indent=4)

print(json.dumps(result_data, indent=4))
print("\nSaved: C:\\cv module\\cv_result.json")
