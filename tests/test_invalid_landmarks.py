import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pushup import PushUpAnalyzer


def test_missing_landmarks():
    analyzer = PushUpAnalyzer()

    # Only 10 landmarks instead of the required 33
    landmarks = [None] * 10

    try:
        analyzer.analyze(landmarks)
        handled = True
    except (IndexError, AttributeError):
        handled = False

    assert handled is True


if __name__ == "__main__":
    test_missing_landmarks()

    print("Invalid landmark test passed!")