import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import squat


class FakeLandmark:
    def __init__(self):
        self.x = 0
        self.y = 0


def create_landmarks():
    return [FakeLandmark() for _ in range(33)]


def test_initial_state():
    analyzer = squat.SquatAnalyzer()

    assert analyzer.reps == 0
    assert analyzer.stage == "UP"


def test_squat_rep_count():
    analyzer = squat.SquatAnalyzer()
    landmarks = create_landmarks()

    squat.calculate_angle = lambda a, b, c: 180
    analyzer.analyze(landmarks)

    squat.calculate_angle = lambda a, b, c: 90
    analyzer.analyze(landmarks)

    squat.calculate_angle = lambda a, b, c: 180
    analyzer.analyze(landmarks)

    squat.calculate_angle = lambda a, b, c: 90
    analyzer.analyze(landmarks)

    assert analyzer.reps == 2


def test_no_rep_when_staying_up():
    analyzer = squat.SquatAnalyzer()
    landmarks = create_landmarks()

    squat.calculate_angle = lambda a, b, c: 180

    analyzer.analyze(landmarks)
    analyzer.analyze(landmarks)
    analyzer.analyze(landmarks)

    assert analyzer.reps == 0


if __name__ == "__main__":
    test_initial_state()
    test_squat_rep_count()
    test_no_rep_when_staying_up()

    print("All squat tests passed!")