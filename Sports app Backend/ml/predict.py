"""Validate one athlete and return a backend-friendly talent assessment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml import MODEL_VERSION
from ml.dataset import (
    ALLOWED_GENDERS,
    INPUT_FEATURES,
    INTEGER_COLUMNS,
    VALID_NUMERIC_RANGES,
)
from ml.model import load_model, predict_with_probabilities
from ml.train import DEFAULT_METADATA_PATH, DEFAULT_MODEL_PATH


ASSESSMENT_WARNING = (
    "AI-assisted demonstration only; this is not an official selection decision. "
    "Use qualified coaches and approved, age-appropriate protocols. Deadlift "
    "assessments must use a safe standard load under trained supervision."
)


def _is_blank(value: object) -> bool:
    """Return True for None, NaN, or an empty text value."""

    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def validate_prediction_input(athlete_data: dict[str, Any]) -> pd.DataFrame:
    """Validate one input dictionary and return a one-row DataFrame."""

    if not isinstance(athlete_data, dict):
        raise TypeError("athlete_data must be a dictionary of input fields.")

    missing_fields = [
        field
        for field in INPUT_FEATURES
        if field not in athlete_data or _is_blank(athlete_data[field])
    ]
    if missing_fields:
        raise ValueError(
            "Missing required input field(s): " + ", ".join(missing_fields)
        )

    clean_data: dict[str, Any] = {}
    errors: list[str] = []

    gender = str(athlete_data["gender"]).strip().title()
    if gender not in ALLOWED_GENDERS:
        errors.append(
            f"gender must be one of {ALLOWED_GENDERS}; received "
            f"'{athlete_data['gender']}'"
        )
    else:
        clean_data["gender"] = gender

    for field, (minimum, maximum) in VALID_NUMERIC_RANGES.items():
        raw_value = athlete_data[field]
        if isinstance(raw_value, bool):
            errors.append(f"{field} must be numeric, not true/false")
            continue

        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            errors.append(f"{field} must be a number; received '{raw_value}'")
            continue

        if not np.isfinite(value):
            errors.append(f"{field} must be a finite number")
            continue
        if not minimum <= value <= maximum:
            errors.append(
                f"{field} must be between {minimum} and {maximum}; received {value}"
            )
            continue
        if field in INTEGER_COLUMNS and not value.is_integer():
            errors.append(f"{field} must be a whole number; received {value}")
            continue

        clean_data[field] = int(value) if field in INTEGER_COLUMNS else value

    if errors:
        raise ValueError("Invalid input: " + "; ".join(errors))

    # Reorder columns to exactly match the model's training contract.
    return pd.DataFrame([{field: clean_data[field] for field in INPUT_FEATURES}])


def recommend_sport(athlete: dict[str, Any]) -> str:
    """Recommend a sport using transparent, editable demonstration rules.

    This is a rule system, not a second Random Forest prediction. Thresholds
    are illustrative and must be replaced by official, age-aware benchmarks.
    """

    fast_running = float(athlete["running_50m_seconds"]) <= 7.2
    strong_upper_body = float(athlete["pushup_count"]) >= 35
    strong_lower_body = float(athlete["squat_count"]) >= 45
    strong_deadlift = float(athlete["deadlift_reps"]) >= 12
    strong_core = (
        float(athlete["situp_count"]) >= 40
        and float(athlete["plank_duration_seconds"]) >= 90
    )
    explosive_jump = float(athlete["vertical_jump_cm"]) >= 50

    if fast_running and strong_core:
        return "Athletics"
    if explosive_jump and strong_lower_body:
        return "Basketball or Volleyball"
    if fast_running and strong_lower_body:
        return "Football or Hockey"
    if strong_deadlift and strong_upper_body and strong_lower_body:
        return "Weightlifting or Wrestling"
    if strong_core and explosive_jump:
        return "Gymnastics or Combat Sports"
    return "General Multi-Sport Development"


def analyse_strengths(athlete: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return strengths and improvement areas from editable demo thresholds."""

    strengths: list[str] = []
    needs_improvement: list[str] = []

    if float(athlete["pushup_count"]) >= 35:
        strengths.append("Upper-Body Strength")
    elif float(athlete["pushup_count"]) < 20:
        needs_improvement.append("Upper-Body Strength")

    if float(athlete["squat_count"]) >= 45:
        strengths.append("Lower-Body Endurance")
    elif float(athlete["squat_count"]) < 25:
        needs_improvement.append("Lower-Body Endurance")

    if float(athlete["deadlift_reps"]) >= 12:
        strengths.append("Deadlift Strength")
    elif float(athlete["deadlift_reps"]) < 6:
        needs_improvement.append("Deadlift Strength")

    if float(athlete["running_50m_seconds"]) <= 7.2:
        strengths.append("Running Speed")
    elif float(athlete["running_50m_seconds"]) > 8.5:
        needs_improvement.append("Running Speed")

    strong_core = (
        float(athlete["situp_count"]) >= 40
        and float(athlete["plank_duration_seconds"]) >= 90
    )
    weak_core = (
        float(athlete["situp_count"]) < 25
        or float(athlete["plank_duration_seconds"]) < 45
    )
    if strong_core:
        strengths.append("Core Endurance")
    elif weak_core:
        needs_improvement.append("Core Endurance")

    if float(athlete["vertical_jump_cm"]) >= 50:
        strengths.append("Explosive Power")
    elif float(athlete["vertical_jump_cm"]) < 35:
        needs_improvement.append("Explosive Power")

    if not strengths:
        strengths.append("Developing overall fitness")
    if not needs_improvement:
        needs_improvement.append("Maintain balanced training")

    return strengths, needs_improvement


def _read_model_version(metadata_path: str | Path) -> str:
    """Read the model version without failing prediction on metadata issues."""

    metadata_path = Path(metadata_path)
    if not metadata_path.exists():
        return MODEL_VERSION
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        return str(metadata.get("version", MODEL_VERSION))
    except (OSError, json.JSONDecodeError, TypeError):
        return MODEL_VERSION


def predict_talent(
    athlete_data: dict[str, Any],
    model_path: str | Path = DEFAULT_MODEL_PATH,
    metadata_path: str | Path = DEFAULT_METADATA_PATH,
) -> dict[str, Any]:
    """Predict talent level and return JSON-compatible assessment details."""

    feature_frame = validate_prediction_input(athlete_data)
    model = load_model(model_path)
    talent_level, probabilities = predict_with_probabilities(model, feature_frame)
    confidence = probabilities[talent_level]
    strengths, needs_improvement = analyse_strengths(athlete_data)

    return {
        "talent_level": talent_level,
        "confidence": round(float(confidence), 4),
        "recommended_sport": recommend_sport(athlete_data),
        "strengths": strengths,
        "needs_improvement": needs_improvement,
        "model_version": _read_model_version(metadata_path),
        "warning": ASSESSMENT_WARNING,
    }


def main() -> None:
    """Run a complete example with: python -m ml.predict"""

    example_athlete = {
        "age": 17,
        "gender": "Male",
        "height_cm": 172,
        "weight_kg": 62,
        "pushup_count": 35,
        "squat_count": 48,
        "deadlift_reps": 12,
        "running_50m_seconds": 7.0,
        "situp_count": 42,
        "plank_duration_seconds": 95,
        "vertical_jump_cm": 48,
    }

    print("Example input:")
    print(json.dumps(example_athlete, indent=2))
    print("\nPrediction output:")
    print(json.dumps(predict_talent(example_athlete), indent=2))


if __name__ == "__main__":
    main()
