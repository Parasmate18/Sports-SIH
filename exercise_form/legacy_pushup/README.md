# SIH25073 — M1 ML Engineer Module

This project trains a model that classifies one exercise repetition as
`correct` or `incorrect`. M2 supplies movement features, while M5 supplies the
labels. M4 loads the exported model and calls `predict_exercise`.

## Input contract

Every CSV row represents one repetition and requires:

`athlete_id, video_id, rep_number, exercise_type, min_elbow_angle,
max_elbow_angle, mean_body_angle, hip_deviation, range_of_motion, rep_duration,
movement_speed, landmark_confidence, visibility_score, label`

Labels must be `correct` or `incorrect`.

## Setup (Windows / VS Code)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Train

Replace the sample CSV with the real combined M2 + M5 dataset, keeping the same
columns. From the project root run:

```powershell
python -m ml.train --data data/processed/exercise_features.csv
```

This produces `artifacts/exercise_model.joblib` and `artifacts/test_set.csv`.

## Evaluate

```powershell
python -m ml.evaluate
```

M6 receives the files created in `reports/`.

## Backend prediction (M4)

```python
from ml.model import predict_exercise

features = {
    "min_elbow_angle": 75.0,
    "max_elbow_angle": 168.0,
    "mean_body_angle": 174.0,
    "hip_deviation": 5.0,
    "range_of_motion": 93.0,
    "rep_duration": 1.8,
    "movement_speed": 0.62,
    "landmark_confidence": 0.95,
    "visibility_score": 0.96,
}

result = predict_exercise(features, "artifacts/exercise_model.joblib")
print(result)
```

Example output:

```python
{
    "label": "correct",
    "raw_prediction": "correct",
    "confidence": 0.91,
    "form_score": 91.0,
    "model_version": "1.0.0"
}
```

## File ownership

- `dataset.py`: load data and make athlete-wise train/test splits.
- `preprocessing.py`: validate and clean numerical features.
- `model.py`: define, save, load and run the model.
- `train.py`: train the model and save its artifact.
- `evaluate.py`: generate metrics, predictions and confusion matrix.

Important: this starter model is a prototype. Do not claim official SAI talent
selection accuracy until it is trained and tested on approved, representative
data and official scoring criteria.

