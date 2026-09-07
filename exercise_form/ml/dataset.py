"""Load and validate labelled form data for seven exercise types."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from . import RANDOM_STATE


DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "exercise_features.csv"
)

ALLOWED_EXERCISES = [
    "pushup",
    "squat",
    "deadlift",
    "running",
    "situp",
    "plank",
    "vertical_jump",
]

NUMERICAL_FEATURES = [
    "primary_joint_min_angle",
    "primary_joint_max_angle",
    "torso_deviation_degrees",
    "range_of_motion_degrees",
    "stability_score",
    "movement_speed",
    "assessment_duration_seconds",
    "landmark_confidence",
    "visibility_score",
]
CATEGORICAL_FEATURES = ["exercise_type"]
MODEL_INPUT_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
ID_COLUMNS = ["athlete_id", "video_id", "sample_number"]
TARGET_COLUMN = "label"
ALLOWED_LABELS = ["correct", "incorrect"]

VALID_RANGES = {
    "primary_joint_min_angle": (0, 180),
    "primary_joint_max_angle": (0, 180),
    "torso_deviation_degrees": (0, 90),
    "range_of_motion_degrees": (0, 180),
    "stability_score": (0, 100),
    "movement_speed": (0, 10),
    "assessment_duration_seconds": (0.1, 1800),
    "landmark_confidence": (0, 1),
    "visibility_score": (0, 1),
}


def load_dataset(csv_path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load, clean, and validate the multi-exercise form dataset."""

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Exercise-form dataset not found: {csv_path}")
    if not csv_path.is_file():
        raise ValueError(f"Exercise-form dataset path is not a file: {csv_path}")

    try:
        data = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError as error:
        raise ValueError(f"Exercise-form dataset is empty: {csv_path}") from error

    required_columns = (
        ID_COLUMNS + CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET_COLUMN]
    )
    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]
    if missing_columns:
        raise ValueError(
            "Exercise-form dataset is missing columns: "
            + ", ".join(missing_columns)
        )

    data = data[required_columns].copy()
    duplicate_count = int(data.duplicated().sum())
    if duplicate_count:
        data = data.drop_duplicates().copy()
        print(f"Removed {duplicate_count} duplicate exercise-form record(s).")

    for column in ID_COLUMNS + CATEGORICAL_FEATURES + [TARGET_COLUMN]:
        data[column] = data[column].map(
            lambda value: str(value).strip().lower()
            if pd.notna(value) and str(value).strip()
            else np.nan
        )

    essential_columns = ID_COLUMNS + CATEGORICAL_FEATURES + [TARGET_COLUMN]
    essential_missing = data[essential_columns].isna().any(axis=1)
    if essential_missing.any():
        rows = [int(index) + 2 for index in essential_missing[essential_missing].index]
        raise ValueError(
            "Identifiers, exercise_type, and label cannot be missing. "
            f"Check CSV row(s): {rows}"
        )

    invalid_exercises = sorted(
        set(data["exercise_type"]) - set(ALLOWED_EXERCISES)
    )
    if invalid_exercises:
        raise ValueError(
            f"Unsupported exercise_type value(s): {invalid_exercises}. "
            f"Use only {ALLOWED_EXERCISES}."
        )

    invalid_labels = sorted(set(data[TARGET_COLUMN]) - set(ALLOWED_LABELS))
    if invalid_labels:
        raise ValueError(
            f"Unsupported form label(s): {invalid_labels}. "
            f"Use only {ALLOWED_LABELS}."
        )

    for column in NUMERICAL_FEATURES:
        original = data[column]
        converted = pd.to_numeric(original, errors="coerce")

        non_numeric = original.notna() & converted.isna()
        if non_numeric.any():
            rows = [int(index) + 2 for index in non_numeric[non_numeric].index]
            raise ValueError(
                f"Column '{column}' contains non-numeric data at CSV row(s): {rows}"
            )

        infinite = converted.notna() & ~np.isfinite(converted)
        if infinite.any():
            rows = [int(index) + 2 for index in infinite[infinite].index]
            raise ValueError(
                f"Column '{column}' contains infinite data at CSV row(s): {rows}"
            )

        minimum, maximum = VALID_RANGES[column]
        invalid_range = converted.notna() & ~converted.between(
            minimum, maximum, inclusive="both"
        )
        if invalid_range.any():
            rows = [int(index) + 2 for index in invalid_range[invalid_range].index]
            raise ValueError(
                f"Invalid '{column}' value at CSV row(s) {rows}. "
                f"Expected {minimum} to {maximum}."
            )
        data[column] = converted

    invalid_angle_order = (
        data["primary_joint_min_angle"].notna()
        & data["primary_joint_max_angle"].notna()
        & (
            data["primary_joint_min_angle"]
            > data["primary_joint_max_angle"]
        )
    )
    if invalid_angle_order.any():
        rows = [
            int(index) + 2
            for index in invalid_angle_order[invalid_angle_order].index
        ]
        raise ValueError(
            "primary_joint_min_angle cannot exceed "
            f"primary_joint_max_angle. Check CSV row(s): {rows}"
        )

    completely_missing = [
        column for column in NUMERICAL_FEATURES if data[column].isna().all()
    ]
    if completely_missing:
        raise ValueError(
            "These exercise-form features are completely empty: "
            + ", ".join(completely_missing)
        )

    if data[TARGET_COLUMN].nunique() < 2:
        raise ValueError("Both correct and incorrect labels are required.")

    missing_counts = data[NUMERICAL_FEATURES].isna().sum()
    missing_counts = missing_counts[missing_counts > 0]
    if not missing_counts.empty:
        details = ", ".join(
            f"{column}={int(count)}" for column, count in missing_counts.items()
        )
        print(
            "Detected missing form features; the pipeline will impute them: "
            + details
        )

    return data.reset_index(drop=True)


def split_by_athlete(
    data: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Keep one athlete's samples together whenever grouping is possible."""

    if data["athlete_id"].nunique() >= 5:
        splitter = GroupShuffleSplit(
            n_splits=1, test_size=test_size, random_state=random_state
        )
        train_index, test_index = next(
            splitter.split(
                data,
                data[TARGET_COLUMN],
                groups=data["athlete_id"],
            )
        )
        train_data = data.iloc[train_index].reset_index(drop=True)
        test_data = data.iloc[test_index].reset_index(drop=True)
    else:
        train_data, test_data = train_test_split(
            data,
            test_size=test_size,
            random_state=random_state,
            stratify=data[TARGET_COLUMN],
        )
        train_data = train_data.reset_index(drop=True)
        test_data = test_data.reset_index(drop=True)

    return train_data, test_data


def get_xy(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return form-model features and correct/incorrect labels."""

    return data[MODEL_INPUT_COLUMNS].copy(), data[TARGET_COLUMN].copy()


def display_dataset_summary(data: pd.DataFrame) -> None:
    """Print counts by exercise and label."""

    print("\nExercise-form dataset summary")
    print("-" * 45)
    print(f"Records: {len(data)}")
    print(f"Unique athletes: {data['athlete_id'].nunique()}")
    print("Records by exercise and label:")
    summary = data.groupby(["exercise_type", TARGET_COLUMN]).size()
    for exercise in ALLOWED_EXERCISES:
        correct_count = int(summary.get((exercise, "correct"), 0))
        incorrect_count = int(summary.get((exercise, "incorrect"), 0))
        print(
            f"  {exercise}: correct={correct_count}, incorrect={incorrect_count}"
        )
    print("-" * 45)
