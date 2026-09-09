from angle import calculate_angle


class PullUpAnalyzer:

    def __init__(self):
        self.reps = 0
        self.stage = "DOWN"

    def analyze(self, landmarks):

        # Check required landmarks
        if landmarks is None or len(landmarks) <= 15:
            return {
                "test": "pullup",
                "reps": self.reps,
                "elbow_angle": None,
                "stage": self.stage,
                "valid": False
            }

        shoulder = landmarks[11]
        elbow = landmarks[13]
        wrist = landmarks[15]

        # Check landmark values
        if shoulder is None or elbow is None or wrist is None:
            return {
                "test": "pullup",
                "reps": self.reps,
                "elbow_angle": None,
                "stage": self.stage,
                "valid": False
            }

        angle = calculate_angle(
            (shoulder.x, shoulder.y),
            (elbow.x, elbow.y),
            (wrist.x, wrist.y)
        )

        if angle > 160:
            if self.stage == "UP":
                self.reps += 1
            self.stage = "DOWN"

        elif angle < 80:
            self.stage = "UP"

        return {
            "test": "pullup",
            "reps": self.reps,
            "elbow_angle": round(angle, 2),
            "stage": self.stage,
            "valid": True
        }