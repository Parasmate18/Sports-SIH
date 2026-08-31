import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PoseDetector:

    def __init__(self):

        base_options = python.BaseOptions(
            model_asset_path="pose_landmarker_lite.task"
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1
        )

        self.detector = vision.PoseLandmarker.create_from_options(
            options
        )

    def detect(self, frame, timestamp_ms):

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.detector.detect_for_video(
            image,
            timestamp_ms
        )

        return result


if __name__ == "__main__":

    detector = PoseDetector()

    camera = cv2.VideoCapture(0)

    timestamp = 0

    while camera.isOpened():

        success, frame = camera.read()

        if not success:
            print("Camera open nahi hua!")
            break

        result = detector.detect(
            frame,
            timestamp
        )

        timestamp += 33

        if result.pose_landmarks:

            print("Person detected!")

            h, w, _ = frame.shape

            for landmark in result.pose_landmarks[0]:

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

        else:

            print("Person not detected")

        cv2.imshow(
            "SIH25073 - Pose Detection",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
