"""CV -> M1 bridge for all seven SIH25073 physical assessments.

The adapter accepts the new unified CV `measurement` contract and remains
backward-compatible with the teammate's older valid_reps JSON.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from ml.dataset import INPUT_FEATURES

CV_TEST_TO_FEATURE = {
    'pushup':'pushup_count', 'push-up':'pushup_count',
    'squat':'squat_count',
    'deadlift':'deadlift_reps',
    'running':'running_50m_seconds', '50m_running':'running_50m_seconds',
    'situp':'situp_count', 'sit-up':'situp_count',
    'plank':'plank_duration_seconds',
    'vertical_jump':'vertical_jump_cm', 'vertical-jump':'vertical_jump_cm',
}


def load_cv_result(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'CV result file not found: {path}')
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
    except json.JSONDecodeError as exc:
        raise ValueError(f'Invalid CV JSON in {path}: {exc}') from exc
    if not isinstance(data, dict):
        raise ValueError('CV JSON must contain an object.')
    return data


def cv_result_to_features(cv_result: dict[str, Any]) -> dict[str, float | int]:
    if not isinstance(cv_result, dict):
        raise TypeError('cv_result must be a dictionary.')
    status = str(cv_result.get('status','SUCCESS')).upper()
    if status not in {'SUCCESS','OK','COMPLETE'}:
        return {}

    # New all-7 contract: measurement already uses exact M1 feature names.
    measurement = cv_result.get('measurement')
    if isinstance(measurement, dict):
        mapped = {}
        for feature in INPUT_FEATURES:
            if feature in measurement and measurement[feature] is not None:
                mapped[feature] = measurement[feature]
        if mapped:
            return mapped

    # Backward compatibility with older teammate JSON.
    test = str(cv_result.get('test','')).strip().lower()
    feature = CV_TEST_TO_FEATURE.get(test)
    if not feature:
        return {}
    if feature in {'pushup_count','squat_count','deadlift_reps','situp_count'}:
        raw = cv_result.get('valid_reps', cv_result.get('reps'))
        if raw is None: return {}
        value = int(raw)
        if value < 0: raise ValueError('Repetition count cannot be negative.')
        return {feature:value}
    keys = {
        'running_50m_seconds': ('running_50m_seconds','elapsed_seconds','duration_seconds','time_seconds'),
        'plank_duration_seconds': ('plank_duration_seconds','duration_seconds','valid_hold_seconds'),
        'vertical_jump_cm': ('vertical_jump_cm','jump_height_cm'),
    }[feature]
    for key in keys:
        if cv_result.get(key) is not None:
            return {feature: float(cv_result[key])}
    return {}


def session_to_features(session: dict[str, Any]) -> dict[str, float | int]:
    if not isinstance(session, dict):
        raise TypeError('session must be a dictionary.')
    mapped = {}
    # session is normally {test_name: result_object}; also accept one result object.
    if 'test' in session:
        return cv_result_to_features(session)
    for result in session.values():
        if isinstance(result, dict):
            mapped.update(cv_result_to_features(result))
    return mapped


def merge_cv_results(athlete_profile: dict[str, Any], cv_results: list[dict[str, Any]], manual_assessments: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(athlete_profile, dict):
        raise TypeError('athlete_profile must be a dictionary.')
    payload = dict(athlete_profile)
    for result in cv_results:
        payload.update(cv_result_to_features(result))
    if manual_assessments:
        payload.update(manual_assessments)
    missing = [f for f in INPUT_FEATURES if payload.get(f) is None]
    if missing:
        raise ValueError('Incomplete M1 assessment. Missing: ' + ', '.join(missing))
    return {f: payload[f] for f in INPUT_FEATURES}


def merge_cv_session(athlete_profile: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    payload = dict(athlete_profile)
    payload.update(session_to_features(session))
    missing = [f for f in INPUT_FEATURES if payload.get(f) is None]
    if missing:
        raise ValueError('CV session is not complete. Missing: ' + ', '.join(missing))
    return {f: payload[f] for f in INPUT_FEATURES}


def build_prediction_from_cv(athlete_profile: dict[str, Any], cv_results: list[dict[str, Any]], manual_assessments: dict[str, Any] | None = None) -> dict[str, Any]:
    from ml.predict import predict_talent
    return predict_talent(merge_cv_results(athlete_profile, cv_results, manual_assessments))


def build_prediction_from_session(athlete_profile: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    from ml.predict import predict_talent
    return predict_talent(merge_cv_session(athlete_profile, session))


def main():
    parser = argparse.ArgumentParser(description='Run an M1 prediction from an all-7 CV session JSON.')
    parser.add_argument('--session', required=True, help='Path to cv_module/session_results.json')
    parser.add_argument('--age', type=int, required=True)
    parser.add_argument('--gender', required=True)
    parser.add_argument('--height', type=float, required=True)
    parser.add_argument('--weight', type=float, required=True)
    args = parser.parse_args()
    session = load_cv_result(args.session)
    profile = {'age':args.age,'gender':args.gender,'height_cm':args.height,'weight_kg':args.weight}
    print(json.dumps(build_prediction_from_session(profile, session), indent=2))

if __name__ == '__main__':
    main()
