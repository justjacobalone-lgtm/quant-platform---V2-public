# Quant Platform OS

Production-oriented deployment pack for an automated quantitative trading platform.

## Safety model

The system starts in `PAPER` mode. Promotion is explicit:

`PAPER -> SHADOW -> LIVE_CANDIDATE -> LIVE`

Live mode requires an operator approval token and a second safety gate. Live exchange credentials are never stored in the Android client.

## Quick start

### VPS
```bash
chmod +x deploy/*.sh
./deploy/one-click.sh
```

The installer creates `.env`, validates Docker, builds the services, runs health checks, and starts the stack.

### Local
```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8080/health
```

## Services

- `api`: authenticated control plane
- `engine`: execution/risk state machine
- `worker`: simulation/shadow research worker
- `postgres`: durable state
- `redis`: event transport
- `prometheus`: metrics
- `grafana`: monitoring

This package is an executable deployment foundation, not a claim that a live-money trading strategy is profitable or that a deployment is independently certified as a regulated investment fund.

## v1.3.4 hardening additions

- Whole-market scanner evaluates every market supplied by connected exchange feeds.
- `+10%` breakout and `-10%` breakdown moves promote a market for specialist analysis; they do not automatically place an order.
- Opportunity ranking incorporates move magnitude, volume acceleration, liquidity, momentum, and spread penalty.
- Per-position emergency loss boundary defaults to 10% below entry.
- Profitable positions can exit or tighten protection when momentum decays.
- Safety tests are configured to run from the repository root with `pytest`.

The package remains `PAPER` by default. Live execution is not enabled by these additions.

## Public-data shadow research (added in the V2 work copy)

The shadow worker now polls Binance's unauthenticated public Spot endpoints, scans active USDT-quoted Spot symbols, evaluates the configured research-agent league, and appends JSON Lines results to `/data/shadow-results.jsonl` in a persistent Docker volume. It does not sign exchange requests or place orders. Set `AGENT_COUNT` (default `100`) and `SHADOW_INTERVAL_SECONDS` (default `60`) in `.env` to configure the research cycle.

Important limitations: the first feed uses 24-hour ticker change, not a completed 5-minute/1-minute candle breakout detector; volume acceleration and liquidity are screening proxies; the 100 agents are deterministic parameter variants for research comparison, not trained AI, not proven profitable, and not yet an evolutionary learning system. Results are shadow research only. `ALLOW_LIVE_TRADING=false` remains the required default. Review the logs and test report before deploying to a server.
