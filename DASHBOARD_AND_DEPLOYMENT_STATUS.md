# Dashboard and Deployment Status — 2026-10-21

## Included
- Phone-friendly read-only dashboard at `/`.
- Dashboard JSON endpoint at `/api/dashboard`.
- Shows system mode, halt state, markets scanned, breakout screening candidates, agent evaluations, public feed coverage/errors, and latest shadow cycle.
- Refreshes every 15 seconds.
- `/health` and FastAPI `/docs` remain available.
- Existing shadow worker submits zero orders; live mode is not enabled by this dashboard.

## Verified locally
- `python -m compileall -q backend research shadow`: passed.
- `pytest -q`: 13 tests passed.
- FastAPI TestClient: `/`, `/api/dashboard`, and `/health` returned HTTP 200.

## Not yet verified
- Docker image build and `docker compose` startup: Docker is not installed in the build environment, so container startup was not tested.
- Public internet market feed calls and sustained worker operation were not live-tested here.
- No server has been provisioned or deployed, so there is no live URL yet.

## Important limitations
The current shadow worker screens using 24-hour ticker change and deterministic research-agent parameter variants. This is not yet the requested short-window candlestick breakout engine with trained/evolving AI agents. The dashboard must not be interpreted as evidence of profitability. Keep `ALLOW_LIVE_TRADING=false`.
