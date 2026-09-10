"""Train and save the SIH25073 athlete talent-level classifier."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ml import MODEL_VERSION, RANDOM_STATE
from ml.dataset import (
    ASSESSMENT_EXERCISES,
    DEFAULT_DATASET_PATH,
    INPUT_FEATURES,
    TALENT_LEVELS,
    display_dataset_summary,
    load_dataset,
)
from ml.model import (
    build_model_pipeline,
    get_feature_importance,
    save_model,
    train_model,
)
from ml.preprocessing import prepare_train_test_data


ML_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = ML_DIR / "saved_models" / "talent_model.pkl"
DEFAULT_METADATA_PATH = ML_DIR / "saved_models" / "model_metadata.json"


def train_talent_model(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    metadata_path: str | Path = DEFAULT_METADATA_PATH,
) -> tuple[Any, dict[str, Any]]:
    """Run the complete training workflow and return model plus metadata."""

    data = load_dataset(dataset_path)
    display_dataset_summary(data)

    X_train, X_test, y_train, _ = prepare_train_test_data(
        data, random_state=RANDOM_STATE
    )

    model = build_model_pipeline(random_state=RANDOM_STATE)
    model = train_model(model, X_train, y_train)
    saved_model_path = save_model(model, model_path)

    trained_classes = [
        str(value) for value in model.named_steps["classifier"].classes_.tolist()
    ]
    ordered_classes = [
        talent_level for talent_level in TALENT_LEVELS if talent_level in trained_classes
    ]

    metadata = {
        "model_name": "Random Forest talent-level classifier",
        "version": MODEL_VERSION,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "input_feature_names": INPUT_FEATURES,
        "assessment_exercises": ASSESSMENT_EXERCISES,
        "target_classes": ordered_classes,
        "training_record_count": int(len(X_train)),
        "testing_record_count": int(len(X_test)),
        "random_state": RANDOM_STATE,
        "class_weight": "balanced",
        "feature_importance": get_feature_importance(model),
    }

    metadata_path = Path(metadata_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print(f"Training records: {len(X_train)}")
    print(f"Testing records reserved for evaluation: {len(X_test)}")
    print(f"Model saved to: {saved_model_path}")
    print(f"Metadata saved to: {metadata_path}")
    print(
        "Warning: the bundled CSV is synthetic demonstration data. "
        "Training success does not establish real-world model accuracy."
    )
    return model, metadata


def main() -> None:
    """Allow training with: python -m ml.train"""

    train_talent_model()


if __name__ == "__main__":
    main()
