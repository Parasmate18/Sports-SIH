from __future__ import annotations

from statistics import median

from cv_module.utils.geometry import choose_side, distance


class VerticalJumpAnalyzer:
    """
    Estimates vertical jump height using single-camera pose tracking.

    Athlete height is used for approximate pixel-to-centimeter calibration.

    This is intended for demonstration/testing and should not be treated
    as an official measurement.
    """

    CALIBRATION_FRAMES = 20
    MIN_BODY_LENGTH = 0.08
    AIRBORNE_THRESHOLD_CM = 5.0
    LANDING_TOLERANCE_NORM = 0.04

    def __init__(self, athlete_height_cm: float):
        self.height_cm = float(athlete_height_cm)

        if self.height_cm <= 0:
            raise ValueError("athlete_height_cm must be greater than 0")

        self.baseline_body_px_norm = None
        self.baseline_hip_y = None

        self.peak_hip_y = None
        self.peak_jump_cm = 0.0

        self.jump_height_cm = 0.0

        self.stage = "CALIBRATING"
        self.calibration_samples = []

        self.was_airborne = False
        self.invalid_frames = 0

    def analyze(self, landmarks, timestamp_ms=None):

        # --------------------------------------------------
        # LANDMARK EXTRACTION
        # --------------------------------------------------

        pts = choose_side(
            landmarks,
            [11, 23, 27],   # left shoulder, hip, ankle
            [12, 24, 28],   # right shoulder, hip, ankle
            threshold=0.35,
        )

        if not pts:
            self.invalid_frames += 1

            return {
                "test": "vertical_jump",
                "jump_height_cm": round(self.jump_height_cm, 2),
                "peak_jump_cm": round(self.peak_jump_cm, 2),
                "stage": "LANDMARKS_NOT_VISIBLE",
                "calibrated": self.baseline_hip_y is not None,
                "valid_posture": False,
            }

        shoulder, hip, ankle = pts

        body_len = distance(
            shoulder,
            ankle,
        )

        if body_len <= self.MIN_BODY_LENGTH:
            self.invalid_frames += 1

            return {
                "test": "vertical_jump",
                "jump_height_cm": round(self.jump_height_cm, 2),
                "peak_jump_cm": round(self.peak_jump_cm, 2),
                "stage": "INVALID",
                "calibrated": self.baseline_hip_y is not None,
                "valid_posture": False,
            }

        hip_y = float(hip.y)

        # --------------------------------------------------
        # CALIBRATION
        # --------------------------------------------------

        if len(self.calibration_samples) < self.CALIBRATION_FRAMES:

            self.calibration_samples.append(
                (body_len, hip_y)
            )

            if len(self.calibration_samples) == self.CALIBRATION_FRAMES:

                body_lengths = [
                    sample[0]
                    for sample in self.calibration_samples
                ]

                hip_positions = [
                    sample[1]
                    for sample in self.calibration_samples
                ]

                self.baseline_body_px_norm = median(body_lengths)
                self.baseline_hip_y = median(hip_positions)

                self.peak_hip_y = self.baseline_hip_y

                self.stage = "READY"

            return {
                "test": "vertical_jump",
                "jump_height_cm": 0.0,
                "peak_jump_cm": 0.0,
                "stage": self.stage,
                "calibrated": (
                    len(self.calibration_samples)
                    >= self.CALIBRATION_FRAMES
                ),
                "calibration_progress": len(
                    self.calibration_samples
                ),
                "valid_posture": True,
            }

        # --------------------------------------------------
        # SCALE CONVERSION
        # --------------------------------------------------

        estimated_height_norm = (
            self.baseline_body_px_norm / 0.80
        )

        cm_per_norm = (
            self.height_cm
            / max(estimated_height_norm, 1e-6)
        )

        # --------------------------------------------------
        # TRACK HIGHEST HIP POSITION
        # --------------------------------------------------

        if self.peak_hip_y is None:
            self.peak_hip_y = hip_y

        if hip_y < self.peak_hip_y:
            self.peak_hip_y = hip_y

        rise_norm = max(
            0.0,
            self.baseline_hip_y - self.peak_hip_y,
        )

        current_peak_estimate_cm = (
            rise_norm * cm_per_norm
        )

        # Save the maximum estimate permanently.
        if current_peak_estimate_cm > self.peak_jump_cm:
            self.peak_jump_cm = current_peak_estimate_cm

        # --------------------------------------------------
        # AIRBORNE DETECTION
        # --------------------------------------------------

        current_hip_rise_norm = max(
            0.0,
            self.baseline_hip_y - hip_y,
        )

        current_hip_rise_cm = (
            current_hip_rise_norm * cm_per_norm
        )

        if (
            not self.was_airborne
            and current_hip_rise_cm
            >= self.AIRBORNE_THRESHOLD_CM
        ):
            self.was_airborne = True
            self.stage = "AIRBORNE"

        # --------------------------------------------------
        # LANDING DETECTION
        # --------------------------------------------------

        if self.was_airborne:

            distance_from_baseline = abs(
                hip_y - self.baseline_hip_y
            )

            if (
                distance_from_baseline
                <= self.LANDING_TOLERANCE_NORM
            ):

                # Store the PEAK estimate reached during jump,
                # not the current landing estimate.
                self.jump_height_cm = max(
                    self.jump_height_cm,
                    self.peak_jump_cm,
                )

                self.stage = "LANDED"
                self.was_airborne = False

                # Reset tracking for a possible second jump.
                self.peak_hip_y = self.baseline_hip_y
                self.peak_jump_cm = 0.0

        # While still airborne, expose the current best estimate.
        elif self.peak_jump_cm > 0:

            self.jump_height_cm = max(
                self.jump_height_cm,
                self.peak_jump_cm,
            )

        return {
            "test": "vertical_jump",
            "jump_height_cm": round(
                self.jump_height_cm,
                2
            ),
            "peak_jump_cm": round(
                self.peak_jump_cm,
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