import json, os, time
from pathlib import Path

AUDIT_FILE = Path(os.getenv("AUDIT_FILE", "/tmp/quant-audit.jsonl"))

def record(event_type: str, actor: str, payload: dict):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": time.time(),
        "event_type": event_type,
        "actor": actor,
        "payload": payload,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")
    return event
