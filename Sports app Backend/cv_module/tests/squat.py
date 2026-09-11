from cv_module.utils.geometry import calculate_angle, choose_side, line_angle_from_vertical, valid_angle

class SquatAnalyzer:
    def __init__(self):
        self.reps = 0
        self.stage = 'WAITING'
        self.standing_hip_y = None
        self.invalid_frames = 0

    def analyze(self, landmarks, timestamp_ms=None):
        pts = choose_side(landmarks, [11,23,25,27], [12,24,26,28])
        if not pts:
            self.invalid_frames += 1
            return {'test':'squat','reps':self.reps,'stage':'LANDMARKS_NOT_VISIBLE','valid_posture':False}
        shoulder, hip, knee, ankle = pts
        knee_angle = calculate_angle(hip, knee, ankle)
        torso_lean = line_angle_from_vertical(hip, shoulder)
        if not valid_angle(knee_angle) or torso_lean > 55:
            self.invalid_frames += 1
            return {'test':'squat','reps':self.reps,'knee_angle':round(knee_angle,2) if valid_angle(knee_angle) else None,
                    'torso_lean':round(torso_lean,2),'stage':'INVALID_POSTURE','valid_posture':False}
        if knee_angle >= 160:
            if self.standing_hip_y is None:
                self.standing_hip_y = float(hip.y)
            else:
                self.standing_hip_y = 0.9*self.standing_hip_y + 0.1*float(hip.y)
            if self.stage == 'DOWN':
                self.reps += 1
            self.stage = 'UP'
        elif knee_angle <= 105 and self.stage in {'UP','WAITING'}:
            lowered = self.standing_hip_y is None or float(hip.y) >= self.standing_hip_y + 0.035
            if lowered:
                self.stage = 'DOWN'
        return {'test':'squat','reps':self.reps,'knee_angle':round(knee_angle,2),'torso_lean':round(torso_lean,2),
                'stage':self.stage,'valid_posture':True}
