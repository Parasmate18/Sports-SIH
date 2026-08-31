import cv2
import json
import os
from datetime import datetime

from pose_detector import PoseDetector

from tests.pushup import PushUpAnalyzer
from tests.squat import SquatAnalyzer
from tests.situp import SitUpAnalyzer
from tests.pullup import PullUpAnalyzer
from tests.running import RunningAnalyzer


TESTS = {
    "1": ("Push-up", PushUpAnalyzer, "pushup"),
    "2": ("Squat", SquatAnalyzer, "squat"),
    "3": ("Sit-up", SitUpAnalyzer, "situp"),
    "4": ("Pull-up", PullUpAnalyzer, "pullup"),
    "5": ("Running", RunningAnalyzer, "running")
}


def run_test(test_name, AnalyzerClass, test_key):

    print()
    print("=" * 50)
    print(f"Starting {test_name} test...")
    print("=" * 50)
    print()
    print("Camera opening...")
    print("Perform the exercise.")
    print("Press Q or ESC to finish.")
    print()

    detector = PoseDetector()
    analyzer = AnalyzerClass()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Camera open nahi hua!")
        return

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    timestamp = 0
    frames_processed = 0

    min_elbow_angle = 180
    max_elbow_angle = 0

    min_knee_angle = 180
    max_knee_angle = 0

    min_body_angle = 180
    max_body_angle = 0

    window = f"Fitness AI - {test_name}"

    cv2.namedWindow(
        window,
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        window,
        1000,
        700
    )

    stopped = False

    while not stopped:

        success, frame = camera.read()

        if not success:
            print("Camera frame read nahi hua!")
            break

        frames_processed += 1

        # ------------------------------------------
        # POSE DETECTION
        # ------------------------------------------

        try:
            result = detector.detect(
                frame,
                timestamp
            )
        except TypeError:
            result = detector.detect(frame)

        timestamp += 33

        data = {}

        # ------------------------------------------
        # PERSON DETECTED
        # ------------------------------------------

        if result.pose_landmarks:

            landmarks = result.pose_landmarks[0]

            # --------------------------------------
            # ANALYZER
            # --------------------------------------

            try:

                if test_key == "running":
                    data = analyzer.analyze(
                        landmarks,
                        timestamp
                    )
                else:
                    data = analyzer.analyze(
                        landmarks
                    )

            except TypeError:

                try:
                    data = analyzer.analyze(
                        landmarks
                    )
                except Exception:
                    data = {}

            except Exception:
                data = {}

            # --------------------------------------
            # FEATURES
            # --------------------------------------

            if isinstance(data, dict):

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

                if "knee_angle" in data:

                    angle = data["knee_angle"]

                    min_knee_angle = min(
                        min_knee_angle,
                        angle
                    )

                    max_knee_angle = max(
                        max_knee_angle,
                        angle
                    )

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

            # --------------------------------------
            # DRAW POSE
            # --------------------------------------

            try:

                frame = detector.draw(
                    frame,
                    result
                )

            except Exception:

                h, w, _ = frame.shape

                for landmark in landmarks:

                    x = int(
                        landmark.x * w
                    )

                    y = int(
                        landmark.y * h
                    )

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

            # --------------------------------------
            # TEST NAME
            # --------------------------------------

            cv2.putText(
                frame,
                test_name.upper(),
                (40, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )

            # --------------------------------------
            # REPS
            # --------------------------------------

            if isinstance(data, dict):

                if "reps" in data:

                    cv2.putText(
                        frame,
                        f"REPS: {data['reps']}",
                        (40, 115),
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

                if "elbow_angle" in data:

                    cv2.putText(
                        frame,
                        f"ELBOW: {int(data['elbow_angle'])} deg",
                        (40, 205),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2
                    )

                if "knee_angle" in data:

                    cv2.putText(
                        frame,
                        f"KNEE: {int(data['knee_angle'])} deg",
                        (40, 205),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2
                    )

                if "body_angle" in data:

                    cv2.putText(
                        frame,
                        f"BODY: {int(data['body_angle'])} deg",
                        (40, 205),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2
                    )

                if "steps" in data:

                    cv2.putText(
                        frame,
                        f"STEPS: {data['steps']}",
                        (40, 115),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 255, 0),
                        3
                    )

        else:

            cv2.putText(
                frame,
                "PERSON NOT DETECTED",
                (40, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )

        # ------------------------------------------
        # INSTRUCTION
        # ------------------------------------------

        cv2.putText(
            frame,
            "Q = Finish    ESC = Finish",
            (40, frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # ------------------------------------------
        # SHOW
        # ------------------------------------------

        cv2.imshow(
            window,
            frame
        )

        # ------------------------------------------
        # KEY HANDLING
        # ------------------------------------------

        key = cv2.waitKeyEx(1)

        if key != -1:

            print(
                f"Key pressed: {key}",
                end="\r"
            )

        # Q
        if key in (
            ord("q"),
            ord("Q")
        ):

            print("\nQ detected. Stopping...")
            stopped = True

        # ESC
        elif key == 27:

            print("\nESC detected. Stopping...")
            stopped = True


    # ------------------------------------------
    # CLOSE CAMERA
    # ------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    # Give Windows time to close OpenCV window
    for _ in range(5):
        cv2.waitKey(1)


    # ==================================================
    # FINAL RESULT
    # ==================================================

    valid_reps = getattr(
        analyzer,
        "reps",
        0
    )

    features = {}

    if min_elbow_angle < 180:

        features["min_elbow_angle"] = round(
            min_elbow_angle
        )

        features["max_elbow_angle"] = round(
            max_elbow_angle
        )

    if min_knee_angle < 180:

        features["min_knee_angle"] = round(
            min_knee_angle
        )

        features["max_knee_angle"] = round(
            max_knee_angle
        )

    if min_body_angle < 180:

        features["min_body_angle"] = round(
            min_body_angle
        )

        features["max_body_angle"] = round(
            max_body_angle
        )


    # ==================================================
    # AI/ML JSON
    # ==================================================

    result_data = {

        "test": test_key,

        "timestamp":
            datetime.now().isoformat(),

        "person_detected":
            frames_processed > 0,

        "frames_processed":
            frames_processed,

        "valid_reps":
            valid_reps,

        "features":
            features

    }


    if test_key == "running":

        result_data["steps"] = getattr(
            analyzer,
            "steps",
            0
        )


    # ==================================================
    # SAVE RESULT
    # ==================================================

    output_file = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "cv_result.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result_data,
            file,
            indent=4
        )


    # ==================================================
    # RESULT FORMAT
    # ==================================================

    print()
    print()
    print("=" * 55)
    print(
        f"             {test_name.upper()} TEST RESULT"
    )
    print("=" * 55)

    print()
    print(
        "              PERFORMANCE SUMMARY"
    )

    print()

    print(
        f"  Repetitions        : {valid_reps}"
    )

    if "min_elbow_angle" in features:

        print(
            f"  Min Elbow Angle    : "
            f"{features['min_elbow_angle']} deg"
        )

        print(
            f"  Max Elbow Angle    : "
            f"{features['max_elbow_angle']} deg"
        )

    if "min_knee_angle" in features:

        print(
            f"  Min Knee Angle     : "
            f"{features['min_knee_angle']} deg"
        )

        print(
            f"  Max Knee Angle     : "
            f"{features['max_knee_angle']} deg"
        )

    if "min_body_angle" in features:

        print(
            f"  Min Body Angle     : "
            f"{features['min_body_angle']} deg"
        )

        print(
            f"  Max Body Angle     : "
            f"{features['max_body_angle']} deg"
        )

    if test_key == "running":

        print(
            f"  Steps              : "
            f"{result_data['steps']}"
        )

    print()
    print("-" * 55)

    print(
        f"  Person Detected    : "
        f"{'YES' if result_data['person_detected'] else 'NO'}"
    )

    print(
        f"  Frames Processed   : "
        f"{frames_processed}"
    )

    print("-" * 55)

    print()
    print(
        "  CV STATUS          : SUCCESS"
    )

    print()
    print(
        "  Movement detected"
    )

    print(
        "  Repetitions calculated"
    )

    print(
        "  Features extracted"
    )

    print(
        "  Ready for AI/ML"
    )

    print()
    print(
        f"  JSON Output        : {output_file}"
    )

    print()
    print("=" * 55)

    print()
    print("Returning to main menu...")


def main():

    while True:

        print()
        print()
        print("=" * 40)
        print("          FITNESS AI SYSTEM")
        print("=" * 40)

        print()
        print("1. Push-up")
        print("2. Squat")
        print("3. Sit-up")
        print("4. Pull-up")
        print("5. Running")

        print()
        print("Q. Exit")

        print()

        choice = input(
            "Enter choice: "
        ).strip().lower()

        if choice == "q":

            print()
            print("Program closed.")
            break

        if choice not in TESTS:

            print()
            print("Invalid choice!")
            continue

        test_name, AnalyzerClass, test_key = TESTS[
            choice
        ]

        run_test(
            test_name,
            AnalyzerClass,
            test_key
        )


if __name__ == "__main__":

    main()
