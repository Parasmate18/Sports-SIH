from angle import calculate_angle


class SitUpAnalyzer:

    def __init__(self):
        self.reps = 0
        self.stage = "DOWN"

    def analyze(self, landmarks):

        # Check required landmarks
        if landmarks is None or len(landmarks) <= 25:
            return {
                "test": "situp",
                "reps": self.reps,
                "body_angle": None,
                "stage": self.stage,
                "valid": False
            }

        shoulder = landmarks[11]
        hip = landmarks[23]
        knee = landmarks[25]

        # Check landmark values
        if shoulder is None or hip is None or knee is None:
            return {
                "test": "situp",
                "reps": self.reps,
                "body_angle": None,
                "stage": self.stage,
                "valid": False
            }

        angle = calculate_angle(
            (shoulder.x, shoulder.y),
            (hip.x, hip.y),
            (knee.x, knee.y)
        )

        if angle < 70:
            if self.stage == "DOWN":
                self.reps += 1
            self.stage = "UP"

        elif angle > 110:
            self.stage = "DOWN"

        return {
            "test": "situp",
            "reps": self.reps,
            "body_angle": round(angle, 2),
            "stage": self.stage,
            "valid": True
        }