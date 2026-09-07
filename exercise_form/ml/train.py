"""Train and save the separate seven-exercise form classifier."""

from __future__ import annotations

from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from .dataset import (
    DEFAULT_DATASET_PATH,
    display_dataset_summary,
    get_xy,
    load_dataset,
    split_by_athlete,
)
from .model import DEFAULT_MODEL_PATH, create_model, save_model
from .preprocessing import validate_features


EXERCISE_FORM_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TEST_OUTPUT_PATH = EXERCISE_FORM_DIR / "artifacts" / "test_set.csv"


def train(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    test_output_path: str | Path = DEFAULT_TEST_OUTPUT_PATH,
):
    """Run the complete multi-exercise form training workflow."""

    data = load_dataset(dataset_path)
    display_dataset_summary(data)
    train_data, test_data = split_by_athlete(data)
    X_train, y_train = get_xy(train_data)
    X_test, y_test = get_xy(test_data)
    X_train = validate_features(X_train)
    X_test = validate_features(X_test)

    model = create_model()
    model.fit(X_train, y_train)
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

    save_model(model, model_path, metrics)
    test_output_path = Path(test_output_path)
    test_output_path.parent.mkdir(parents=True, exist_ok=True)
    test_data.to_csv(test_output_path, index=False)

    print(f"Rows loaded: {len(data)}")
    print(f"Training rows: {len(train_data)}")
    print(f"Testing rows: {len(test_data)}")
    for name, value in metrics.items():
        print(f"{name.replace('_', ' ').title()}: {value:.4f}")
    print(f"Exercise-form model saved: {model_path}")
    print(
        "Warning: this component uses synthetic demonstration form data. "
        "It is not validated for real coaching or safety decisions."
    )
    return model, metrics


def main() -> None:
    """Allow training with: python -m exercise_form.ml.train"""

    train()


if __name__ == "__main__":
    main()
