import os, time, hmac, hashlib, json
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

APP_VERSION = "1.3.3-hardened"
app = FastAPI(title="Quant Platform OS Control Plane", version=APP_VERSION)

ALLOWED = {"PAPER", "SHADOW", "LIVE_CANDIDATE", "LIVE"}
ROLES = {"viewer", "operator", "admin"}
STATE = {
    "mode": os.getenv("TRADING_MODE", "PAPER").upper(),
    "halted": True,
    "live_approved": False,
    "started_at": time.time(),
}

class ModeRequest(BaseModel):
    mode: str = Field(min_length=1)
    approval_token: str | None = None

class Principal:
    def __init__(self, role: str): self.role = role

def _token_ok(provided: str | None, expected: str | None) -> bool:
    return bool(provided and expected and hmac.compare_digest(provided.encode(), expected.encode()))

def require_auth(x_admin_token: str | None = Header(default=None), authorization: str | None = Header(default=None)) -> Principal:
    # Legacy token is opt-in and intended only for migration.
    if os.getenv("ALLOW_LEGACY_ADMIN_TOKEN", "false").lower() == "true" and _token_ok(x_admin_token, os.getenv("ADMIN_TOKEN")):
        return Principal("admin")
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if _token_ok(token, os.getenv("LIVE_ENABLE_TOKEN")):
        return Principal("admin")
    raise HTTPException(status_code=401, detail="authentication required")

def require_operator(principal: Principal = Depends(require_auth)) -> Principal:
    if principal.role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="operator role required")
    return principal

def require_admin(principal: Principal = Depends(require_auth)) -> Principal:
    if principal.role != "admin": raise HTTPException(status_code=403, detail="admin role required")
    return principal

@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION, "mode": STATE["mode"], "halted": STATE["halted"], "live_approved": STATE["live_approved"]}

@app.get("/status")
def status():
    return dict(STATE)

@app.post("/kill")
def kill(_: Principal = Depends(require_operator)):
    STATE["halted"] = True
    STATE["live_approved"] = False
    return {"ok": True, "status": "HALTED"}

@app.post("/resume")
def resume(_: Principal = Depends(require_operator)):
    if STATE["mode"] == "LIVE" and not STATE["live_approved"]:
        raise HTTPException(status_code=409, detail="LIVE approval required")
    STATE["halted"] = False
    return {"ok": True, "status": "RUNNING", "mode": STATE["mode"]}

@app.post("/live/approve")
def approve_live(_: Principal = Depends(require_admin)):
    if os.getenv("ALLOW_LIVE_TRADING", "false").lower() != "true":
        raise HTTPException(status_code=403, detail="live trading disabled by configuration")
    STATE["live_approved"] = True
    return {"ok": True, "live_approved": True}

@app.post("/live/revoke")
def revoke_live(_: Principal = Depends(require_admin)):
    STATE["live_approved"] = False
    if STATE["mode"] == "LIVE": STATE["mode"] = "LIVE_CANDIDATE"
    STATE["halted"] = True
    return {"ok": True, "live_approved": False, "status": "HALTED"}

@app.post("/mode")
def set_mode(req: ModeRequest, _: Principal = Depends(require_operator)):
    mode = req.mode.upper()
    if mode not in ALLOWED: raise HTTPException(status_code=400, detail="invalid mode")
    if mode == "LIVE":
        if os.getenv("ALLOW_LIVE_TRADING", "false").lower() != "true":
            raise HTTPException(status_code=403, detail="live trading disabled by configuration")
        if not STATE["live_approved"]: raise HTTPException(status_code=403, detail="explicit LIVE approval required")
        if STATE["halted"]: raise HTTPException(status_code=409, detail="system is halted")
    if mode == "LIVE_CANDIDATE" and STATE["mode"] == "PAPER":
        raise HTTPException(status_code=409, detail="shadow validation required")
    STATE["mode"] = mode
    if mode != "LIVE": STATE["live_approved"] = False
    return {"ok": True, "mode": mode}


@app.get("/api/dashboard")
def dashboard_data():
    """Read-only dashboard snapshot; never submits orders."""
    results_path = Path(os.getenv("SHADOW_RESULTS_PATH", "/data/shadow-results.jsonl"))
    latest = None
    if results_path.exists():
        try:
            with results_path.open("rb") as handle:
                lines = handle.readlines()[-5:]
            if lines:
                latest = json.loads(lines[-1].decode("utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            latest = None
    return {"service": "Quant Platform OS", "version": APP_VERSION, "mode": STATE["mode"], "halted": STATE["halted"], "live_approved": STATE["live_approved"], "live_trading_configured": os.getenv("ALLOW_LIVE_TRADING", "false").lower() == "true", "shadow": latest}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Serve the phone-friendly, read-only dashboard."""
    page = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"
    return HTMLResponse(page.read_text(encoding="utf-8"))
