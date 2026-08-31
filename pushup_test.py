import cv2
import json
from datetime import datetime

from pose_detector import PoseDetector
from tests.pushup import PushUpAnalyzer


detector = PoseDetector()
analyzer = PushUpAnalyzer()

camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

timestamp = 0

min_elbow_angle = 180
max_elbow_angle = 0

frames_processed = 0

window = "SIH25073 - Push-up CV Test"

cv2.namedWindow(
    window,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    window,
    1000,
    700
)


while camera.isOpened():

    success, frame = camera.read()

    if not success:
        print("Camera open nahi hua!")
        break

    frames_processed += 1

    result = detector.detect(
        frame,
        timestamp
    )

    timestamp += 33


    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        data = analyzer.analyze(
            landmarks
        )

        # -----------------------------
        # Collect elbow angle
        # -----------------------------

        if "elbow_angle" in data:

            angle = data["elbow_angle"]

            min_elbow_angle = min(
                min_elbow_angle,
                angle
            )

            max_elbow_angle = max(
                max_elbow_angle,
                angle
            )


        # -----------------------------
        # Draw landmarks
        # -----------------------------

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


        # -----------------------------
        # Display
        # -----------------------------

        cv2.putText(
            frame,
            "PUSH-UP TEST",
            (40, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )


        if "reps" in data:

            cv2.putText(
                frame,
                f"REPS: {data['reps']}",
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
                (40, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )


        if "elbow_angle" in data:

            cv2.putText(
                frame,
                f"ELBOW: {int(data['elbow_angle'])}",
                (40, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )


    else:

        cv2.putText(
            frame,
            "PERSON NOT DETECTED",
            (40, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 0, 255),
            3
        )


    cv2.putText(
        frame,
        "Press Q to finish test",
        (40, frame.shape[0] - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    cv2.imshow(
        window,
        frame
    )


    key = cv2.waitKey(10) & 0xFF

    if key == ord("q"):

        break


camera.release()

cv2.destroyAllWindows()

cv2.waitKey(1)


# =====================================
# GENERATE REAL CV OUTPUT
# =====================================

result_data = {

    "test": "pushup",

    "timestamp": datetime.now().isoformat(),

    "person_detected": frames_processed > 0,

    "frames_processed": frames_processed,

    "valid_reps": analyzer.reps,

    "features": {

        "min_elbow_angle":
            round(min_elbow_angle, 2),

        "max_elbow_angle":
            round(max_elbow_angle, 2)

    }

}


# =====================================
# SAVE JSON
# =====================================

with open(
    "cv_result.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        result_data,
        file,
        indent=4
    )


print("\n================================")
print("       CV TEST RESULT")
print("================================")

print(
    json.dumps(
        result_data,
        indent=4
    )
)

print("\nSaved as: cv_result.json")
