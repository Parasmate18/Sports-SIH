import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pushup import PushUpAnalyzer


class FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def create_landmarks(elbow_angle):
    landmarks = [FakeLandmark(0, 0) for _ in range(33)]

    shoulder = (0, 0)
    elbow = (1, 0)

    # Create the wrist position using the required angle
    radians = math.radians(180 - elbow_angle)
    wrist = (
        1 + math.cos(radians),
        math.sin(radians)
    )

    landmarks[12] = FakeLandmark(*shoulder)
    landmarks[14] = FakeLandmark(*elbow)
    landmarks[16] = FakeLandmark(*wrist)

    return landmarks


def test_initial_state():
    analyzer = PushUpAnalyzer()

    assert analyzer.reps == 0
    assert analyzer.stage == "UP"


def test_pushup_rep_count():
    analyzer = PushUpAnalyzer()

    # UP position
    analyzer.analyze(create_landmarks(180))

    # DOWN position
    analyzer.analyze(create_landmarks(80))

    # UP position
    analyzer.analyze(create_landmarks(180))

    # DOWN position
    analyzer.analyze(create_landmarks(80))

    assert analyzer.reps == 2


def test_no_rep_when_staying_up():
    analyzer = PushUpAnalyzer()

    analyzer.analyze(create_landmarks(180))
    analyzer.analyze(create_landmarks(180))
    analyzer.analyze(create_landmarks(180))

    assert analyzer.reps == 0


if __name__ == "__main__":
    test_initial_state()
    test_pushup_rep_count()
    test_no_rep_when_staying_up()

    print("All push-up tests passed!")