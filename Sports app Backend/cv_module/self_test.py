"""Small logic checks that do not replace real-camera validation."""
from dataclasses import dataclass
from cv_module.tests.pushup import PushUpAnalyzer

@dataclass
class LM:
    x: float = 0.0
    y: float = 0.0
    visibility: float = 1.0


def frame(points):
    lms = [LM(0,0,0.1) for _ in range(33)]
    for idx, (x,y) in points.items():
        lms[idx] = LM(x,y,1.0)
    return lms


def pushup_false_positive_check():
    a = PushUpAnalyzer()
    # Standing body is vertical. Arm changes angle, but it must never count as a push-up.
    standing_straight = frame({12:(0.5,0.2),14:(0.5,0.35),16:(0.5,0.5),24:(0.5,0.55),28:(0.5,0.9)})
    standing_bent = frame({12:(0.5,0.2),14:(0.5,0.35),16:(0.65,0.35),24:(0.5,0.55),28:(0.5,0.9)})
    for _ in range(5):
        a.analyze(standing_straight)
        a.analyze(standing_bent)
    assert a.reps == 0, f'False positive: standing arm movement counted {a.reps} push-ups'


def pushup_cycle_check():
    a = PushUpAnalyzer()
    up = frame({12:(0.30,0.50),14:(0.25,0.60),16:(0.19,0.68),24:(0.55,0.50),28:(0.80,0.50)})
    down = frame({12:(0.30,0.50),14:(0.30,0.60),16:(0.40,0.60),24:(0.55,0.50),28:(0.80,0.50)})
    a.analyze(up); a.analyze(down); a.analyze(up)
    assert a.reps == 1, f'Expected one complete push-up cycle, got {a.reps}'


def main():
    pushup_false_positive_check()
    pushup_cycle_check()
    print('CV logic self-test passed.')
    print('Note: this checks code logic only; real-camera validation is still required.')

if __name__ == '__main__':
    main()
