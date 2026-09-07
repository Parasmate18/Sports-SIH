# SIH25073 — M1 Machine Learning Module

## Project overview

This repository contains the M1 machine-learning baseline for:

**SIH25073 — AI-Powered Mobile Platform for Democratizing Sports Talent Assessment**

M1 is responsible for:

**Dataset → Feature Processing → ML Model → Evaluation → Prediction**

The talent model combines seven requested physical assessments:

1. Push-ups
2. Squats
3. Deadlift repetitions at an approved standard load
4. 50-metre running
5. Sit-ups
6. Plank
7. Vertical jump

It predicts one of four demonstration talent levels: Beginner, Intermediate,
Advanced, or Elite.

The project also contains a completely separate exercise-form classifier for
the same seven exercise types. A correct exercise-form result is never treated
as the athlete's complete talent level.

## Important synthetic-data notice

Both bundled datasets are synthetic demonstration data.

- ml/data/athlete_data.csv contains 80 unique synthetic athletes, with 20
  records per talent class.
- exercise_form/data/processed/exercise_features.csv contains 112 unique
  synthetic form samples, balanced across seven exercises and two form labels.
- Each dataset includes one duplicate demonstration row and a few missing
  feature cells to test cleaning and pipeline imputation.

The generated evaluation results cannot prove real-world accuracy, fairness,
safety, or athlete-selection quality. Real deployment requires consented and
representative athlete data, standard test protocols, official benchmarks,
independent validation, bias testing, and qualified sports-science review.

## Folder structure

    SIH25073_M1_ML/
    ├── ml/
    │   ├── __init__.py
    │   ├── init.py
    │   ├── dataset.py
    │   ├── preprocessing.py
    │   ├── model.py
    │   ├── train.py
    │   ├── evaluate.py
    │   ├── predict.py
    │   ├── data/
    │   │   └── athlete_data.csv
    │   ├── saved_models/
    │   │   ├── talent_model.pkl
    │   │   └── model_metadata.json
    │   └── reports/
    │       ├── evaluation_report.txt
    │       └── confusion_matrix.png
    ├── exercise_form/
    │   ├── ml/
    │   │   ├── dataset.py
    │   │   ├── preprocessing.py
    │   │   ├── model.py
    │   │   ├── train.py
    │   │   ├── evaluate.py
    │   │   └── predict.py
    │   ├── data/processed/exercise_features.csv
    │   ├── artifacts/exercise_model.joblib
    │   ├── reports/
    │   ├── legacy_pushup/
    │   └── README.md
    ├── requirements.txt
    ├── README.md
    └── .gitignore

legacy_pushup/ is an unchanged backup of the original push-up-only component
from the uploaded ZIP.

## Main talent-model files

| File | Purpose |
| --- | --- |
| ml/__init__.py | Stores model version 1.2.0 and random state 42. |
| ml/init.py | Compatibility file exposing the same shared constants. |
| ml/dataset.py | Loads the CSV, validates columns, finds missing values, removes exact duplicates, rejects invalid ranges, prints a summary, and separates features from the target. |
| ml/preprocessing.py | Uses median and most-frequent imputation, OneHotEncoder, StandardScaler, ColumnTransformer, and a stratified split. |
| ml/model.py | Builds the class-balanced Random Forest pipeline, trains it, saves/loads it with joblib, returns probabilities, and exposes feature importance. |
| ml/train.py | Trains only on the training split and creates the saved pipeline and metadata. |
| ml/evaluate.py | Calculates held-out metrics, classification report, confusion matrix, cross-validation, warnings, and feature importance. |
| ml/predict.py | Validates one athlete, predicts talent level, calculates confidence, and applies editable sport-recommendation and strengths rules. |

## Talent dataset columns

| Column | Meaning | Used by model? |
| --- | --- | --- |
| athlete_id | Unique athlete or assessment identifier | No |
| age | Age in years | Yes |
| gender | Male, Female, or Other | Yes |
| height_cm | Height in centimetres | Yes |
| weight_kg | Weight in kilograms | Yes |
| pushup_count | Completed push-ups under the selected test protocol | Yes |
| squat_count | Completed bodyweight squats under the selected protocol | Yes |
| deadlift_reps | Supervised repetitions at an approved, standardised safe load | Yes |
| running_50m_seconds | Time for a 50-metre run; lower is faster | Yes |
| situp_count | Completed sit-ups under the selected protocol | Yes |
| plank_duration_seconds | Correct plank-hold duration in seconds | Yes |
| vertical_jump_cm | Vertical-jump height in centimetres | Yes |
| talent_level | Beginner, Intermediate, Advanced, or Elite | Target only |
| recommended_sport | Reference label in the CSV | No |

athlete_id, talent_level, and recommended_sport are never model inputs.
Preprocessing is fitted only through the pipeline after the raw train/test
split, preventing target and preprocessing leakage.

## Deadlift safety and measurement

deadlift_reps does not mean an unsupervised one-repetition maximum. It must be
measured with an age-appropriate, expert-approved standard load, correct
equipment, and trained supervision. Replace this demonstration protocol with
the official protocol chosen by the hackathon's sports experts.

## Installation on Windows

Open PowerShell or Command Prompt in the project root:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python -m ml.train
    python -m ml.evaluate
    python -m ml.predict

Python 3.10 or newer is required.

## Linux or macOS

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m ml.train
    python -m ml.evaluate
    python -m ml.predict

All commands should be run from the directory containing this README.

## Training

    python -m ml.train

The verified demonstration run:

1. Removed one exact duplicate.
2. Detected six missing input cells for pipeline imputation.
3. Loaded 80 cleaned records, balanced across four classes.
4. Used 64 records for training and reserved 16 for testing.
5. Fitted the entire preprocessing and Random Forest pipeline on training data.
6. Saved:

       ml/saved_models/talent_model.pkl
       ml/saved_models/model_metadata.json

## Evaluation

    python -m ml.evaluate

Generated:

    ml/reports/evaluation_report.txt
    ml/reports/confusion_matrix.png

Latest verified synthetic demonstration results:

| Metric | Result |
| --- | ---: |
| Held-out records | 16 |
| Accuracy | 1.0000 |
| Weighted precision | 1.0000 |
| Weighted recall | 1.0000 |
| Weighted F1-score | 1.0000 |
| Five-fold CV weighted F1 mean | 0.9733 |
| Five-fold CV standard deviation | 0.0533 |

These are actual outputs from the included code and CSV. They are not evidence
of real-world accuracy because the data is small, structured, and synthetic.

## Prediction

Run:

    python -m ml.predict

Example input:

    {
      "age": 17,
      "gender": "Male",
      "height_cm": 172,
      "weight_kg": 62,
      "pushup_count": 35,
      "squat_count": 48,
      "deadlift_reps": 12,
      "running_50m_seconds": 7.0,
      "situp_count": 42,
      "plank_duration_seconds": 95,
      "vertical_jump_cm": 48
    }

Actual latest demonstration output:

    {
      "talent_level": "Advanced",
      "confidence": 0.9136,
      "recommended_sport": "Athletics",
      "strengths": [
        "Upper-Body Strength",
        "Lower-Body Endurance",
        "Deadlift Strength",
        "Running Speed",
        "Core Endurance"
      ],
      "needs_improvement": [
        "Maintain balanced training"
      ],
      "model_version": "1.2.0",
      "warning": "AI-assisted demonstration only; this is not an official selection decision. Use qualified coaches and approved, age-appropriate protocols. Deadlift assessments must use a safe standard load under trained supervision."
    }

confidence comes from RandomForestClassifier.predict_proba. It is not a
guarantee that the prediction is correct.


## CV teammate integration review (v1.2.0)

The uploaded teammate `cv module.zip` was inspected before this revision. M1 now
contains `ml/cv_adapter.py` and `ml/cv_contract.json` so the boundary between CV
and ML is explicit instead of guessing feature names.

Current direct mappings are: `pushup valid_reps -> pushup_count`, `squat
valid_reps -> squat_count`, and `situp valid_reps -> situp_count`. The reviewed
CV module also has running and pull-up analyzers, but pull-up is not one of the
seven selected M1 assessments, and the running analyzer does not currently
measure an actual 50-metre elapsed time. The reviewed CV module has no deadlift,
plank, or vertical-jump analyzer. Therefore those four M1 measurements must be
provided by an approved manual/backend source until CV implements them. M1 does
**not** invent them from pose angles, displacement, frames, or step count.

The CV review also found a naming mismatch: the push-up analyzer returns `angle`
while the CV `main.py` feature collector checks for `elbow_angle`. This should be
fixed by the CV owner; the M1 adapter intentionally consumes the final
`valid_reps` field and does not modify the teammate's source code.

Example integration:

    from ml.cv_adapter import build_prediction_from_cv

    profile = {"age": 17, "gender": "Male", "height_cm": 172, "weight_kg": 62}
    cv_results = [
        {"test": "pushup", "valid_reps": 35},
        {"test": "squat", "valid_reps": 48},
        {"test": "situp", "valid_reps": 42}
    ]
    remaining = {
        "deadlift_reps": 12,
        "running_50m_seconds": 7.0,
        "plank_duration_seconds": 95,
        "vertical_jump_cm": 48
    }
    result = build_prediction_from_cv(profile, cv_results, remaining)

See `ml/cv_contract.json` for the exact reviewed interface and known gaps.

## Backend integration

    from ml.predict import predict_talent

    athlete = {
        "age": 17,
        "gender": "Male",
        "height_cm": 172,
        "weight_kg": 62,
        "pushup_count": 35,
        "squat_count": 48,
        "deadlift_reps": 12,
        "running_50m_seconds": 7.0,
        "situp_count": 42,
        "plank_duration_seconds": 95,
        "vertical_jump_cm": 48,
    }

    result = predict_talent(athlete)

The backend should catch ValueError and return an HTTP 400 response for missing
or invalid input.

## Sport recommendation

recommended_sport is produced by editable rules in ml/predict.py. The Random
Forest predicts only talent_level.

| Demonstration condition | Recommendation |
| --- | --- |
| Fast running and strong core | Athletics |
| Strong vertical jump and squats | Basketball or Volleyball |
| Fast running and strong squats | Football or Hockey |
| Strong supervised deadlift, push-ups, and squats | Weightlifting or Wrestling |
| Strong core and vertical jump | Gymnastics or Combat Sports |
| No rule matches | General Multi-Sport Development |

These are demonstration rules, not official selection benchmarks.

## Seven-exercise form component

The separate form classifier supports:

- pushup
- squat
- deadlift
- running
- situp
- plank
- vertical_jump

Run it from the same project root:

    python -m exercise_form.ml.train
    python -m exercise_form.ml.evaluate
    python -m exercise_form.ml.predict

It predicts correct, incorrect, or uncertain for one exercise sample. See
exercise_form/README.md for its feature contract and limitations.

## Current limitations

- Both datasets are synthetic.
- Synthetic classes and form labels are easier to separate than real data.
- Counts, running time, plank duration, and jump height require a standard
  measurement protocol.
- Exercise-form features require a reliable pose-estimation component.
- The model has not been validated across ages, genders, regions, disability
  categories, training levels, camera conditions, or equipment.
- The deadlift assessment must not be performed without an approved load and
  qualified supervision.
- Sport recommendation is rule-based, not a separately trained model.
- Neither model may be used alone to accept, reject, rank, diagnose, or make an
  official decision about an athlete.

## Future improvements

1. Define official protocols and age-aware benchmarks with sports scientists.
2. Collect consented, coach-labelled real data for all seven exercises.
3. Train exercise-specific pose/form models instead of relying only on generic
   motion features.
4. Use athlete-wise, site-wise, and external-centre validation.
5. Add model calibration, confidence intervals, fairness checks, and monitoring.
6. Train a sport-recommendation model only after reliable sport labels exist.

## Safe interpretation

This is a reviewed college-level hackathon baseline. It demonstrates modular
data validation, leakage-safe preprocessing, training, evaluation, inference,
and backend integration. It is not a medical system, coaching replacement, or
official athlete-selection system.
