import cv2

from pose_detector import PoseDetector
from tests.squat import SquatAnalyzer


detector = PoseDetector()
analyzer = SquatAnalyzer()

camera = cv2.VideoCapture(0)

timestamp = 0


while camera.isOpened():

    success, frame = camera.read()

    if not success:
        print("Camera open nahi hua!")
        break

    result = detector.detect(frame, timestamp)

    timestamp += 33

    if result.pose_landmarks:

        landmarks = result.pose_landmarks[0]

        data = analyzer.analyze(landmarks)

        cv2.putText(
            frame,
            f"Reps: {data['reps']}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Knee Angle: {int(data['knee_angle'])}",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Stage: {data['stage']}",
            (30, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        for landmark in landmarks:

            h, w, _ = frame.shape

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )

    cv2.imshow(
        "SIH25073 - Squat Test",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()
