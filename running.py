class RunningAnalyzer:

    def __init__(self):
        self.start_x = None
        self.start_time = None
        self.steps = 0
        self.last_leg_state = None

    def analyze(self, landmarks, timestamp_ms):

        # Check required landmarks
        if landmarks is None or len(landmarks) <= 28:
            return {
                "test": "running",
                "displacement": 0,
                "steps": self.steps,
                "hip_y": 0,
                "valid": False
            }

        left_ankle = landmarks[27]
        right_ankle = landmarks[28]
        left_hip = landmarks[23]
        right_hip = landmarks[24]

        # Check landmark values
        if (left_ankle is None or right_ankle is None or
                left_hip is None or right_hip is None):
            return {
                "test": "running",
                "displacement": 0,
                "steps": self.steps,
                "hip_y": 0,
                "valid": False
            }

        hip_x = (left_hip.x + right_hip.x) / 2
        hip_y = (left_hip.y + right_hip.y) / 2

        if self.start_x is None:
            self.start_x = hip_x

        displacement = abs(hip_x - self.start_x)

        ankle_difference = abs(left_ankle.y - right_ankle.y)
        current_leg_state = ankle_difference > 0.08

        if (self.last_leg_state is not None and
                current_leg_state != self.last_leg_state):
            self.steps += 1

        self.last_leg_state = current_leg_state

        return {
            "test": "running",
            "displacement": round(displacement, 3),
            "steps": self.steps,
            "hip_y": round(hip_y, 3),
            "valid": True
        }