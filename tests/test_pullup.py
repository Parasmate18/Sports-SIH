import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pullup


class FakeLandmark:
    def __init__(self):
        self.x = 0
        self.y = 0


def create_landmarks():
    return [FakeLandmark() for _ in range(33)]


def test_initial_state():
    analyzer = pullup.PullUpAnalyzer()

    assert analyzer.reps == 0
    assert analyzer.stage == "DOWN"


def test_pullup_rep_count():
    analyzer = pullup.PullUpAnalyzer()
    landmarks = create_landmarks()

    # UP position: elbow angle < 80°
    pullup.calculate_angle = lambda a, b, c: 70
    analyzer.analyze(landmarks)

    # DOWN position: elbow angle > 160° → Rep 1
    pullup.calculate_angle = lambda a, b, c: 170
    analyzer.analyze(landmarks)

    # UP position
    pullup.calculate_angle = lambda a, b, c: 70
    analyzer.analyze(landmarks)

    # DOWN position → Rep 2
    pullup.calculate_angle = lambda a, b, c: 170
    analyzer.analyze(landmarks)

    assert analyzer.reps == 2


def test_no_rep_when_staying_down():
    analyzer = pullup.PullUpAnalyzer()
    landmarks = create_landmarks()

    pullup.calculate_angle = lambda a, b, c: 170

    analyzer.analyze(landmarks)
    analyzer.analyze(landmarks)
    analyzer.analyze(landmarks)

    assert analyzer.reps == 0


if __name__ == "__main__":
    test_initial_state()
    test_pullup_rep_count()
    test_no_rep_when_staying_down()

    print("All pull-up tests passed!")