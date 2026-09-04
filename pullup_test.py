import sys
import os
import cv2
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from pose_detector import PoseDetector
from tests.pullup import PullUpAnalyzer


detector = PoseDetector()
analyzer = PullUpAnalyzer()

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

timestamp = 0
frames_processed = 0

window = "SIH25073 - Pull-up Test"

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

        data = analyzer.analyze(landmarks)

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
            "PULL-UP TEST",
            (40, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            f"REPS: {data.get('reps', 0)}",
            (40, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        if "stage" in data:

            cv2.putText(
                frame,
                f"STAGE: {data['stage']}",
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
    "test": "pullup",
    "timestamp": datetime.now().isoformat(),
    "person_detected": frames_processed > 0,
    "frames_processed": frames_processed,
    "valid_reps": analyzer.reps
}

with open(
    os.path.join(ROOT, "cv_result.json"),
    "w",
    encoding="utf-8"
) as file:

    json.dump(result_data, file, indent=4)

print(json.dumps(result_data, indent=4))
print("\nSaved: C:\\cv module\\cv_result.json")
