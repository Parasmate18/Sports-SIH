from cv_module.utils.geometry import (
    calculate_angle,
    choose_side,
    line_angle_from_horizontal,
    valid_angle,
)


class SitUpAnalyzer:
    """
    Counts sit-ups using side-view pose landmarks.

    Movement:
        DOWN -> UP -> DOWN = 1 repetition

    Designed to be tolerant of normal camera/video variations.
    """

    def __init__(self):
        self.reps = 0
        self.stage = 'WAITING'
        self.invalid_frames = 0

        # Tolerant thresholds for video/webcam testing
        self.DOWN_BODY_ANGLE = 105
        self.UP_BODY_ANGLE = 80

        # Wider acceptable knee range
        self.MIN_KNEE_ANGLE = 30
        self.MAX_KNEE_ANGLE = 175

        # Torso does not need to be perfectly horizontal
        self.MAX_DOWN_TORSO_ANGLE = 60

    def analyze(self, landmarks, timestamp_ms=None):

        # Try the side with the better visibility.
        # Shoulder -> Hip -> Knee -> Ankle
        pts = choose_side(
            landmarks,
            [11, 23, 25, 27],
            [12, 24, 26, 28],
            threshold=0.35,
        )

        if not pts:
            self.invalid_frames += 1

            return {
                'test': 'situp',
                'reps': self.reps,
                'stage': 'LANDMARKS_NOT_VISIBLE',
                'valid_posture': False,
            }

        shoulder, hip, knee, ankle = pts

        # --------------------------------------------------
        # Calculate angles
        # --------------------------------------------------

        body_angle = calculate_angle(
            shoulder,
            hip,
            knee,
        )

        knee_angle = calculate_angle(
            hip,
            knee,
            ankle,
        )

        torso_horizontal = abs(
            float(
                line_angle_from_horizontal(
                    hip,
                    shoulder,
                )
            )
        )

        # --------------------------------------------------
        # Check that angles are usable
        # --------------------------------------------------

        if not (
            valid_angle(body_angle)
            and valid_angle(knee_angle)
        ):
            self.invalid_frames += 1

            return {
                'test': 'situp',
                'reps': self.reps,
                'stage': 'INVALID_POSTURE',
                'valid_posture': False,
            }

        # --------------------------------------------------
        # Basic knee validation
        #
        # We intentionally use a very wide range because
        # different videos/camera positions can produce
        # slightly different knee angles.
        # --------------------------------------------------

        knee_valid = (
            self.MIN_KNEE_ANGLE
            <= knee_angle
            <= self.MAX_KNEE_ANGLE
        )

        if not knee_valid:
            self.invalid_frames += 1

            return {
                'test': 'situp',
                'reps': self.reps,
                'body_angle': round(body_angle, 2),
                'knee_angle': round(knee_angle, 2),
                'torso_horizontal_angle': round(
                    torso_horizontal, 2
                ),
                'stage': 'INVALID_POSTURE',
                'valid_posture': False,
            }

        # --------------------------------------------------
        # DOWN POSITION
        #
        # Athlete is reclined and torso is relatively close
        # to horizontal.
        # --------------------------------------------------

        down_position = (
            body_angle >= self.DOWN_BODY_ANGLE
            and torso_horizontal <= self.MAX_DOWN_TORSO_ANGLE
        )

        # --------------------------------------------------
        # UP POSITION
        #
        # Athlete has brought the torso toward the knees.
        # --------------------------------------------------

        up_position = (
            body_angle <= self.UP_BODY_ANGLE
        )

        # --------------------------------------------------
        # STATE MACHINE
        # --------------------------------------------------

        if down_position:

            # If athlete completed the UP movement and
            # returned DOWN, count one repetition.
            if self.stage == 'UP':
                self.reps += 1

            self.stage = 'DOWN'

        elif up_position:

            # Only allow UP after starting/being DOWN.
            if self.stage in {'DOWN', 'WAITING'}:
                self.stage = 'UP'

        # Otherwise keep the previous stage.
        # This prevents noisy frames from resetting
        # the movement.

        return {
            'test': 'situp',
            'reps': self.reps,
            'body_angle': round(body_angle, 2),
            'knee_angle': round(knee_angle, 2),
            'torso_horizontal_angle': round(
                torso_horizontal, 2
            ),
            'stage': self.stage,
            'valid_posture': down_position or up_position,
        }