from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / 'results'
SESSION_PATH = ROOT / 'session_results.json'


def save_result(result: dict) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    test = str(result.get('test','unknown'))
    path = RESULTS_DIR / f'{test}.json'
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    session = load_session()
    session[test] = result
    SESSION_PATH.write_text(json.dumps(session, indent=2), encoding='utf-8')
    return path


def load_session() -> dict:
    if not SESSION_PATH.exists():
        return {}
    try:
        data = json.loads(SESSION_PATH.read_text(encoding='utf-8-sig'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def clear_session():
    SESSION_PATH.write_text('{}\n', encoding='utf-8')
