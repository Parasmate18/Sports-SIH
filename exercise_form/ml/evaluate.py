"""Evaluate the separate seven-exercise correct/incorrect form model."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from .dataset import ID_COLUMNS, TARGET_COLUMN, get_xy, load_dataset
from .model import DEFAULT_MODEL_PATH, get_feature_importance, load_model
from .preprocessing import validate_features
from .train import DEFAULT_TEST_OUTPUT_PATH


EXERCISE_FORM_DIR = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_DIR = EXERCISE_FORM_DIR / "reports"


def evaluate(
    model_path: str | Path = DEFAULT_MODEL_PATH,
    test_path: str | Path = DEFAULT_TEST_OUTPUT_PATH,
    reports_dir: str | Path = DEFAULT_REPORTS_DIR,
):
    """Evaluate the saved form model and export reports."""

    bundle = load_model(model_path)
    test_data = load_dataset(test_path)
    X_test, y_test = get_xy(test_data)
    X_test = validate_features(X_test)
    model = bundle["model"]
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "weighted_precision": float(
            precision_score(
                y_test, predictions, average="weighted", zero_division=0
            )
        ),
        "weighted_recall": float(
            recall_score(y_test, predictions, average="weighted", zero_division=0)
        ),
        "weighted_f1": float(
            f1_score(y_test, predictions, average="weighted", zero_division=0)
        ),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "feature_importance": get_feature_importance(model),
        "warning": (
            "Synthetic demonstration form data only; metrics do not establish "
            "real-world exercise-form accuracy."
        ),
    }

    reports = Path(reports_dir)
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    result_rows = test_data[ID_COLUMNS + ["exercise_type", TARGET_COLUMN]].copy()
    result_rows["prediction"] = predictions
    probabilities = model.predict_proba(X_test)
    result_rows["confidence"] = probabilities.max(axis=1)
    result_rows.to_csv(reports / "predictions.csv", index=False)

    labels = ["incorrect", "correct"]
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    plt.figure(figsize=(7, 5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title("Seven-Exercise Form Confusion Matrix\nSynthetic Demonstration Data")
    plt.xlabel("Predicted form label")
    plt.ylabel("True form label")
    plt.tight_layout()
    plt.savefig(reports / "confusion_matrix.png", dpi=160)
    plt.close()

    print(pd.DataFrame(metrics["classification_report"]).transpose())
    print(
        "Warning: synthetic demonstration data; do not present these metrics "
        "as real exercise-form performance."
    )
    print(f"Exercise-form reports saved in: {reports}")
    return metrics


def main() -> None:
    """Allow evaluation with: python -m exercise_form.ml.evaluate"""

    evaluate()


if __name__ == "__main__":
    main()
