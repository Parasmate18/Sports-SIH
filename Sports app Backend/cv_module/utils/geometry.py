from __future__ import annotations
import math
from typing import Iterable


def xy(p):
    return (float(p.x), float(p.y))


def distance(a, b) -> float:
    return math.hypot(float(a.x) - float(b.x), float(a.y) - float(b.y))


def calculate_angle(a, b, c) -> float:
    bax, bay = float(a.x) - float(b.x), float(a.y) - float(b.y)
    bcx, bcy = float(c.x) - float(b.x), float(c.y) - float(b.y)
    denom = math.hypot(bax, bay) * math.hypot(bcx, bcy)
    if denom <= 1e-9:
        return float('nan')
    cosine = max(-1.0, min(1.0, (bax * bcx + bay * bcy) / denom))
    return math.degrees(math.acos(cosine))


def line_angle_from_horizontal(a, b) -> float:
    dx = float(b.x) - float(a.x)
    dy = float(b.y) - float(a.y)
    if abs(dx) + abs(dy) <= 1e-9:
        return float('nan')
    angle = abs(math.degrees(math.atan2(dy, dx))) % 180.0
    return min(angle, 180.0 - angle)


def line_angle_from_vertical(a, b) -> float:
    h = line_angle_from_horizontal(a, b)
    return abs(90.0 - h) if math.isfinite(h) else h


def visible(points: Iterable, threshold: float = 0.55) -> bool:
    for p in points:
        v = getattr(p, 'visibility', 1.0)
        if v is not None and float(v) < threshold:
            return False
    return True


def valid_angle(value: float, low: float = 5.0, high: float = 179.5) -> bool:
    return math.isfinite(value) and low <= value <= high


def choose_side(landmarks, left_ids, right_ids, threshold: float = 0.55):
    left = [landmarks[i] for i in left_ids]
    right = [landmarks[i] for i in right_ids]
    lscore = sum(float(getattr(p, 'visibility', 1.0) or 0.0) for p in left) / len(left)
    rscore = sum(float(getattr(p, 'visibility', 1.0) or 0.0) for p in right) / len(right)
    pts = left if lscore >= rscore else right
    return pts if visible(pts, threshold) else None
