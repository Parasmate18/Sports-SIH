from utils.angle import calculate_angle


class PullUpAnalyzer:

    def __init__(self):

        self.reps = 0
        self.stage = "DOWN"

    def analyze(self, landmarks):

        # Left side landmarks
        shoulder = landmarks[11]
        elbow = landmarks[13]
        wrist = landmarks[15]

        angle = calculate_angle(
            (shoulder.x, shoulder.y),
            (elbow.x, elbow.y),
            (wrist.x, wrist.y)
        )

        # Arms extended = DOWN position
        if angle > 160:

            if self.stage == "UP":
                self.reps += 1

            self.stage = "DOWN"

        # Arms bent = UP position
        elif angle < 80:

            self.stage = "UP"

        return {
            "test": "pullup",
            "reps": self.reps,
            "elbow_angle": round(angle, 2),
            "stage": self.stage
        }
