import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pullup import PullUpAnalyzer


def test_missing_landmarks():
    analyzer = PullUpAnalyzer()

    landmarks = [None] * 10

    result = analyzer.analyze(landmarks)

    assert result["valid"] is False
    assert result["reps"] == 0
    assert result["elbow_angle"] is None


if __name__ == "__main__":
    test_missing_landmarks()

    print("Pull-up invalid landmark test passed!")