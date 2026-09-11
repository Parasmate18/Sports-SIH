from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
import cv2

from cv_module.pose_detector import PoseDetector
from cv_module.session_store import save_result, load_session, clear_session
from cv_module.tests.pushup import PushUpAnalyzer
from cv_module.tests.squat import SquatAnalyzer
from cv_module.tests.deadlift import DeadliftAnalyzer
from cv_module.tests.running import Running50mAnalyzer
from cv_module.tests.situp import SitUpAnalyzer
from cv_module.tests.plank import PlankAnalyzer
from cv_module.tests.vertical_jump import VerticalJumpAnalyzer

TESTS = {
    '1': ('Push-up', 'pushup', PushUpAnalyzer),
    '2': ('Squat', 'squat', SquatAnalyzer),
    '3': ('Deadlift', 'deadlift', DeadliftAnalyzer),
    '4': ('50 m Running', 'running', Running50mAnalyzer),
    '5': ('Sit-up', 'situp', SitUpAnalyzer),
    '6': ('Plank', 'plank', PlankAnalyzer),
    '7': ('Vertical Jump', 'vertical_jump', VerticalJumpAnalyzer),
}


def _make_analyzer(test_key, athlete_height_cm=None):
    if test_key == 'vertical_jump':
        if athlete_height_cm is None:
            athlete_height_cm = float(input('Enter athlete height in cm for jump calibration: ').strip())
        return VerticalJumpAnalyzer(athlete_height_cm)
    cls = next(cls for _, key, cls in TESTS.values() if key == test_key)
    return cls()


def _measurement(test_key, analyzer):
    if test_key == 'pushup': return {'pushup_count': int(analyzer.reps)}
    if test_key == 'squat': return {'squat_count': int(analyzer.reps)}
    if test_key == 'deadlift': return {'deadlift_reps': int(analyzer.reps)}
    if test_key == 'running': return {'running_50m_seconds': analyzer.elapsed_seconds}
    if test_key == 'situp': return {'situp_count': int(analyzer.reps)}
    if test_key == 'plank': return {'plank_duration_seconds': round(float(analyzer.duration_seconds), 2)}
    if test_key == 'vertical_jump': return {'vertical_jump_cm': round(float(analyzer.jump_height_cm), 2)}
    return {}


def run_test(test_name, test_key, AnalyzerClass=None, athlete_height_cm=None, camera_index=0):
    print('\n' + '='*58)
    print(f'Starting {test_name} test')
    print('='*58)
    if test_key == 'deadlift':
        print('SAFETY: use only an expert-approved standard load with trained supervision.')
    if test_key == 'running':
        print('Use a physically measured 50 m course. Press S at the start and F at the finish.')
        print('The camera validates body movement/steps; it does NOT measure 50 m distance.')
    if test_key == 'vertical_jump':
        print('Stand still for ~1 second first so the camera can calibrate against athlete height.')
    print('Press Q or ESC to finish the camera test.\n')

    analyzer = _make_analyzer(test_key, athlete_height_cm)
    detector = PoseDetector()
    camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        detector.close()
        raise RuntimeError('Camera could not be opened.')
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    start_clock = time.monotonic()
    frames_processed = 0
    person_frames = 0
    last_data = {}
    window = f'SIH25073 - {test_name}'
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 1000, 700)

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frames_processed += 1
            timestamp_ms = max(1, int((time.monotonic()-start_clock)*1000))
            result = detector.detect(frame, timestamp_ms)
            person = bool(result.pose_landmarks)
            if person:
                person_frames += 1
                landmarks = result.pose_landmarks[0]
                try:
                    last_data = analyzer.analyze(landmarks, timestamp_ms)
                except Exception as exc:
                    last_data = {'stage': 'ANALYZER_ERROR', 'error': str(exc)}
                h, w = frame.shape[:2]
                for lm in landmarks:
                    if float(getattr(lm,'visibility',1.0) or 0.0) >= 0.45:
                        cv2.circle(frame, (int(lm.x*w), int(lm.y*h)), 3, (0,255,0), -1)
            else:
                last_data = {'stage':'PERSON_NOT_DETECTED'}

            cv2.putText(frame, test_name.upper(), (35,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
            stage = str(last_data.get('stage',''))
            cv2.putText(frame, f'STAGE: {stage}', (35,90), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
            if hasattr(analyzer,'reps'):
                cv2.putText(frame, f'REPS: {analyzer.reps}', (35,130), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            if test_key == 'plank':
                cv2.putText(frame, f'VALID HOLD: {analyzer.duration_seconds:.1f}s', (35,130), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            if test_key == 'running':
                elapsed = analyzer.elapsed_seconds
                if analyzer.started_at is not None and analyzer.finished_at is None:
                    elapsed = (timestamp_ms-analyzer.started_at)/1000.0
                cv2.putText(frame, f'TIMER: {elapsed:.2f}s' if elapsed is not None else 'TIMER: READY', (35,130), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                cv2.putText(frame, f'STEPS: {analyzer.steps}', (35,170), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
                cv2.putText(frame, 'S=start  F=finish', (35,210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            if test_key == 'vertical_jump':
                cv2.putText(frame, f'JUMP: {analyzer.jump_height_cm:.1f} cm', (35,130), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            cv2.putText(frame, 'Q / ESC = finish', (35, frame.shape[0]-25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 2)
            cv2.imshow(window, frame)

            key = cv2.waitKeyEx(1)
            if test_key == 'running' and key in (ord('s'),ord('S')):
                if person:
                    analyzer.start(timestamp_ms)
                    print('50 m timer STARTED')
                else:
                    print('Start ignored: person not detected.')
            elif test_key == 'running' and key in (ord('f'),ord('F')):
                if analyzer.finish(timestamp_ms):
                    print(f'50 m timer FINISHED: {analyzer.elapsed_seconds:.2f} s')
                else:
                    print('Finish ignored: press S first.')
            elif key in (ord('q'),ord('Q'),27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        detector.close()
        for _ in range(3):
            cv2.waitKey(1)

    measurement = _measurement(test_key, analyzer)
    # A running result without a start/finish time must not silently become 0.
    if test_key == 'running' and measurement['running_50m_seconds'] is None:
        status = 'INCOMPLETE'
    elif person_frames == 0:
        status = 'INCOMPLETE'
    else:
        status = 'SUCCESS'

    result_data = {
        'test': test_key,
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'person_detected': person_frames > 0,
        'frames_processed': frames_processed,
        'person_frames': person_frames,
        'measurement': measurement,
        'features': {k:v for k,v in last_data.items() if k not in {'test','reps','stage','valid_posture'}},
        'quality': {
            'last_stage': last_data.get('stage'),
            'last_frame_valid_posture': bool(last_data.get('valid_posture', False)),
            'invalid_frames': int(getattr(analyzer,'invalid_frames',0)),
        }
    }
    if hasattr(analyzer,'reps'):
        result_data['valid_reps'] = int(analyzer.reps)
    if test_key == 'running':
        result_data['steps'] = int(analyzer.steps)
        result_data['distance_protocol'] = 'physically measured 50 m course required'
        result_data['timing_method'] = 'operator start/finish keys with CV movement validation'
    if test_key == 'vertical_jump':
        result_data['calibration'] = 'athlete-height single-camera estimate; validate against a measured reference before official use'
    if test_key == 'deadlift':
        result_data['safety'] = 'expert-approved standard load and trained supervision required'

    path = save_result(result_data)
    print('\nRESULT')
    print(json.dumps(result_data, indent=2))
    print(f'\nSaved: {path}')
    return result_data


def main():
    while True:
        print('\n' + '='*44)
        print('      ASSESSMENT')
        print('='*44)
        for choice, (name, _, _) in TESTS.items():
            print(f'{choice}. {name}')
        print('A. Show current session results')
        print('C. Clear current session')
        print('Q. Exit')
        choice = input('\nEnter choice: ').strip().lower()
        if choice == 'q':
            break
        if choice == 'a':
            print(json.dumps(load_session(), indent=2))
            continue
        if choice == 'c':
            clear_session(); print('Session cleared.'); continue
        if choice not in TESTS:
            print('Invalid choice.'); continue
        name, key, cls = TESTS[choice]
        run_test(name, key, cls)

if __name__ == '__main__':
    main()
