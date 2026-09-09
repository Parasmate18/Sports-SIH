import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import situp


class FakeLandmark:
    def __init__(self):
        self.x = 0
        self.y = 0


def create_landmarks():
    return [FakeLandmark() for _ in range(33)]


def test_initial_state():
    analyzer = situp.SitUpAnalyzer()

    assert analyzer.reps == 0
    assert analyzer.stage == "DOWN"


def test_situp_rep_count():
    analyzer = situp.SitUpAnalyzer()
    landmarks = create_landmarks()

    # DOWN position: body angle > 110°
    situp.calculate_angle = lambda a, b, c: 120
    analyzer.analyze(landmarks)

    # UP position: body angle < 70° → Rep 1
    situp.calculate_angle = lambda a, b, c: 60
    analyzer.analyze(landmarks)

    # DOWN position
    situp.calculate_angle = lambda a, b, c: 120
    analyzer.analyze(landmarks)

    # UP position → Rep 2
    situp.calculate_angle = lambda a, b, c: 60
    analyzer.analyze(landmarks)

    assert analyzer.reps == 2


def test_no_rep_when_staying_down():
    analyzer = situp.SitUpAnalyzer()
    landmarks = create_landmarks()

    situp.calculate_angle = lambda a, b, c: 120

    analyzer.analyze(landmarks)
    analyzer.analyze(landmarks)
    analyzer.analyze(landmarks)

    assert analyzer.reps == 0


if __name__ == "__main__":
    test_initial_state()
    test_situp_rep_count()
    test_no_rep_when_staying_down()

    print("All sit-up tests passed!")