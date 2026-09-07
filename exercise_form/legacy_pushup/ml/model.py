"""Create, save, load and use the exercise-quality model."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from ml.dataset import FEATURE_COLUMNS
from ml.preprocessing import build_preprocessor, validate_features


def create_model(random_state: int = 42) -> Pipeline:
    """Return the complete preprocessing + classification pipeline."""
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
    output_path: str | Path,
    metrics: Dict[str, float] | None = None,
) -> Path:
    """Save the model together with its feature contract and metadata."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "model_version": "1.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics or {},
    }
    joblib.dump(bundle, output_path)
    return output_path


def load_model(model_path: str | Path) -> Dict[str, Any]:
    """Load and validate a saved model bundle."""
    bundle = joblib.load(model_path)
    required = {"model", "feature_columns", "model_version"}
    if not required.issubset(bundle):
        raise ValueError("Invalid model bundle.")
    return bundle


def predict_exercise(
    feature_values: Dict[str, float],
    model_path: str | Path = "artifacts/exercise_model.joblib",
    uncertain_threshold: float = 0.65,
) -> Dict[str, Any]:
    """Predict one repetition and return a backend-friendly dictionary."""
    bundle = load_model(model_path)
    features = validate_features(pd.DataFrame([feature_values]))
    model = bundle["model"]

    probabilities = model.predict_proba(features)[0]
    classes = list(model.classes_)
    best_index = int(probabilities.argmax())
    predicted_label = str(classes[best_index])
    confidence = float(probabilities[best_index])

    correct_probability = (
        float(probabilities[classes.index("correct")]) if "correct" in classes else 0.0
    )
    output_label = predicted_label if confidence >= uncertain_threshold else "uncertain"

    return {
        "label": output_label,
        "raw_prediction": predicted_label,
        "confidence": round(confidence, 4),
        "form_score": round(correct_probability * 100, 2),
        "model_version": bundle["model_version"],
    }

