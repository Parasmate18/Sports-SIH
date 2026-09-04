import sys
import os
import cv2
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from pose_detector import PoseDetector
from tests.situp import SitUpAnalyzer


detector = PoseDetector()
analyzer = SitUpAnalyzer()

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

timestamp = 0
frames_processed = 0

min_body_angle = 180
max_body_angle = 0

window = "SIH25073 - Sit-up Test"

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

        if "body_angle" in data:

            angle = data["body_angle"]

            min_body_angle = min(
                min_body_angle,
                angle
            )

            max_body_angle = max(
                max_body_angle,
                angle
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
            "SIT-UP TEST",
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

        cv2.putText(
            frame,
            f"BODY: {int(data.get('body_angle', 0))}",
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
    "test": "situp",
    "timestamp": datetime.now().isoformat(),
    "person_detected": frames_processed > 0,
    "frames_processed": frames_processed,
    "valid_reps": analyzer.reps,
    "features": {
        "min_body_angle": round(min_body_angle, 2),
        "max_body_angle": round(max_body_angle, 2)
    }
}

with open(
    os.path.join(ROOT, "cv_result.json"),
    "w",
    encoding="utf-8"
) as file:

    json.dump(result_data, file, indent=4)

print(json.dumps(result_data, indent=4))
print("\nSaved: C:\\cv module\\cv_result.json")
