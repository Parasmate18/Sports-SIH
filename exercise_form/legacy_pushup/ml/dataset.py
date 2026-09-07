"""Load, validate and split the labelled repetition dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split


FEATURE_COLUMNS = [
    "min_elbow_angle",
    "max_elbow_angle",
    "mean_body_angle",
    "hip_deviation",
    "range_of_motion",
    "rep_duration",
    "movement_speed",
    "landmark_confidence",
    "visibility_score",
]

ID_COLUMNS = ["athlete_id", "video_id", "rep_number", "exercise_type"]
TARGET_COLUMN = "label"
ALLOWED_LABELS = {"correct", "incorrect"}


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    """Read a CSV and validate the columns required by the ML pipeline."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    data = pd.read_csv(csv_path)
    required = set(FEATURE_COLUMNS + ID_COLUMNS + [TARGET_COLUMN])
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    data = data.drop_duplicates(subset=["video_id", "rep_number"]).copy()
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(str).str.strip().str.lower()

    bad_labels = sorted(set(data[TARGET_COLUMN].dropna()) - ALLOWED_LABELS)
    if bad_labels:
        raise ValueError(
            f"Unsupported labels {bad_labels}. Use only: {sorted(ALLOWED_LABELS)}"
        )

    if data[TARGET_COLUMN].nunique() < 2:
        raise ValueError("The dataset must contain both correct and incorrect labels.")

    for column in FEATURE_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    return data.reset_index(drop=True)


def split_by_athlete(
    data: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split the dataset so an athlete cannot appear in both sets."""
    if data["athlete_id"].nunique() >= 3:
        splitter = GroupShuffleSplit(
            n_splits=1, test_size=test_size, random_state=random_state
        )
        train_index, test_index = next(
            splitter.split(data, data[TARGET_COLUMN], groups=data["athlete_id"])
        )
    else:
        # Only for tiny demonstrations. Real evaluation should use >= 3 athletes.
        train_index, test_index = train_test_split(
            range(len(data)),
            test_size=test_size,
            random_state=random_state,
            stratify=data[TARGET_COLUMN],
        )

    train_data = data.iloc[train_index].reset_index(drop=True)
    test_data = data.iloc[test_index].reset_index(drop=True)
    return train_data, test_data


def get_xy(data: pd.DataFrame):
    """Return model features and target labels."""
    return data[FEATURE_COLUMNS].copy(), data[TARGET_COLUMN].copy()

