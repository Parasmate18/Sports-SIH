"""Validate form features and build reusable multi-exercise preprocessing."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .dataset import (
    ALLOWED_EXERCISES,
    CATEGORICAL_FEATURES,
    MODEL_INPUT_COLUMNS,
    NUMERICAL_FEATURES,
    VALID_RANGES,
)


def validate_features(features: pd.DataFrame) -> pd.DataFrame:
    """Validate exercise type, feature names, numeric values, and ranges."""

    missing = [column for column in MODEL_INPUT_COLUMNS if column not in features]
    if missing:
        raise ValueError("Missing exercise-form feature(s): " + ", ".join(missing))

    clean = features[MODEL_INPUT_COLUMNS].copy()
    clean["exercise_type"] = clean["exercise_type"].map(
        lambda value: str(value).strip().lower() if pd.notna(value) else np.nan
    )

    if clean["exercise_type"].isna().any():
        raise ValueError("exercise_type cannot be missing for form prediction.")
    invalid_exercises = sorted(
        set(clean["exercise_type"]) - set(ALLOWED_EXERCISES)
    )
    if invalid_exercises:
        raise ValueError(
            f"Unsupported exercise_type value(s): {invalid_exercises}. "
            f"Use only {ALLOWED_EXERCISES}."
        )

    for column in NUMERICAL_FEATURES:
        original = clean[column]
        converted = pd.to_numeric(original, errors="coerce")
        non_numeric = original.notna() & converted.isna()
        if non_numeric.any():
            raise ValueError(f"{column} must contain numeric values.")
        infinite = converted.notna() & ~np.isfinite(converted)
        if infinite.any():
            raise ValueError(f"{column} must contain finite values.")

        minimum, maximum = VALID_RANGES[column]
        invalid_range = converted.notna() & ~converted.between(
            minimum, maximum, inclusive="both"
        )
        if invalid_range.any():
            raise ValueError(
                f"{column} must be between {minimum} and {maximum}."
            )
        clean[column] = converted

    invalid_angle_order = (
        clean["primary_joint_min_angle"].notna()
        & clean["primary_joint_max_angle"].notna()
        & (
            clean["primary_joint_min_angle"]
            > clean["primary_joint_max_angle"]
        )
    )
    if invalid_angle_order.any():
        raise ValueError(
            "primary_joint_min_angle cannot exceed primary_joint_max_angle."
        )

    return clean


def build_preprocessor() -> ColumnTransformer:
    """Create numeric and exercise-type preprocessing inside one transformer."""

    numerical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot_encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    return ColumnTransformer(
        [
            ("numerical", numerical_pipeline, NUMERICAL_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
