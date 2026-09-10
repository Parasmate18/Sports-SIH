"""Run a reusable example for the separate exercise-form component."""

from __future__ import annotations

import json

from .model import predict_exercise


def main() -> None:
    """Allow prediction with: python -m exercise_form.ml.predict"""

    example = {
        "exercise_type": "squat",
        "primary_joint_min_angle": 68,
        "primary_joint_max_angle": 169,
        "torso_deviation_degrees": 7,
        "range_of_motion_degrees": 101,
        "stability_score": 89,
        "movement_speed": 0.58,
        "assessment_duration_seconds": 2.1,
        "landmark_confidence": 0.95,
        "visibility_score": 0.96,
    }
    print("Exercise-form example input:")
    print(json.dumps(example, indent=2))
    print("\nExercise-form prediction:")
    print(json.dumps(predict_exercise(example), indent=2))


if __name__ == "__main__":
    main()
