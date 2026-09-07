from cv_module.utils.geometry import (
    calculate_angle,
    choose_side,
    line_angle_from_horizontal,
    valid_angle,
)


class PushUpAnalyzer:
    def __init__(self):
        self.reps = 0
        self.stage = 'WAITING'
        self.invalid_frames = 0

        # More tolerant push-up thresholds
        self.DOWN_ANGLE = 110
        self.UP_ANGLE = 150

        # Body-position tolerance
        self.MIN_BODY_ANGLE = 145
        self.MAX_HORIZONTAL_ANGLE = 45

    def analyze(self, landmarks, timestamp_ms=None):

        # Try either side of the body
        pts = choose_side(
            landmarks,
            [11, 13, 15, 23, 27],   # left shoulder, elbow, wrist, hip, ankle
            [12, 14, 16, 24, 28]    # right shoulder, elbow, wrist, hip, ankle
        )

        if not pts:
            self.invalid_frames += 1

            return {
                'test': 'pushup',
                'reps': self.reps,
                'stage': 'LANDMARKS_NOT_VISIBLE',
                'valid_posture': False
            }

        shoulder, elbow, wrist, hip, ankle = pts

        # Calculate important angles
        elbow_angle = calculate_angle(
            shoulder,
            elbow,
            wrist
        )

        body_angle = calculate_angle(
            shoulder,
            hip,
            ankle
        )

        body_horizontal = line_angle_from_horizontal(
            shoulder,
            ankle
        )

        # Make sure angles are usable
        if not valid_angle(elbow_angle):
            self.invalid_frames += 1

            return {
                'test': 'pushup',
                'reps': self.reps,
                'stage': 'INVALID_ELBOW_ANGLE',
                'valid_posture': False
            }

        # Normalize horizontal angle if necessary
        body_horizontal = abs(float(body_horizontal))

        # More tolerant posture check
        valid_posture = (
            valid_angle(body_angle)
            and body_angle >= self.MIN_BODY_ANGLE
            and body_horizontal <= self.MAX_HORIZONTAL_ANGLE
        )

        if not valid_posture:
            self.invalid_frames += 1

            return {
                'test': 'pushup',
                'reps': self.reps,
                'elbow_angle': round(elbow_angle, 2),
                'body_angle': round(body_angle, 2)
                if valid_angle(body_angle) else None,
                'body_horizontal_angle': round(body_horizontal, 2),
                'stage': 'INVALID_POSTURE',
                'valid_posture': False
            }

        # PUSH-UP STATE MACHINE

        # Going down
        if elbow_angle <= self.DOWN_ANGLE:
            self.stage = 'DOWN'

        # Coming back up
        elif elbow_angle >= self.UP_ANGLE:

            # Count only if we previously reached DOWN
            if self.stage == 'DOWN':
                self.reps += 1

            self.stage = 'UP'

        # Otherwise keep the previous stage
        # This prevents noisy frames from resetting the rep.

        return {
            'test': 'pushup',
            'reps': self.reps,
            'elbow_angle': round(elbow_angle, 2),
            'body_angle': round(body_angle, 2)
            if valid_angle(body_angle) else None,
            'body_horizontal_angle': round(body_horizontal, 2),
            'stage': self.stage,
            'valid_posture': True
        }