import os
os.environ["LIVE_ENABLE_TOKEN"] = "test-token"
os.environ["ALLOW_LIVE_TRADING"] = "false"
from fastapi.testclient import TestClient
from backend.main import app
client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}

def test_health():
    assert client.get("/health").status_code == 200

def test_live_disabled_even_when_authenticated():
    r = client.post("/mode", headers=HEADERS, json={"mode":"LIVE"})
    assert r.status_code == 403

def test_unauthenticated_kill_blocked():
    assert client.post("/kill").status_code == 401

def test_kill_authenticated():
    assert client.post("/kill", headers=HEADERS).json()["status"] == "HALTED"
