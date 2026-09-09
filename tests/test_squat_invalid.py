import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from squat import SquatAnalyzer


def test_missing_landmarks():
    analyzer = SquatAnalyzer()

    landmarks = [None] * 10

    result = analyzer.analyze(landmarks)

    assert result["valid"] is False
    assert result["reps"] == 0
    assert result["knee_angle"] is None


if __name__ == "__main__":
    test_missing_landmarks()

    print("Squat invalid landmark test passed!")