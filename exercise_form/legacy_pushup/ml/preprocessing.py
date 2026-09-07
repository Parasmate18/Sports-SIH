"""Validate incoming features and build reusable preprocessing."""

from __future__ import annotations

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from ml.dataset import FEATURE_COLUMNS


ANGLE_COLUMNS = [
    "min_elbow_angle",
    "max_elbow_angle",
    "mean_body_angle",
    "hip_deviation",
    "range_of_motion",
]


def validate_features(features: pd.DataFrame) -> pd.DataFrame:
    """Check feature names, types and physically meaningful ranges."""
    missing = sorted(set(FEATURE_COLUMNS) - set(features.columns))
    if missing:
        raise ValueError(f"Missing prediction features: {missing}")

    clean = features[FEATURE_COLUMNS].copy()
    for column in FEATURE_COLUMNS:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    for column in ANGLE_COLUMNS:
        invalid = clean[column].dropna().loc[lambda values: ~values.between(0, 180)]
        if not invalid.empty:
            raise ValueError(f"{column} must be between 0 and 180 degrees.")

    for column in ["landmark_confidence", "visibility_score"]:
        invalid = clean[column].dropna().loc[lambda values: ~values.between(0, 1)]
        if not invalid.empty:
            raise ValueError(f"{column} must be between 0 and 1.")

    if (clean["rep_duration"].dropna() <= 0).any():
        raise ValueError("rep_duration must be greater than zero.")
    if (clean["movement_speed"].dropna() < 0).any():
        raise ValueError("movement_speed cannot be negative.")

    return clean


def build_preprocessor() -> Pipeline:
    """Median imputation keeps occasional missing landmarks from crashing ML."""
    return Pipeline([("imputer", SimpleImputer(strategy="median"))])

