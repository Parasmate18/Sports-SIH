from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import cv2

from cv_module.pose_detector import PoseDetector
from cv_module.session_store import save_result, load_session, clear_session
from cv_module.tests.pushup import PushUpAnalyzer
from cv_module.tests.squat import SquatAnalyzer
from cv_module.tests.deadlift import DeadliftAnalyzer
from cv_module.tests.running import Running50mAnalyzer
from cv_module.tests.situp import SitUpAnalyzer
from cv_module.tests.plank import PlankAnalyzer
from cv_module.tests.vertical_jump import VerticalJumpAnalyzer


TESTS = {
    "1": ("Push-up", "pushup", PushUpAnalyzer),
    "2": ("Squat", "squat", SquatAnalyzer),
    "3": ("Deadlift", "deadlift", DeadliftAnalyzer),
    "4": ("50 m Running", "running", Running50mAnalyzer),
    "5": ("Sit-up", "situp", SitUpAnalyzer),
    "6": ("Plank", "plank", PlankAnalyzer),
    "7": ("Vertical Jump", "vertical_jump", VerticalJumpAnalyzer),
}


def _make_analyzer(test_key, athlete_height_cm=None):
    if test_key == "vertical_jump":
        if athlete_height_cm is None:
            athlete_height_cm = float(
                input(
                    "Enter athlete height in cm for jump calibration: "
                ).strip()
            )
        return VerticalJumpAnalyzer(athlete_height_cm)

    cls = next(
        cls
        for _, key, cls in TESTS.values()
        if key == test_key
    )

    return cls()


def _measurement(test_key, analyzer):
    if test_key == "pushup":
        return {"pushup_count": int(analyzer.reps)}

    if test_key == "squat":
        return {"squat_count": int(analyzer.reps)}

    if test_key == "deadlift":
        return {"deadlift_reps": int(analyzer.reps)}

    if test_key == "running":
        return {
            "running_50m_seconds": analyzer.elapsed_seconds
        }

    if test_key == "situp":
        return {"situp_count": int(analyzer.reps)}

    if test_key == "plank":
        return {
            "plank_duration_seconds": round(
                float(analyzer.duration_seconds),
                2,
            )
        }

    if test_key == "vertical_jump":
        return {
            "vertical_jump_cm": round(
                float(analyzer.jump_height_cm),
                2,
            )
        }

    return {}


def run_test(
    test_name,
    test_key,
    AnalyzerClass=None,
    athlete_height_cm=None,
    camera_index=0,
    input_source="webcam",
    video_path=None,
):
    """
    Run one exercise using either:

    input_source="webcam"
        Existing webcam behaviour.

    input_source="video"
        Process a prerecorded video file.

    The same exercise analyzers are used for both sources.
    """

    print("\n" + "=" * 58)
    print(f"Starting {test_name} test")
    print("=" * 58)

    # EXERCISE-SPECIFIC INFORMATION

    if test_key == "deadlift":
        print(
            "SAFETY: use only an expert-approved standard load "
            "with trained supervision."
        )

    if test_key == "running":
        print(
            "Use a physically measured 50 m course."
        )

        if input_source == "webcam":
            print(
                "Press S at the start and F at the finish."
            )

        print(
            "The camera validates body movement/steps; "
            "it does NOT measure 50 m distance."
        )

    if test_key == "vertical_jump":
        print(
            "Stand still for ~1 second first so the camera "
            "can calibrate against athlete height."
        )

    if input_source == "video":
        print(f"Video file: {video_path}")
        print("Processing video...")
        print("Press Q or ESC to stop.")

    else:
        print("Camera opening...")
        print("Press Q or ESC to finish the camera test.")

    print()

    # CREATE ANALYZER

    analyzer = _make_analyzer(
        test_key,
        athlete_height_cm,
    )

    detector = PoseDetector()

    # OPEN INPUT

    if input_source == "video":
        camera = cv2.VideoCapture(str(video_path))
    else:
        camera = cv2.VideoCapture(
            camera_index,
            cv2.CAP_DSHOW,
        )

    if not camera.isOpened():
        detector.close()

        if input_source == "video":
            raise RuntimeError(
                f"Video could not be opened: {video_path}"
            )

        raise RuntimeError(
            "Camera could not be opened."
        )

    # CAMERA RESOLUTION

    if input_source == "webcam":
        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            1280,
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            720,
        )

    # VIDEO FPS

    fps = camera.get(cv2.CAP_PROP_FPS)

    if not fps or fps <= 0:
        fps = 30.0

    # PROCESSING VARIABLES

    start_clock = time.monotonic()

    frames_processed = 0
    person_frames = 0

    last_data = {}

    window = f"SIH25073 - {test_name}"

    cv2.namedWindow(
        window,
        cv2.WINDOW_NORMAL,
    )

    cv2.resizeWindow(
        window,
        1000,
        700,
    )

    # MAIN FRAME LOOP

    try:
        while True:

            ok, frame = camera.read()

            if not ok:

                if input_source == "video":
                    print("\nVideo processing finished.")

                break

            frames_processed += 1

            # TIMESTAMP

            if input_source == "video":

                # Video timestamp is based on frame number
                # and FPS instead of wall-clock time.
                timestamp_ms = max(
                    1,
                    int(
                        (frames_processed - 1)
                        * 1000.0
                        / fps
                    ),
                )

            else:

                # Preserve the original webcam behaviour.
                timestamp_ms = max(
                    1,
                    int(
                        (
                            time.monotonic()
                            - start_clock
                        )
                        * 1000
                    ),
                )

            # POSE DETECTION

            result = detector.detect(
                frame,
                timestamp_ms,
            )

            person = bool(
                result.pose_landmarks
            )

            if person:

                person_frames += 1

                landmarks = result.pose_landmarks[0]

                try:

                    last_data = analyzer.analyze(
                        landmarks,
                        timestamp_ms,
                    )

                except Exception as exc:

                    last_data = {
                        "stage": "ANALYZER_ERROR",
                        "error": str(exc),
                    }


                # DRAW LANDMARKS


                h, w = frame.shape[:2]

                for lm in landmarks:

                    visibility = float(
                        getattr(
                            lm,
                            "visibility",
                            1.0,
                        )
                        or 0.0
                    )

                    if visibility >= 0.45:

                        cv2.circle(
                            frame,
                            (
                                int(lm.x * w),
                                int(lm.y * h),
                            ),
                            3,
                            (0, 255, 0),
                            -1,
                        )

            else:

                last_data = {
                    "stage": "PERSON_NOT_DETECTED"
                }

            # DISPLAY TITLE

            cv2.putText(
                frame,
                test_name.upper(),
                (35, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
            )

            # DISPLAY INPUT SOURCE

            source_text = (
                "VIDEO"
                if input_source == "video"
                else "WEBCAM"
            )

            cv2.putText(
                frame,
                f"SOURCE: {source_text}",
                (35, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
            )

            # DISPLAY STAGE

            stage = str(
                last_data.get(
                    "stage",
                    "",
                )
            )

            cv2.putText(
                frame,
                f"STAGE: {stage}",
                (35, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
            )

            # REP DISPLAY

            if hasattr(analyzer, "reps"):

                cv2.putText(
                    frame,
                    f"REPS: {analyzer.reps}",
                    (35, 165),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.90,
                    (0, 255, 0),
                    2,
                )

            # PLANK

            if test_key == "plank":

                cv2.putText(
                    frame,
                    (
                        f"VALID HOLD: "
                        f"{analyzer.duration_seconds:.1f}s"
                    ),
                    (35, 165),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.90,
                    (0, 255, 0),
                    2,
                )

            # RUNNING

            if test_key == "running":

                elapsed = analyzer.elapsed_seconds

                if (
                    analyzer.started_at is not None
                    and analyzer.finished_at is None
                ):

                    elapsed = (
                        timestamp_ms
                        - analyzer.started_at
                    ) / 1000.0

                timer_text = (
                    f"TIMER: {elapsed:.2f}s"
                    if elapsed is not None
                    else "TIMER: READY"
                )

                cv2.putText(
                    frame,
                    timer_text,
                    (35, 165),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.90,
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    f"STEPS: {analyzer.steps}",
                    (35, 205),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (255, 255, 255),
                    2,
                )

                # S/F controls are only meaningful for webcam.
                if input_source == "webcam":

                    cv2.putText(
                        frame,
                        "S=start  F=finish",
                        (35, 245),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.70,
                        (255, 255, 255),
                        2,
                    )

            # VERTICAL JUMP

            if test_key == "vertical_jump":

                cv2.putText(
                    frame,
                    (
                        f"JUMP: "
                        f"{analyzer.jump_height_cm:.1f} cm"
                    ),
                    (35, 165),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.90,
                    (0, 255, 0),
                    2,
                )

            # FINISH MESSAGE

            cv2.putText(
                frame,
                "Q / ESC = finish",
                (
                    35,
                    frame.shape[0] - 25,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            # SHOW FRAME

            cv2.imshow(
                window,
                frame,
            )

            key = cv2.waitKeyEx(1)

            # RUNNING START

            if (
                input_source == "webcam"
                and test_key == "running"
                and key in (
                    ord("s"),
                    ord("S"),
                )
            ):

                if person:

                    analyzer.start(
                        timestamp_ms
                    )

                    print(
                        "50 m timer STARTED"
                    )

                else:

                    print(
                        "Start ignored: "
                        "person not detected."
                    )

            # RUNNING FINISH

            elif (
                input_source == "webcam"
                and test_key == "running"
                and key in (
                    ord("f"),
                    ord("F"),
                )
            ):

                if analyzer.finish(
                    timestamp_ms
                ):

                    print(
                        "50 m timer FINISHED: "
                        f"{analyzer.elapsed_seconds:.2f} s"
                    )

                else:

                    print(
                        "Finish ignored: "
                        "press S first."
                    )

            # EXIT

            elif key in (
                ord("q"),
                ord("Q"),
                27,
            ):

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

        detector.close()

        for _ in range(3):
            cv2.waitKey(1)

    # BUILD MEASUREMENT

    measurement = _measurement(
        test_key,
        analyzer,
    )

    # RESULT STATUS

    if (
        test_key == "running"
        and measurement[
            "running_50m_seconds"
        ] is None
    ):

        status = "INCOMPLETE"

    elif person_frames == 0:

        status = "INCOMPLETE"

    else:

        status = "SUCCESS"

    # RESULT DATA

    result_data = {
        "test": test_key,
        "timestamp": datetime.now().isoformat(),
        "status": status,

        # NEW:
        # tells us whether the result came from
        # webcam or video.
        "input_source": input_source,

        "person_detected": person_frames > 0,

        "frames_processed": frames_processed,

        "person_frames": person_frames,

        "measurement": measurement,

        "features": {
            k: v
            for k, v in last_data.items()
            if k not in {
                "test",
                "reps",
                "stage",
                "valid_posture",
            }
        },

        "quality": {
            "last_stage": last_data.get(
                "stage"
            ),

            "last_frame_valid_posture": bool(
                last_data.get(
                    "valid_posture",
                    False,
                )
            ),

            "invalid_frames": int(
                getattr(
                    analyzer,
                    "invalid_frames",
                    0,
                )
            ),
        },
    }

    # REP RESULTS

    if hasattr(analyzer, "reps"):

        result_data[
            "valid_reps"
        ] = int(analyzer.reps)

    # RUNNING RESULTS

    if test_key == "running":

        result_data["steps"] = int(
            analyzer.steps
        )

        result_data["distance_protocol"] = (
            "physically measured 50 m course required"
        )

        result_data["timing_method"] = (
            "operator start/finish keys "
            "with CV movement validation"
        )

    # VERTICAL JUMP

    if test_key == "vertical_jump":

        result_data["calibration"] = (
            "athlete-height single-camera estimate; "
            "validate against a measured reference "
            "before official use"
        )

    # DEADLIFT SAFETY

    if test_key == "deadlift":

        result_data["safety"] = (
            "expert-approved standard load "
            "and trained supervision required"
        )

    # SAVE

    path = save_result(
        result_data
    )

    print("\nRESULT")

    print(
        json.dumps(
            result_data,
            indent=2,
        )
    )

    print(
        f"\nSaved: {path}"
    )

    return result_data


def main():

    while True:

        print(
            "\n"
            + "=" * 44
        )

        print(
            "      ASSESSMENT"
        )

        print(
            "=" * 44
        )

        for choice, (
            name,
            _,
            _,
        ) in TESTS.items():

            print(
                f"{choice}. {name}"
            )

        print(
            "A. Show current session results"
        )

        print(
            "C. Clear current session"
        )

        print(
            "Q. Exit"
        )

        choice = input(
            "\nEnter choice: "
        ).strip().lower()


        # EXIT


        if choice == "q":
            break


        # SHOW SESSION


        if choice == "a":

            print(
                json.dumps(
                    load_session(),
                    indent=2,
                )
            )

            continue


        # CLEAR SESSION


        if choice == "c":

            clear_session()

            print(
                "Session cleared."
            )

            continue


        # INVALID EXERCISE


        if choice not in TESTS:

            print(
                "Invalid choice."
            )

            continue


        # EXERCISE


        name, key, cls = TESTS[choice]


        # INPUT SOURCE MENU


        print(
            "\nInput source:"
        )

        print(
            "1. Web Camera"
        )

        print(
            "2. Video File"
        )

        source_choice = input(
            "Choose input: "
        ).strip()


        # WEBCAM


        if source_choice == "1":

            try:

                run_test(
                    name,
                    key,
                    cls,
                    input_source="webcam",
                )

            except Exception as exc:

                print(
                    f"\nERROR: {exc}"
                )


        # VIDEO


        elif source_choice == "2":

            video_path = input(
                "\nEnter full path to video file: "
            ).strip().strip('"')

            if not video_path:

                print(
                    "No video file selected."
                )

                continue

            video_file = Path(
                video_path
            )

            if not video_file.exists():

                print(
                    f"Video file not found:\n"
                    f"{video_file}"
                )

                continue

            if not video_file.is_file():

                print(
                    "The selected path is not a file."
                )

                continue

            try:

                run_test(
                    name,
                    key,
                    cls,
                    input_source="video",
                    video_path=video_file,
                )

            except Exception as exc:

                print(
                    f"\nERROR: {exc}"
                )


        # INVALID SOURCE


        else:

            print(
                "Invalid input source."
            )


if __name__ == "__main__":
    main()