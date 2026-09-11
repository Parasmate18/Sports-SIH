import cv2
from datetime import datetime

from cv_module.pose_detector import PoseDetector

from cv_module.tests.pushup import PushUpAnalyzer
from cv_module.tests.squat import SquatAnalyzer
from cv_module.tests.deadlift import DeadliftAnalyzer
from cv_module.tests.running import Running50mAnalyzer
from cv_module.tests.situp import SitUpAnalyzer
from cv_module.tests.plank import PlankAnalyzer
from cv_module.tests.vertical_jump import VerticalJumpAnalyzer


# ==========================================================
# Analyzer mapping
# ==========================================================

ANALYZERS = {
    "pushup": PushUpAnalyzer,
    "squat": SquatAnalyzer,
    "deadlift": DeadliftAnalyzer,
    "running": Running50mAnalyzer,
    "situp": SitUpAnalyzer,
    "plank": PlankAnalyzer,
    "vertical_jump": VerticalJumpAnalyzer,
}


# ==========================================================
# Measurement field mapping
# ==========================================================

MEASUREMENT_FIELDS = {
    "pushup": "pushup_count",
    "squat": "squat_count",
    "deadlift": "deadlift_reps",
    "running": "running_50m_seconds",
    "situp": "situp_count",
    "plank": "plank_duration_seconds",
    "vertical_jump": "vertical_jump_cm",
}


# ==========================================================
# Generic exercise video processor
# ==========================================================

def process_exercise_video(
    video_path: str,
    exercise: str,
    athlete_height_cm: float | None = None,
) -> dict:

    exercise = exercise.lower().strip()

    if exercise not in ANALYZERS:
        raise ValueError(
            f"Unsupported exercise: {exercise}"
        )

    # ------------------------------------------------------
    # Create pose detector
    # ------------------------------------------------------

    detector = PoseDetector()

    # ------------------------------------------------------
    # Create exercise analyzer
    # ------------------------------------------------------

    if exercise == "vertical_jump":

        if athlete_height_cm is None:
            detector.close()

            raise ValueError(
                "Athlete height is required for vertical jump"
            )

        analyzer = VerticalJumpAnalyzer(
            athlete_height_cm
        )

    else:

        AnalyzerClass = ANALYZERS[exercise]

        analyzer = AnalyzerClass()

    # ------------------------------------------------------
    # Open video
    # ------------------------------------------------------

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        detector.close()

        raise ValueError(
            "Could not open video file"
        )

    # ------------------------------------------------------
    # Read FPS
    # ------------------------------------------------------

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if not fps or fps <= 0:
        fps = 30

    # ------------------------------------------------------
    # Processing variables
    # ------------------------------------------------------

    frames_processed = 0

    person_frames = 0

    last_data = {}

    analyzer_error = None

    # Running-specific variables
    running_started = False

    last_person_timestamp = None

    # ------------------------------------------------------
    # Process video
    # ------------------------------------------------------

    try:

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frames_processed += 1

            # ----------------------------------------------
            # Video timestamp
            # ----------------------------------------------

            timestamp_ms = max(
                1,
                int(
                    (frames_processed - 1)
                    * 1000
                    / fps
                )
            )

            # ----------------------------------------------
            # Pose detection
            # ----------------------------------------------

            result = detector.detect(
                frame,
                timestamp_ms
            )

            # No person detected
            if not result.pose_landmarks:
                continue

            person_frames += 1

            landmarks = (
                result.pose_landmarks[0]
            )

            # ----------------------------------------------
            # Running start logic
            # ----------------------------------------------

            if exercise == "running":

                if not running_started:

                    analyzer.start(
                        timestamp_ms
                    )

                    running_started = True

                last_person_timestamp = (
                    timestamp_ms
                )

            # ----------------------------------------------
            # Analyze pose
            # ----------------------------------------------

            try:

                last_data = analyzer.analyze(
                    landmarks,
                    timestamp_ms
                )

            except Exception as exc:

                analyzer_error = str(exc)

                last_data = {
                    "stage": "ANALYZER_ERROR",
                    "valid_posture": False,
                }

                break

        # --------------------------------------------------
        # Running finish logic
        # --------------------------------------------------

        if (
            exercise == "running"
            and running_started
            and last_person_timestamp is not None
        ):

            analyzer.finish(
                last_person_timestamp
            )

            last_data = {
                "test": "running",

                "steps":
                    analyzer.steps,

                "elapsed_seconds":
                    analyzer.elapsed_seconds,

                "stage":
                    analyzer.stage,

                "person_detected":
                    True,

                "valid_posture":
                    True,
            }

    finally:

        cap.release()

        detector.close()

    # ======================================================
    # Determine result status
    # ======================================================

    if frames_processed == 0:

        status = "INCOMPLETE"

    elif person_frames == 0:

        status = "INCOMPLETE"

    elif analyzer_error is not None:

        status = "INCOMPLETE"

    elif (
        exercise == "running"
        and analyzer.elapsed_seconds is None
    ):

        status = "INCOMPLETE"

    else:

        status = "SUCCESS"

    # ======================================================
    # Measurement
    # ======================================================

    measurement_field = (
        MEASUREMENT_FIELDS[exercise]
    )

    measurement_value = 0

    valid_reps = 0

    # ------------------------------------------------------
    # REP-BASED EXERCISES
    # ------------------------------------------------------

    if exercise in {
        "pushup",
        "squat",
        "deadlift",
        "situp",
    }:

        valid_reps = getattr(
            analyzer,
            "reps",
            0
        )

        measurement_value = (
            valid_reps
        )

    # ------------------------------------------------------
    # RUNNING
    # ------------------------------------------------------

    elif exercise == "running":

        measurement_value = getattr(
            analyzer,
            "elapsed_seconds",
            None
        )

        if measurement_value is not None:
            measurement_value = round(
                float(measurement_value),
                2
            )

        valid_reps = 0

    # ------------------------------------------------------
    # PLANK
    # ------------------------------------------------------

    elif exercise == "plank":

        measurement_value = (
            last_data.get(
                "plank_duration_seconds"
            )
        )

        if measurement_value is None:

            measurement_value = (
                last_data.get(
                    "duration_seconds"
                )
            )

        if measurement_value is None:

            measurement_value = getattr(
                analyzer,
                "duration_seconds",
                0
            )

        if measurement_value is not None:

            measurement_value = round(
                float(measurement_value),
                2
            )

        valid_reps = 0

    # ------------------------------------------------------
    # VERTICAL JUMP
    # ------------------------------------------------------

    elif exercise == "vertical_jump":

        measurement_value = last_data.get(
            "jump_height_cm"
        )

        if measurement_value is None:
            measurement_value = last_data.get(
                "vertical_jump_cm"
            )

        if measurement_value is None:
            measurement_value = getattr(
                analyzer,
                "jump_height_cm",
                None
            )

        if measurement_value is not None:
            try:
                measurement_value = round(
                    float(measurement_value),
                    2
                )
            except (TypeError, ValueError):
                measurement_value = None

        valid_reps = 0

    # ======================================================
    # Extract features
    # ======================================================

    excluded_keys = {
        "test",
        "reps",
        "stage",
        "valid_posture",
        "person_detected",

        "pushup_count",
        "squat_count",
        "deadlift_reps",
        "running_50m_seconds",
        "situp_count",
        "plank_duration_seconds",
        "vertical_jump_cm",

        "elapsed_seconds",
        "duration_seconds",
    }

    features = {
        key: value
        for key, value
        in last_data.items()
        if key not in excluded_keys
    }

    # ======================================================
    # Quality information
    # ======================================================

    quality = {

        "last_stage":
            last_data.get(
                "stage"
            ),

        "last_frame_valid_posture":
            last_data.get(
                "valid_posture",
                False
            ),

        "invalid_frames":
            getattr(
                analyzer,
                "invalid_frames",
                0
            ),
    }

    if analyzer_error is not None:

        quality[
            "analyzer_error"
        ] = analyzer_error

    # ======================================================
    # Return CV result
    # ======================================================

    return {

        "test":
            exercise,

        "timestamp":
            datetime.now().isoformat(),

        "status":
            status,

        "input_source":
            "video",

        "person_detected":
            person_frames > 0,

        "frames_processed":
            frames_processed,

        "person_frames":
            person_frames,

        "measurement": {
            measurement_field:
                measurement_value
        },

        "features":
            features,

        "quality":
            quality,

        "valid_reps":
            valid_reps,
    }


# ==========================================================
# Individual helper functions
# ==========================================================


def process_pushup_video(
    video_path: str
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="pushup",
    )


def process_squat_video(
    video_path: str
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="squat",
    )


def process_deadlift_video(
    video_path: str
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="deadlift",
    )


def process_running_video(
    video_path: str
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="running",
    )


def process_situp_video(
    video_path: str
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="situp",
    )


def process_plank_video(
    video_path: str
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="plank",
    )


def process_vertical_jump_video(
    video_path: str,
    athlete_height_cm: float,
) -> dict:

    return process_exercise_video(
        video_path=video_path,
        exercise="vertical_jump",
        athlete_height_cm=athlete_height_cm,
    )