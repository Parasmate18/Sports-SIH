import math


class RunningAnalyzer:

    def __init__(self):

        self.start_x = None
        self.start_time = None
        self.steps = 0
        self.last_leg_state = None

    def analyze(self, landmarks, timestamp_ms):

        # Left and right ankle
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]

        # Hip position
        left_hip = landmarks[23]
        right_hip = landmarks[24]

        hip_x = (
            left_hip.x +
            right_hip.x
        ) / 2

        hip_y = (
            left_hip.y +
            right_hip.y
        ) / 2

        # Starting position
        if self.start_x is None:

            self.start_x = hip_x

        # Horizontal displacement
        displacement = abs(
            hip_x - self.start_x
        )

        # Leg movement
        ankle_difference = abs(
            left_ankle.y -
            right_ankle.y
        )

        current_leg_state = (
            ankle_difference > 0.08
        )

        # Simple step detection
        if (
            self.last_leg_state is not None
            and current_leg_state != self.last_leg_state
        ):

            self.steps += 1

        self.last_leg_state = current_leg_state

        return {
            "test": "running",
            "displacement": round(
                displacement,
                3
            ),
            "steps": self.steps,
            "hip_y": round(
                hip_y,
                3
            )
        }
