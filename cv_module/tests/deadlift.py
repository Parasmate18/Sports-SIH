from cv_module.utils.geometry import (
    calculate_angle,
    line_angle_from_vertical,
    valid_angle,
)


class DeadliftAnalyzer:
    """
    Counts a controlled deadlift hinge/lift cycle.

    This version is designed to be more tolerant of video footage where
    the wrist/hand or one side of the body has lower MediaPipe visibility.

    Safety:
    Use only an expert-approved standard load with trained supervision.
    """

    def __init__(self):
        self.reps = 0
        self.stage = 'WAITING'
        self.invalid_frames = 0

        # Upright position
        self.UP_KNEE_ANGLE = 150
        self.UP_HIP_ANGLE = 145
        self.UP_TORSO_LEAN = 35

        # Bottom / hinge position
        self.DOWN_HIP_MIN = 70
        self.DOWN_HIP_MAX = 140
        self.DOWN_KNEE_MIN = 70
        self.DOWN_KNEE_MAX = 165
        self.DOWN_TORSO_LEAN = 20

    def _get_best_side(self, landmarks):
        """
        Select the better visible body side.

        Deadlift counting only needs:
            shoulder, hip, knee, ankle

        We intentionally do NOT require the wrist because the barbell
        can hide the wrist/hand from MediaPipe.
        """

        left_ids = [11, 23, 25, 27]
        right_ids = [12, 24, 26, 28]

        candidates = []

        for side_name, ids in [
            ('LEFT', left_ids),
            ('RIGHT', right_ids),
        ]:
            points = [landmarks[i] for i in ids]

            visibility_scores = [
                float(getattr(p, 'visibility', 1.0) or 0.0)
                for p in points
            ]

            # Number of landmarks that are reasonably visible
            visible_count = sum(
                score >= 0.25
                for score in visibility_scores
            )

            average_visibility = (
                sum(visibility_scores) / len(visibility_scores)
            )

            # Need at least 3 of the 4 important landmarks.
            if visible_count >= 3:
                candidates.append(
                    (
                        average_visibility,
                        visible_count,
                        side_name,
                        points,
                    )
                )

        if not candidates:
            return None

        # Prefer:
        # 1. more visible landmarks
        # 2. higher average visibility
        candidates.sort(
            key=lambda x: (x[1], x[0]),
            reverse=True
        )

        _, _, side_name, points = candidates[0]

        return side_name, points

    def analyze(self, landmarks, timestamp_ms=None):

        selected = self._get_best_side(landmarks)

        if selected is None:
            self.invalid_frames += 1

            return {
                'test': 'deadlift',
                'reps': self.reps,
                'stage': 'LANDMARKS_NOT_VISIBLE',
                'valid_posture': False,
            }

        side_name, pts = selected

        shoulder, hip, knee, ankle = pts

        # --------------------------------------------------
        # JOINT ANGLES
        # --------------------------------------------------

        hip_angle = calculate_angle(
            shoulder,
            hip,
            knee
        )

        knee_angle = calculate_angle(
            hip,
            knee,
            ankle
        )

        # Torso lean relative to vertical
        torso_lean = abs(
            float(
                line_angle_from_vertical(
                    hip,
                    shoulder
                )
            )
        )

        if not (
            valid_angle(hip_angle)
            and valid_angle(knee_angle)
        ):
            self.invalid_frames += 1

            return {
                'test': 'deadlift',
                'reps': self.reps,
                'stage': 'INVALID_POSTURE',
                'valid_posture': False,
            }

        # --------------------------------------------------
        # UPRIGHT POSITION
        # --------------------------------------------------

        upright = (
            knee_angle >= self.UP_KNEE_ANGLE
            and hip_angle >= self.UP_HIP_ANGLE
            and torso_lean <= self.UP_TORSO_LEAN
        )

        # --------------------------------------------------
        # LOWER / HINGE POSITION
        # --------------------------------------------------

        bottom = (
            self.DOWN_HIP_MIN <= hip_angle <= self.DOWN_HIP_MAX
            and self.DOWN_KNEE_MIN <= knee_angle <= self.DOWN_KNEE_MAX
            and torso_lean >= self.DOWN_TORSO_LEAN
        )

        # --------------------------------------------------
        # STATE MACHINE
        # --------------------------------------------------

        if bottom:

            # Athlete has reached the lowered position.
            self.stage = 'DOWN'

        elif upright:

            # DOWN -> UP = one completed deadlift repetition.
            if self.stage == 'DOWN':
                self.reps += 1

            self.stage = 'UP'

        # --------------------------------------------------
        # RETURN DATA
        # --------------------------------------------------

        return {
            'test': 'deadlift',
            'reps': self.reps,
            'hip_angle': round(hip_angle, 2),
            'knee_angle': round(knee_angle, 2),
            'torso_lean': round(torso_lean, 2),
            'side': side_name,
            'stage': self.stage,
            'valid_posture': upright or bottom,
        }