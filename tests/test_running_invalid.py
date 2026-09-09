import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from running import RunningAnalyzer


def test_missing_landmarks():
    analyzer = RunningAnalyzer()

    landmarks = [None] * 10

    result = analyzer.analyze(landmarks, 0)

    assert result["valid"] is False
    assert result["steps"] == 0
    assert result["displacement"] == 0


if __name__ == "__main__":
    test_missing_landmarks()

    print("Running invalid landmark test passed!")