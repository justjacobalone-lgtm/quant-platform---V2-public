# Free-host deployment (dashboard + public-data shadow scan)

This repo includes a Render Blueprint (`render.yaml`) and a root `Dockerfile` for a free web-service deployment. It starts the read-only FastAPI dashboard and the public-market shadow worker in one service. The worker scans public exchange data and writes its latest cycles to `/tmp/shadow-results.jsonl`.

## Deploy
1. Put this project directory in a Git repository that your hosting provider can read.
2. In Render, create a **Blueprint** from that repository and select `render.yaml`.
3. Review the service settings, then create/deploy the service.
4. When deployment finishes, open the generated `https://...onrender.com` URL. Verify `/health`, `/api/dashboard`, and `/`.

## Free-tier limitations
- The free web service can sleep after inactivity; a sleeping service does not continuously scan markets.
- `/tmp` is ephemeral. Latest shadow results can be lost after restart/sleep.
- This is a dashboard and shadow research deployment, not a production-grade always-on trading server.
- The current worker screens 24-hour ticker changes; it is not the requested short-window candlestick breakout engine. The 100 agents are deterministic research variants, not trained/evolving AI.
- `ALLOW_LIVE_TRADING=false` is hard-coded as the container default. No exchange credentials are needed for public data, and this service does not submit orders.

For continuous 24/7 scanning with durable data, use an always-on server and separate worker/database services; that generally is not available at $0 on mainstream hosting.
