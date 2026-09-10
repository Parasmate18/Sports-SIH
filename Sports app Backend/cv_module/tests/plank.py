from cv_module.utils.geometry import (
    calculate_angle,
    choose_side,
    line_angle_from_horizontal,
    valid_angle,
)


class PlankAnalyzer:
    """
    Measures the duration for which the athlete maintains
    a valid plank position.
    """

    def __init__(self):
        self.duration_seconds = 0.0
        self.last_ts = None
        self.stage = "WAITING"
        self.invalid_frames = 0

    def analyze(self, landmarks, timestamp_ms=None):

        pts = choose_side(
            landmarks,
            [11, 23, 27],
            [12, 24, 28],
            threshold=0.35
        )

        ts = int(timestamp_ms or 0)

        if not pts:
            self.invalid_frames += 1
            self.last_ts = ts

            return {
                "test": "plank",
                "duration_seconds": round(
                    self.duration_seconds, 2
                ),
                "stage": "LANDMARKS_NOT_VISIBLE",
                "valid_posture": False
            }

        shoulder, hip, ankle = pts

        body_angle = calculate_angle(
            shoulder,
            hip,
            ankle
        )

        horizontal = line_angle_from_horizontal(
            shoulder,
            ankle
        )

        # Valid plank:
        # body should be reasonably straight and close
        # to horizontal.
        valid = (
            valid_angle(body_angle)
            and body_angle >= 150
            and horizontal <= 35
        )

        # --------------------------------------------------
        # TIME ACCUMULATION
        # --------------------------------------------------

        if self.last_ts is not None and valid:

            if ts >= self.last_ts:

                delta = (
                    ts - self.last_ts
                ) / 1000.0

                # Prevent a bad camera timestamp from
                # adding a huge amount of time.
                self.duration_seconds += min(
                    delta,
                    0.20
                )

        self.last_ts = ts

        # --------------------------------------------------
        # STAGE
        # --------------------------------------------------

        if valid:
            self.stage = "HOLD"
        else:
            self.stage = "INVALID"
            self.invalid_frames += 1

        return {
            "test": "plank",
            "duration_seconds": round(
                self.duration_seconds,
                2
            ),
            "body_angle": (
                round(body_angle, 2)
                if valid_angle(body_angle)
                else None
            ),
            "body_horizontal_angle": round(
                horizontal,
                2
            ),
            "stage": self.stage,
            "valid_posture": valid
        }
    