import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from running import RunningAnalyzer


class FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def create_landmarks(left_ankle_y, right_ankle_y):
    landmarks = [FakeLandmark(0, 0) for _ in range(33)]

    # Ankles
    landmarks[27] = FakeLandmark(0, left_ankle_y)
    landmarks[28] = FakeLandmark(0, right_ankle_y)

    # Hips
    landmarks[23] = FakeLandmark(0, 0)
    landmarks[24] = FakeLandmark(0, 0)

    return landmarks


def test_initial_state():
    analyzer = RunningAnalyzer()

    assert analyzer.steps == 0
    assert analyzer.start_x is None
    assert analyzer.last_leg_state is None


def test_step_counting():
    analyzer = RunningAnalyzer()

    # State: False
    analyzer.analyze(create_landmarks(0.00, 0.00), 0)

    # State: True → 1 step
    analyzer.analyze(create_landmarks(0.00, 0.20), 33)

    # State: False → 2 steps
    analyzer.analyze(create_landmarks(0.00, 0.00), 66)

    # State: True → 3 steps
    analyzer.analyze(create_landmarks(0.00, 0.20), 99)

    assert analyzer.steps == 3


def test_no_steps_when_state_does_not_change():
    analyzer = RunningAnalyzer()

    analyzer.analyze(create_landmarks(0.00, 0.20), 0)
    analyzer.analyze(create_landmarks(0.00, 0.20), 33)
    analyzer.analyze(create_landmarks(0.00, 0.20), 66)

    assert analyzer.steps == 0


if __name__ == "__main__":
    test_initial_state()
    test_step_counting()
    test_no_steps_when_state_does_not_change()

    print("All running tests passed!")