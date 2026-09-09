"""Build leakage-safe preprocessing and create train/test splits."""

from __future__ import annotations

from math import ceil
from typing import Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml import RANDOM_STATE
from ml.dataset import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    separate_features_and_target,
)


def build_preprocessor() -> ColumnTransformer:
    """Create preprocessing that is fitted only when the model is trained.

    Numerical values use median imputation and standardisation. Gender uses
    most-frequent imputation and one-hot encoding. Keeping this object inside
    the final model pipeline guarantees identical transformations at inference.
    """

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot_encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numerical", numerical_pipeline, NUMERICAL_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def _stratification_is_possible(y: pd.Series, test_size: float) -> bool:
    """Return True when every class can appear in both train and test sets."""

    class_counts = y.value_counts()
    class_count = int(y.nunique())
    test_record_count = ceil(len(y) * test_size)
    train_record_count = len(y) - test_record_count

    return bool(
        class_count >= 2
        and int(class_counts.min()) >= 2
        and test_record_count >= class_count
        and train_record_count >= class_count
    )


def split_data(
    features: pd.DataFrame,
    target: pd.Series,
    test_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split raw data before preprocessing to prevent information leakage."""

    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")
    if len(features) != len(target):
        raise ValueError("Features and target must contain the same number of rows.")

    stratify_target = target if _stratification_is_possible(target, test_size) else None
    if stratify_target is None:
        print(
            "Warning: stratified splitting is not possible for this dataset. "
            "A regular random split will be used."
        )

    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_target,
    )


def prepare_train_test_data(
    data: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Separate features/target, then return raw training and testing data."""

    features, target = separate_features_and_target(data)
    return split_data(features, target, test_size, random_state)
