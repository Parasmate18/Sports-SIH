"""Build, train, save, load, and inspect the talent-level model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from ml import RANDOM_STATE
from ml.preprocessing import build_preprocessor


def build_model_pipeline(random_state: int = RANDOM_STATE) -> Pipeline:
    """Return one pipeline containing preprocessing and Random Forest.

    class_weight="balanced" automatically gives more influence to classes with
    fewer records. It has little effect when the dataset is balanced and
    protects the baseline when real data later becomes imbalanced.
    """

    classifier = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", classifier),
        ]
    )


def train_model(
    model: Pipeline, features: pd.DataFrame, target: pd.Series
) -> Pipeline:
    """Fit the complete pipeline using training data only."""

    if features.empty:
        raise ValueError("Training features are empty.")
    if target.nunique() < 2:
        raise ValueError("Training data must contain at least two target classes.")
    model.fit(features, target)
    return model


def save_model(model: Pipeline, output_path: str | Path) -> Path:
    """Save the complete fitted pipeline with joblib."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    return output_path


def load_model(model_path: str | Path) -> Pipeline:
    """Load a saved pipeline and check its expected steps."""

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found at: {model_path}\n"
            "Run 'python -m ml.train' from the project root first."
        )

    model = joblib.load(model_path)
    if not isinstance(model, Pipeline):
        raise ValueError("Saved object is not a Scikit-learn Pipeline.")
    if not {"preprocessor", "classifier"}.issubset(model.named_steps):
        raise ValueError("Saved pipeline is missing required model steps.")
    return model


def predict_with_probabilities(
    model: Pipeline, athlete_features: pd.DataFrame
) -> tuple[str, dict[str, float]]:
    """Predict one athlete and return the label plus every class probability."""

    predictions = model.predict(athlete_features)
    probability_rows = model.predict_proba(athlete_features)
    classes = model.named_steps["classifier"].classes_

    probabilities = {
        str(label): float(probability)
        for label, probability in zip(classes, probability_rows[0])
    }
    return str(predictions[0]), probabilities


def get_feature_importance(
    model: Pipeline, top_n: int | None = None
) -> list[dict[str, Any]]:
    """Return sorted feature importance values when the model supports them."""

    preprocessor = model.named_steps.get("preprocessor")
    classifier = model.named_steps.get("classifier")

    if preprocessor is None or classifier is None:
        return []
    if not hasattr(classifier, "feature_importances_"):
        return []

    try:
        feature_names = preprocessor.get_feature_names_out()
    except (AttributeError, ValueError):
        return []

    importance_rows = [
        {"feature": str(name), "importance": round(float(value), 6)}
        for name, value in zip(feature_names, classifier.feature_importances_)
    ]
    importance_rows.sort(key=lambda row: row["importance"], reverse=True)

    if top_n is not None:
        if top_n < 1:
            raise ValueError("top_n must be at least 1 when provided.")
        return importance_rows[:top_n]
    return importance_rows
