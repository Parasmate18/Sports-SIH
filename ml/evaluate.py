"""Evaluate the trained talent model and save honest, labelled reports."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score

from ml import RANDOM_STATE
from ml.dataset import (
    ASSESSMENT_EXERCISES,
    DEFAULT_DATASET_PATH,
    TALENT_LEVELS,
    load_dataset,
    separate_features_and_target,
)
from ml.model import get_feature_importance, load_model
from ml.preprocessing import prepare_train_test_data
from ml.train import DEFAULT_MODEL_PATH


ML_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_PATH = ML_DIR / "reports" / "evaluation_report.txt"
DEFAULT_CONFUSION_MATRIX_PATH = ML_DIR / "reports" / "confusion_matrix.png"


def _calculate_cross_validation_scores(model, features, target):
    """Return weighted-F1 CV scores, or an honest reason for skipping them."""

    class_counts = target.value_counts()
    smallest_class = int(class_counts.min())

    if len(features) < 40:
        return None, "Cross-validation skipped: fewer than 40 records are available."
    if smallest_class < 3:
        return (
            None,
            "Cross-validation skipped: at least one class has fewer than 3 records.",
        )

    fold_count = min(5, smallest_class)
    splitter = StratifiedKFold(
        n_splits=fold_count, shuffle=True, random_state=RANDOM_STATE
    )
    scores = cross_val_score(
        model,
        features,
        target,
        cv=splitter,
        scoring="f1_weighted",
        n_jobs=1,
    )
    return scores, None


def evaluate_talent_model(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    report_path: str | Path = DEFAULT_REPORT_PATH,
    confusion_matrix_path: str | Path = DEFAULT_CONFUSION_MATRIX_PATH,
) -> dict[str, float]:
    """Evaluate the saved model on its deterministic held-out test split."""

    data = load_dataset(dataset_path)
    features, target = separate_features_and_target(data)
    _, X_test, _, y_test = prepare_train_test_data(
        data, random_state=RANDOM_STATE
    )

    model = load_model(model_path)
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
    }

    report_text = classification_report(
        y_test,
        predictions,
        labels=TALENT_LEVELS,
        target_names=TALENT_LEVELS,
        digits=4,
        zero_division=0,
    )
    matrix = confusion_matrix(y_test, predictions, labels=TALENT_LEVELS)

    cv_scores, cv_warning = _calculate_cross_validation_scores(
        model, features, target
    )

    warnings = [
        "The bundled athlete_data.csv is synthetic demonstration data; these "
        "metrics do not measure real-world sports-talent accuracy."
    ]
    if len(data) < 200:
        warnings.append(
            "The dataset has fewer than 200 records, so the held-out metrics "
            "have high uncertainty and must not be used for official claims."
        )
    if cv_warning:
        warnings.append(cv_warning)

    report_lines = [
        "SIH25073 - Talent-Level Model Evaluation",
        "=" * 45,
        f"Evaluation date (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Total cleaned records: {len(data)}",
        f"Held-out test records: {len(X_test)}",
        f"Random state: {RANDOM_STATE}",
        "Assessment exercises: " + ", ".join(ASSESSMENT_EXERCISES),
        "",
        "Held-out metrics",
        "-" * 20,
        f"Accuracy:           {metrics['accuracy']:.4f}",
        f"Weighted precision: {metrics['weighted_precision']:.4f}",
        f"Weighted recall:    {metrics['weighted_recall']:.4f}",
        f"Weighted F1-score:  {metrics['weighted_f1']:.4f}",
        "",
        "Classification report",
        "-" * 24,
        report_text,
        "Confusion matrix (rows=true, columns=predicted)",
        "-" * 48,
        f"Labels: {TALENT_LEVELS}",
        np.array2string(matrix),
        "",
        "Cross-validation (weighted F1-score)",
        "-" * 39,
    ]

    if cv_scores is not None:
        formatted_scores = ", ".join(f"{score:.4f}" for score in cv_scores)
        report_lines.extend(
            [
                f"Fold scores: {formatted_scores}",
                f"Mean: {float(np.mean(cv_scores)):.4f}",
                f"Standard deviation: {float(np.std(cv_scores)):.4f}",
            ]
        )
    else:
        report_lines.append(cv_warning or "Cross-validation was not available.")

    report_lines.extend(["", "Top feature importance values", "-" * 29])
    importance_rows = get_feature_importance(model, top_n=10)
    if importance_rows:
        report_lines.extend(
            f"{row['feature']}: {row['importance']:.6f}"
            for row in importance_rows
        )
    else:
        report_lines.append("Feature importance is not available for this model.")

    report_lines.extend(["", "Warnings and interpretation", "-" * 27])
    report_lines.extend(f"- {warning}" for warning in warnings)

    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    confusion_matrix_path = Path(confusion_matrix_path)
    confusion_matrix_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=TALENT_LEVELS,
        yticklabels=TALENT_LEVELS,
    )
    plt.title("Talent-Level Confusion Matrix\nSynthetic Demonstration Data")
    plt.xlabel("Predicted talent level")
    plt.ylabel("True talent level")
    plt.xticks(rotation=25, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(confusion_matrix_path, dpi=160)
    plt.close()

    print("Evaluation completed.")
    for name, value in metrics.items():
        print(f"{name.replace('_', ' ').title()}: {value:.4f}")
    if cv_scores is not None:
        print(
            "Cross-validation weighted F1: "
            f"{float(np.mean(cv_scores)):.4f} +/- {float(np.std(cv_scores)):.4f}"
        )
    for warning in warnings:
        print(f"Warning: {warning}")
    print(f"Text report saved to: {report_path}")
    print(f"Confusion matrix saved to: {confusion_matrix_path}")
    return metrics


def main() -> None:
    """Allow evaluation with: python -m ml.evaluate"""

    evaluate_talent_model()


if __name__ == "__main__":
    main()
