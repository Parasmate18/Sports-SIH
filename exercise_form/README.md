# Separate Seven-Exercise Form Assessment

This component is separate from the main talent-level model. It predicts
whether one recorded exercise segment has correct or incorrect form, or returns
uncertain when confidence is below the configured threshold.

Supported exercise_type values:

- pushup
- squat
- deadlift
- running
- situp
- plank
- vertical_jump

A correct form label does not mean that an athlete is Advanced or Elite.

## Original push-up component

legacy_pushup/ is an unchanged backup of the complete original push-up-only
component from the uploaded ZIP, including its code, data, model, test set,
reports, README, and requirements.

## Synthetic-data warning

The active multi-exercise CSV is synthetic demonstration data. Its form labels
and generated metrics cannot establish real-world correctness, coaching
quality, injury risk, or safety. Real deployment needs exercise-specific
coach-labelled videos, reliable pose landmarks, and independent validation.

Deadlift must always use qualified supervision and an approved safe load.

## Input contract

Every CSV row requires:

| Column | Meaning |
| --- | --- |
| athlete_id | Athlete identifier |
| video_id | Video or capture identifier |
| sample_number | Segment number within the video |
| exercise_type | One of the seven supported exercise names |
| primary_joint_min_angle | Minimum main-joint angle in degrees |
| primary_joint_max_angle | Maximum main-joint angle in degrees |
| torso_deviation_degrees | Torso deviation from the exercise-specific reference |
| range_of_motion_degrees | Main-joint range of motion |
| stability_score | Demonstration stability score from 0 to 100 |
| movement_speed | Normalised movement-speed value |
| assessment_duration_seconds | Duration of the repetition or assessment segment |
| landmark_confidence | Pose landmark confidence from 0 to 1 |
| visibility_score | Required-landmark visibility from 0 to 1 |
| label | correct or incorrect |

exercise_type is one-hot encoded. Numerical fields use median imputation and
standardisation. These transformations and the Random Forest are saved inside
one Scikit-learn Pipeline.

## Files

| File | Purpose |
| --- | --- |
| ml/dataset.py | Validates seven exercise types, form labels, ranges, missing values, duplicates, and athlete-wise splitting. |
| ml/preprocessing.py | Validates prediction data and builds numeric plus categorical preprocessing. |
| ml/model.py | Builds, saves, loads, predicts with, and explains the form model. |
| ml/train.py | Trains the multi-exercise model and saves a held-out test set. |
| ml/evaluate.py | Creates metrics, predictions, feature importance, and a confusion matrix. |
| ml/predict.py | Provides a runnable squat-form example. |
| data/processed/exercise_features.csv | Balanced synthetic data for seven exercise types. |
| artifacts/exercise_model.joblib | Complete fitted model bundle. |
| artifacts/test_set.csv | Athlete-separated test records. |
| reports/metrics.json | Actual synthetic evaluation metrics and warning. |
| reports/predictions.csv | Test labels, predictions, and confidence values. |
| reports/confusion_matrix.png | Correct/incorrect confusion matrix. |

## Commands

Run from the main SIH25073_M1_ML project root:

    pip install -r requirements.txt
    python -m exercise_form.ml.train
    python -m exercise_form.ml.evaluate
    python -m exercise_form.ml.predict

## Latest verified demonstration results

- Cleaned rows: 112
- Unique athletes: 56
- Training rows: 88
- Testing rows: 24
- Test accuracy: 1.0000
- Weighted precision: 1.0000
- Weighted recall: 1.0000
- Weighted F1: 1.0000

The perfect test result occurs on deliberately structured synthetic data and is
not a claim of real form-classification accuracy.

## Backend usage

    from exercise_form.ml.model import predict_exercise

    features = {
        "exercise_type": "squat",
        "primary_joint_min_angle": 68,
        "primary_joint_max_angle": 169,
        "torso_deviation_degrees": 7,
        "range_of_motion_degrees": 101,
        "stability_score": 89,
        "movement_speed": 0.58,
        "assessment_duration_seconds": 2.1,
        "landmark_confidence": 0.95,
        "visibility_score": 0.96,
    }

    result = predict_exercise(features)

Actual verified demonstration output:

    {
      "exercise_type": "squat",
      "label": "correct",
      "raw_prediction": "correct",
      "confidence": 1.0,
      "form_score": 100.0,
      "model_version": "1.1.0",
      "warning": "AI-assisted form feedback only; it is not medical advice or an official coach assessment. Deadlift must be performed with qualified supervision."
    }

## Limitations and next work

- The dataset does not come from real videos.
- Generic movement features cannot replace exercise-specific biomechanical
  features and coaching criteria.
- Plank and running are assessment segments rather than normal repetitions.
- Camera position, occlusion, clothing, body proportions, disability
  categories, and equipment can alter pose measurements.
- Thresholds and labels require approval from coaches and sports scientists.
- Separate exercise-specific models may be more reliable after enough real data
  is collected.
