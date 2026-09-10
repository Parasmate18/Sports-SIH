from cv_module.utils.geometry import choose_side

class Running50mAnalyzer:
    """CV-assisted timer. The course itself must be physically measured as 50 m."""
    def __init__(self):
        self.steps = 0
        self.last_leg_state = None
        self.started_at = None
        self.finished_at = None
        self.elapsed_seconds = None
        self.stage = 'READY'

    def start(self, timestamp_ms):
        self.started_at = int(timestamp_ms)
        self.finished_at = None
        self.elapsed_seconds = None
        self.steps = 0
        self.last_leg_state = None
        self.stage = 'RUNNING'

    def finish(self, timestamp_ms):
        if self.started_at is None:
            return False
        self.finished_at = int(timestamp_ms)
        self.elapsed_seconds = max(0.0, (self.finished_at-self.started_at)/1000.0)
        self.stage = 'FINISHED'
        return True

    def analyze(self, landmarks, timestamp_ms=None):
        pts = choose_side(landmarks, [23,25,27], [24,26,28], threshold=0.45)
        # Step cadence uses both ankles when available.
        try:
            la, ra = landmarks[27], landmarks[28]
            diff = float(la.y) - float(ra.y)
            state = 1 if diff > 0.035 else (-1 if diff < -0.035 else 0)
            if self.stage == 'RUNNING' and state != 0 and self.last_leg_state not in (None,0,state):
                self.steps += 1
            if state != 0:
                self.last_leg_state = state
        except Exception:
            pass
        return {'test':'running','steps':self.steps,'elapsed_seconds':self.elapsed_seconds,'stage':self.stage,
                'person_detected':pts is not None,'valid_posture':pts is not None}
