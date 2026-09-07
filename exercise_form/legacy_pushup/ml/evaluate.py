"""Evaluate a trained model and export reports for M6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.dataset import get_xy, load_dataset
from ml.model import load_model
from ml.preprocessing import validate_features


def evaluate(model_path: str, test_path: str, reports_dir: str):
    bundle = load_model(model_path)
    test_data = load_dataset(test_path)
    X_test, y_test = get_xy(test_data)
    X_test = validate_features(X_test)
    predictions = bundle["model"].predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision_correct": float(
            precision_score(y_test, predictions, pos_label="correct", zero_division=0)
        ),
        "recall_correct": float(
            recall_score(y_test, predictions, pos_label="correct", zero_division=0)
        ),
        "f1_correct": float(
            f1_score(y_test, predictions, pos_label="correct", zero_division=0)
        ),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
    }

    reports = Path(reports_dir)
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    result_rows = test_data[["athlete_id", "video_id", "rep_number", "label"]].copy()
    result_rows["prediction"] = predictions
    probabilities = bundle["model"].predict_proba(X_test)
    result_rows["confidence"] = probabilities.max(axis=1)
    result_rows.to_csv(reports / "predictions.csv", index=False)

    labels = ["incorrect", "correct"]
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    ConfusionMatrixDisplay(matrix, display_labels=labels).plot(cmap="Blues")
    plt.title("Exercise Quality Confusion Matrix")
    plt.tight_layout()
    plt.savefig(reports / "confusion_matrix.png", dpi=160)
    plt.close()

    print(pd.DataFrame(metrics["classification_report"]).transpose())
    print(f"Reports saved in: {reports}")
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate the saved classifier")
    parser.add_argument("--model", default="artifacts/exercise_model.joblib")
    parser.add_argument("--test-data", default="artifacts/test_set.csv")
    parser.add_argument("--reports", default="reports")
    args = parser.parse_args()
    evaluate(args.model, args.test_data, args.reports)


if __name__ == "__main__":
    main()

