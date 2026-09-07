from __future__ import annotations
import json
from cv_module.main import run_test, TESTS
from cv_module.session_store import clear_session, load_session
from ml.cv_adapter import build_prediction_from_session


def read_profile():
    print('\nATHLETE PROFILE')
    return {
        'age': int(input('Age: ').strip()),
        'gender': input('Gender (Male/Female/Other): ').strip().title(),
        'height_cm': float(input('Height (cm): ').strip()),
        'weight_kg': float(input('Weight (kg): ').strip()),
    }


def main():
    profile = read_profile()
    clear_session()
    print('\nEach test opens the camera. Complete the real test and finish it with Q/ESC.')
    print('For 50 m running, use a measured 50 m course and press S at start, F at finish.')
    print('Deadlift must use a safe expert-approved standard load under supervision.\n')
    for choice in '1234567':
        name, key, cls = TESTS[choice]
        input(f'\nPress ENTER when ready for: {name}')
        height = profile['height_cm'] if key == 'vertical_jump' else None
        run_test(name, key, cls, athlete_height_cm=height)
    session = load_session()
    print('\nALL CV RESULTS')
    print(json.dumps(session, indent=2))
    try:
        prediction = build_prediction_from_session(profile, session)
    except Exception as exc:
        print('\nM1 prediction blocked because the CV session is incomplete/invalid:')
        print(exc)
        return
    print('\nFINAL M1 PREDICTION')
    print(json.dumps(prediction, indent=2))

if __name__ == '__main__':
    main()
