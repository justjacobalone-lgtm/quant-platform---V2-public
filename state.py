import json, os, time
from pathlib import Path

STATE_FILE = Path(os.getenv("STATE_FILE", "/tmp/quant-state.json"))

DEFAULT = {
    "mode": "PAPER",
    "halted": False,
    "updated_at": 0,
    "reason": "startup"
}

def load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return DEFAULT.copy()

def save(state):
    state["updated_at"] = time.time()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(STATE_FILE)
    return state
