from utils.angle import calculate_angle


class SitUpAnalyzer:

    def __init__(self):

        self.reps = 0
        self.stage = "DOWN"

    def analyze(self, landmarks):

        # Left side body landmarks
        shoulder = landmarks[11]
        hip = landmarks[23]
        knee = landmarks[25]

        angle = calculate_angle(
            (shoulder.x, shoulder.y),
            (hip.x, hip.y),
            (knee.x, knee.y)
        )

        # Upper body is upright
        if angle < 70:

            if self.stage == "DOWN":
                self.reps += 1

            self.stage = "UP"

        # Lying/back position
        elif angle > 110:

            self.stage = "DOWN"

        return {
            "test": "situp",
            "reps": self.reps,
            "body_angle": round(angle, 2),
            "stage": self.stage
        }
