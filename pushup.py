from angle import calculate_angle


class PushUpAnalyzer:

    def __init__(self):
        self.reps = 0
        self.stage = "UP"

    def analyze(self, landmarks):

        # Check that required landmarks exist
        if landmarks is None or len(landmarks) <= 16:
            return {
                "test": "pushup",
                "reps": self.reps,
                "angle": None,
                "stage": self.stage,
                "valid": False
            }

        # Check that required landmarks are usable
        shoulder = landmarks[12]
        elbow = landmarks[14]
        wrist = landmarks[16]

        if shoulder is None or elbow is None or wrist is None:
            return {
                "test": "pushup",
                "reps": self.reps,
                "angle": None,
                "stage": self.stage,
                "valid": False
            }

        angle = calculate_angle(
            (shoulder.x, shoulder.y),
            (elbow.x, elbow.y),
            (wrist.x, wrist.y)
        )

        if angle > 160:
            self.stage = "UP"

        if angle < 90 and self.stage == "UP":
            self.stage = "DOWN"
            self.reps += 1

        return {
            "test": "pushup",
            "reps": self.reps,
            "angle": round(angle, 2),
            "stage": self.stage,
            "valid": True
        }