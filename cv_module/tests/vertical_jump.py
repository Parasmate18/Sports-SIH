from __future__ import annotations

from cv_module.utils.geometry import choose_side, distance


class VerticalJumpAnalyzer:
    """
    Estimates vertical jump height using single-camera pose tracking.

    Athlete height is used for approximate pixel-to-centimeter
    calibration.

    This is intended for demonstration/testing and should not
    be treated as an official measurement.
    """

    def __init__(self, athlete_height_cm: float):
        self.height_cm = float(athlete_height_cm)

        self.baseline_body_px_norm = None
        self.baseline_hip_y = None
        self.peak_hip_y = None

        self.jump_height_cm = 0.0

        self.stage = "CALIBRATING"
        self.calibration_samples = []

        self.was_airborne = False
        self.invalid_frames = 0

    def analyze(self, landmarks, timestamp_ms=None):

        # Shoulder, hip and ankle.
        pts = choose_side(
            landmarks,
            [11, 23, 27],
            [12, 24, 28],
            threshold=0.35,
        )

        if not pts:
            self.invalid_frames += 1

            return {
                "test": "vertical_jump",
                "jump_height_cm": round(
                    self.jump_height_cm, 2
                ),
                "stage": "LANDMARKS_NOT_VISIBLE",
                "valid_posture": False,
            }

        shoulder, hip, ankle = pts

        # Normalized shoulder-to-ankle distance.
        body_len = distance(
            shoulder,
            ankle,
        )

        if body_len <= 0.08:
            self.invalid_frames += 1

            return {
                "test": "vertical_jump",
                "jump_height_cm": round(
                    self.jump_height_cm, 2
                ),
                "stage": "INVALID",
                "valid_posture": False,
            }

        hip_y = float(hip.y)

        # --------------------------------------------------
        # CALIBRATION
        # --------------------------------------------------

        # First 30 valid frames establish standing position.
        if len(self.calibration_samples) < 30:

            self.calibration_samples.append(
                (body_len, hip_y)
            )

            if len(self.calibration_samples) == 30:

                lengths = sorted(
                    x[0]
                    for x in self.calibration_samples
                )

                hips = sorted(
                    x[1]
                    for x in self.calibration_samples
                )

                middle = len(lengths) // 2

                self.baseline_body_px_norm = lengths[middle]
                self.baseline_hip_y = hips[middle]
                self.peak_hip_y = self.baseline_hip_y

                self.stage = "READY"

            return {
                "test": "vertical_jump",
                "jump_height_cm": 0.0,
                "stage": self.stage,
                "calibrated": False,
                "valid_posture": True,
            }

        # --------------------------------------------------
        # TRACK HIP MOVEMENT
        # --------------------------------------------------

        if self.peak_hip_y is None:
            self.peak_hip_y = self.baseline_hip_y

        # In an image, Y decreases when the athlete moves upward.
        if hip_y < self.peak_hip_y:
            self.peak_hip_y = hip_y

        rise_norm = max(
            0.0,
            self.baseline_hip_y - self.peak_hip_y,
        )

        # Shoulder-to-ankle is approximately 80% of standing height.
        estimated_height_norm = (
            self.baseline_body_px_norm / 0.80
        )

        cm_per_norm = (
            self.height_cm
            / max(estimated_height_norm, 1e-6)
        )

        estimate = rise_norm * cm_per_norm

        # --------------------------------------------------
        # AIRBORNE
        # --------------------------------------------------

        if estimate >= 5.0:
            self.was_airborne = True
            self.stage = "AIRBORNE"

        # --------------------------------------------------
        # LANDING
        # --------------------------------------------------

        if self.was_airborne:

            distance_from_baseline = abs(
                hip_y - self.baseline_hip_y
            )

            if distance_from_baseline < 0.035:

                self.jump_height_cm = max(
                    self.jump_height_cm,
                    estimate,
                )

                self.stage = "LANDED"
                self.was_airborne = False

                # Prepare for another jump.
                self.peak_hip_y = hip_y

        else:

            self.jump_height_cm = max(
                self.jump_height_cm,
                estimate,
            )

        return {
            "test": "vertical_jump",
            "jump_height_cm": round(
                self.jump_height_cm,
                2
            ),
            "stage": self.stage,
            "calibrated": True,
            "rise_norm": round(
                rise_norm,
                4
            ),
            "valid_posture": True,
        }