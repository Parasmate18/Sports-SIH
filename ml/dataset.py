"""Load, validate, clean, and describe athlete talent-assessment data."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


ML_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET_PATH = ML_DIR / "data" / "athlete_data.csv"

TARGET_COLUMN = "talent_level"
TALENT_LEVELS = ["Beginner", "Intermediate", "Advanced", "Elite"]
ASSESSMENT_EXERCISES = [
    "Push-ups",
    "Squats",
    "Deadlift repetitions",
    "50-metre running",
    "Sit-ups",
    "Plank",
    "Vertical jump",
]

# Only these fields are given to the talent-level model. In particular,
# athlete_id, talent_level, and recommended_sport are deliberately excluded.
INPUT_FEATURES = [
    "age",
    "gender",
    "height_cm",
    "weight_kg",
    "pushup_count",
    "squat_count",
    "deadlift_reps",
    "running_50m_seconds",
    "situp_count",
    "plank_duration_seconds",
    "vertical_jump_cm",
]

NUMERICAL_FEATURES = [column for column in INPUT_FEATURES if column != "gender"]
CATEGORICAL_FEATURES = ["gender"]

REQUIRED_COLUMNS = [
    "athlete_id",
    *INPUT_FEATURES,
    TARGET_COLUMN,
    "recommended_sport",
]

ALLOWED_GENDERS = ["Male", "Female", "Other"]

# These are broad physical-validity limits, not official sports benchmarks.
# Replace or refine them after consulting sports-science experts.
VALID_NUMERIC_RANGES = {
    "age": (5, 100),
    "height_cm": (80, 250),
    "weight_kg": (20, 300),
    "pushup_count": (0, 200),
    "squat_count": (0, 300),
    "deadlift_reps": (0, 100),
    "running_50m_seconds": (3, 30),
    "situp_count": (0, 200),
    "plank_duration_seconds": (0, 1800),
    "vertical_jump_cm": (0, 150),
}

INTEGER_COLUMNS = {
    "age",
    "pushup_count",
    "squat_count",
    "deadlift_reps",
    "situp_count",
}


def _csv_row_numbers(mask: pd.Series) -> list[int]:
    """Convert zero-based DataFrame indexes to human-friendly CSV row numbers."""

    return [int(index) + 2 for index in mask[mask].index]


def _normalise_text(value: object) -> object:
    """Trim a text cell while preserving missing values."""

    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    return text if text else np.nan


def load_dataset(csv_path: str | Path = DEFAULT_DATASET_PATH) -> pd.DataFrame:
    """Load the CSV, validate its schema and values, and return clean data.

    Missing input features are deliberately retained because the preprocessing
    pipeline imputes them after the train/test split. Missing identifiers or
    target labels cannot be used for supervised training and therefore raise a
    clear error.
    """

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Athlete dataset was not found at: {csv_path}\n"
            "Place the CSV there or pass a valid path to load_dataset()."
        )
    if not csv_path.is_file():
        raise ValueError(f"Dataset path is not a file: {csv_path}")

    try:
        data = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError as error:
        raise ValueError(f"Dataset is empty: {csv_path}") from error
    except Exception as error:
        raise ValueError(f"Could not read dataset '{csv_path}': {error}") from error

    if data.empty:
        raise ValueError("The dataset contains column names but no athlete records.")

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in data.columns
    ]
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing_columns)
        )

    # Ignore unrelated extra columns so they can never accidentally enter the model.
    data = data[REQUIRED_COLUMNS].copy()

    for column in ["athlete_id", "gender", TARGET_COLUMN, "recommended_sport"]:
        data[column] = data[column].map(_normalise_text)

    duplicate_count = int(data.duplicated().sum())
    if duplicate_count:
        data = data.drop_duplicates().copy()
        print(f"Removed {duplicate_count} duplicate record(s).")

    # Normalise supported categories without changing missing cells.
    data["gender"] = data["gender"].map(
        lambda value: str(value).title() if pd.notna(value) else np.nan
    )
    data[TARGET_COLUMN] = data[TARGET_COLUMN].map(
        lambda value: str(value).title() if pd.notna(value) else np.nan
    )

    invalid_genders = sorted(
        set(data["gender"].dropna()) - set(ALLOWED_GENDERS)
    )
    if invalid_genders:
        raise ValueError(
            f"Unsupported gender value(s): {invalid_genders}. "
            f"Use one of {ALLOWED_GENDERS}, or leave the cell empty for imputation."
        )

    invalid_targets = sorted(
        set(data[TARGET_COLUMN].dropna()) - set(TALENT_LEVELS)
    )
    if invalid_targets:
        raise ValueError(
            f"Unsupported talent_level value(s): {invalid_targets}. "
            f"Use only {TALENT_LEVELS}."
        )

    essential_missing = data["athlete_id"].isna() | data[TARGET_COLUMN].isna()
    if essential_missing.any():
        rows = _csv_row_numbers(essential_missing)
        raise ValueError(
            "athlete_id and talent_level cannot be missing. "
            f"Check CSV row(s): {rows}"
        )

    if data["athlete_id"].duplicated().any():
        repeated_ids = sorted(
            data.loc[data["athlete_id"].duplicated(keep=False), "athlete_id"]
            .astype(str)
            .unique()
            .tolist()
        )
        print(
            "Warning: repeated athlete_id values were retained because they may "
            f"represent separate assessments: {repeated_ids}"
        )

    # Convert numerical text safely and reject non-numeric or infinite values.
    for column in NUMERICAL_FEATURES:
        original_values = data[column]
        converted_values = pd.to_numeric(original_values, errors="coerce")

        non_numeric = original_values.notna() & converted_values.isna()
        if non_numeric.any():
            rows = _csv_row_numbers(non_numeric)
            raise ValueError(
                f"Column '{column}' contains non-numeric value(s) at CSV row(s): "
                f"{rows}"
            )

        infinite = converted_values.notna() & ~np.isfinite(converted_values)
        if infinite.any():
            rows = _csv_row_numbers(infinite)
            raise ValueError(
                f"Column '{column}' contains an infinite value at CSV row(s): {rows}"
            )

        minimum, maximum = VALID_NUMERIC_RANGES[column]
        outside_range = converted_values.notna() & ~converted_values.between(
            minimum, maximum, inclusive="both"
        )
        if outside_range.any():
            rows = _csv_row_numbers(outside_range)
            raise ValueError(
                f"Invalid '{column}' value at CSV row(s) {rows}. "
                f"Expected a value from {minimum} to {maximum}."
            )

        if column in INTEGER_COLUMNS:
            non_integer = converted_values.notna() & ~np.isclose(
                converted_values % 1, 0
            )
            if non_integer.any():
                rows = _csv_row_numbers(non_integer)
                raise ValueError(
                    f"Column '{column}' must contain whole numbers. "
                    f"Check CSV row(s): {rows}"
                )

        data[column] = converted_values

    completely_missing_features = [
        column for column in INPUT_FEATURES if data[column].isna().all()
    ]
    if completely_missing_features:
        raise ValueError(
            "These input columns are completely empty and cannot be imputed: "
            + ", ".join(completely_missing_features)
        )

    if data[TARGET_COLUMN].nunique() < 2:
        raise ValueError("At least two talent_level classes are required for training.")

    missing_inputs = data[INPUT_FEATURES].isna().sum()
    missing_inputs = missing_inputs[missing_inputs > 0]
    if not missing_inputs.empty:
        details = ", ".join(
            f"{column}={int(count)}" for column, count in missing_inputs.items()
        )
        print(
            "Detected missing input values (the training pipeline will impute "
            f"them): {details}"
        )

    return data.reset_index(drop=True)


def separate_features_and_target(
    data: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Return model inputs and talent-level labels without target leakage."""

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(
            "Cannot separate features because columns are missing: "
            + ", ".join(missing)
        )
    features = data[INPUT_FEATURES].copy()
    target = data[TARGET_COLUMN].copy()
    return features, target


def display_dataset_summary(data: pd.DataFrame) -> None:
    """Print a small, beginner-friendly summary of the cleaned dataset."""

    print("\nDataset summary")
    print("-" * 40)
    print(f"Records: {len(data)}")
    print(f"Input features: {len(INPUT_FEATURES)}")
    print(f"Unique athletes: {data['athlete_id'].nunique()}")
    print("Assessments: " + ", ".join(ASSESSMENT_EXERCISES))
    print("Talent-level distribution:")
    class_counts = data[TARGET_COLUMN].value_counts()
    for talent_level in TALENT_LEVELS:
        print(f"  {talent_level}: {int(class_counts.get(talent_level, 0))}")

    missing_counts = data[INPUT_FEATURES].isna().sum()
    if int(missing_counts.sum()) == 0:
        print("Missing input values: none")
    else:
        print("Missing input values:")
        for column, count in missing_counts[missing_counts > 0].items():
            print(f"  {column}: {int(count)}")
    print("-" * 40)
