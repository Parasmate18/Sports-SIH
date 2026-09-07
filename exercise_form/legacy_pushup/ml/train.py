"""Train and save the SIH25073 exercise-quality classifier."""

from __future__ import annotations

import argparse
from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from ml.dataset import get_xy, load_dataset, split_by_athlete
from ml.model import create_model, save_model
from ml.preprocessing import validate_features


def train(dataset_path: str, model_path: str, test_output_path: str):
    data = load_dataset(dataset_path)
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
        "precision": float(
            precision_score(y_test, predictions, pos_label="correct", zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, pos_label="correct", zero_division=0)
        ),
        "f1": float(
            f1_score(y_test, predictions, pos_label="correct", zero_division=0)
        ),
    }

    save_model(model, model_path, metrics)
    Path(test_output_path).parent.mkdir(parents=True, exist_ok=True)
    test_data.to_csv(test_output_path, index=False)

    print(f"Rows loaded: {len(data)}")
    print(f"Training rows: {len(train_data)}")
    print(f"Testing rows: {len(test_data)}")
    for name, value in metrics.items():
        print(f"{name.capitalize()}: {value:.4f}")
    print(f"Model saved: {model_path}")
    return model, metrics


def main():
    parser = argparse.ArgumentParser(description="Train the exercise classifier")
    parser.add_argument("--data", default="data/processed/exercise_features.csv")
    parser.add_argument("--model", default="artifacts/exercise_model.joblib")
    parser.add_argument("--test-output", default="artifacts/test_set.csv")
    args = parser.parse_args()
    train(args.data, args.model, args.test_output)


if __name__ == "__main__":
    main()

