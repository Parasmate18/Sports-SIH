"""Create, save, load, and use the seven-exercise form classifier."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from . import MODEL_VERSION, RANDOM_STATE
from .dataset import ALLOWED_EXERCISES, MODEL_INPUT_COLUMNS
from .preprocessing import build_preprocessor, validate_features


DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "artifacts"
    / "exercise_model.joblib"
)

FORM_WARNING = (
    "AI-assisted form feedback only; it is not medical advice or an official "
    "coach assessment. Deadlift must be performed with qualified supervision."
)


def create_model(random_state: int = RANDOM_STATE) -> Pipeline:
    """Return complete preprocessing plus a class-balanced Random Forest."""

    classifier = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    return Pipeline(
        [
            ("preprocessor", build_preprocessor()),
            ("classifier", classifier),
        ]
    )


def save_model(
    model: Pipeline,
    output_path: str | Path = DEFAULT_MODEL_PATH,
    metrics: dict[str, float] | None = None,
) -> Path:
    """Save the fitted pipeline together with its public input contract."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": model,
        "feature_columns": MODEL_INPUT_COLUMNS,
        "supported_exercises": ALLOWED_EXERCISES,
        "model_version": MODEL_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics or {},
    }
    joblib.dump(bundle, output_path)
    return output_path


def load_model(model_path: str | Path = DEFAULT_MODEL_PATH) -> dict[str, Any]:
    """Load and validate a saved multi-exercise model bundle."""

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Exercise-form model not found: {model_path}. "
            "Run 'python -m exercise_form.ml.train' first."
        )

    bundle = joblib.load(model_path)
    required = {
        "model",
        "feature_columns",
        "supported_exercises",
        "model_version",
    }
    if not isinstance(bundle, dict) or not required.issubset(bundle):
        raise ValueError("Invalid exercise-form model bundle.")
    return bundle


def predict_exercise(
    feature_values: dict[str, Any],
    model_path: str | Path = DEFAULT_MODEL_PATH,
    uncertain_threshold: float = 0.65,
) -> dict[str, Any]:
    """Predict correct/incorrect form for one supported exercise sample."""

    bundle = load_model(model_path)
    features = validate_features(pd.DataFrame([feature_values]))
    model = bundle["model"]

    probabilities = model.predict_proba(features)[0]
    classes = list(model.named_steps["classifier"].classes_)
    best_index = int(probabilities.argmax())
    predicted_label = str(classes[best_index])
    confidence = float(probabilities[best_index])
    correct_probability = (
        float(probabilities[classes.index("correct")])
        if "correct" in classes
        else 0.0
    )
    output_label = (
        predicted_label if confidence >= uncertain_threshold else "uncertain"
    )

    return {
        "exercise_type": str(features.iloc[0]["exercise_type"]),
        "label": output_label,
        "raw_prediction": predicted_label,
        "confidence": round(confidence, 4),
        "form_score": round(correct_probability * 100, 2),
        "model_version": bundle["model_version"],
        "warning": FORM_WARNING,
    }


def get_feature_importance(model: Pipeline) -> list[dict[str, float | str]]:
    """Return sorted transformed-feature importance values."""

    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]
    if not hasattr(classifier, "feature_importances_"):
        return []

    names = preprocessor.get_feature_names_out()
    rows = [
        {"feature": str(name), "importance": round(float(value), 6)}
        for name, value in zip(names, classifier.feature_importances_)
    ]
    rows.sort(key=lambda row: float(row["importance"]), reverse=True)
    return rows
