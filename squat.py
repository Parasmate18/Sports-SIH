from angle import calculate_angle


class SquatAnalyzer:

    def __init__(self):
        self.reps = 0
        self.stage = "UP"

    def analyze(self, landmarks):

        # Check required landmarks
        if landmarks is None or len(landmarks) <= 28:
            return {
                "test": "squat",
                "reps": self.reps,
                "knee_angle": None,
                "stage": self.stage,
                "valid": False
            }

        hip = landmarks[24]
        knee = landmarks[26]
        ankle = landmarks[28]

        # Check landmark values
        if hip is None or knee is None or ankle is None:
            return {
                "test": "squat",
                "reps": self.reps,
                "knee_angle": None,
                "stage": self.stage,
                "valid": False
            }

        angle = calculate_angle(
            (hip.x, hip.y),
            (knee.x, knee.y),
            (ankle.x, ankle.y)
        )

        if angle > 160:
            self.stage = "UP"

        if angle < 100 and self.stage == "UP":
            self.stage = "DOWN"
            self.reps += 1

        return {
            "test": "squat",
            "reps": self.reps,
            "knee_angle": round(angle, 2),
            "stage": self.stage,
            "valid": True
        }