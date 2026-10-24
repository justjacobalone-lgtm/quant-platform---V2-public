"""Live-public-data shadow analysis worker. It never places or signs orders."""
from __future__ import annotations
import json
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

from research.binance_public_feed import MarketDataError
from research.multi_exchange_feed import MultiExchangePublicFeed
from research.market_scanner import MarketSnapshot, WholeMarketScanner
from research.multi_agent import AgentArena

STOP = False

def _stop(_signum, _frame):
    global STOP
    STOP = True


def run_cycle(feed=None, scanner=None, arena=None, output_path=None):
    feed = feed or MultiExchangePublicFeed(coinbase_max_products=int(os.getenv("COINBASE_MAX_PRODUCTS", "40")))
    scanner = scanner or WholeMarketScanner(
        breakout_pct=float(os.getenv("BREAKOUT_PCT", "10")),
        breakdown_pct=float(os.getenv("BREAKDOWN_PCT", "-10")),
        max_per_minute=int(os.getenv("MAX_OPPORTUNITIES_PER_CYCLE", "100")),
    )
    arena = arena or AgentArena(int(os.getenv("AGENT_COUNT", "100")))
    raw = feed.fetch_markets()
    markets = [MarketSnapshot(
        exchange=x["exchange"], symbol=x["symbol"], price=x["price"],
        change_pct=x["change_pct"], volume_accel=x["volume_accel"],
        liquidity_score=x["liquidity_score"], momentum_score=x["momentum_score"],
        spread_bps=x["spread_bps"],
    ) for x in raw]
    opportunities = scanner.scan(markets)
    agent_results = arena.evaluate(opportunities)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "multi_exchange_public_spot_24h_tickers",
        "exchange_counts": {name: sum(1 for market in raw if market["exchange"] == name) for name in sorted({market["exchange"] for market in raw})},
        "feed_errors": getattr(feed, "errors", {}),
        "markets_scanned": len(markets),
        "opportunity_count": len(opportunities),
        "opportunities": [op.__dict__ for op in opportunities],
        "agent_count": len(agent_results),
        "agents": agent_results,
        "mode": "SHADOW", "orders_submitted": 0,
        "warning": "24-hour percent change is a screening signal, not a short-window breakout confirmation.",
    }
    destination = Path(output_path or os.getenv("SHADOW_RESULTS_PATH", "/data/shadow-results.jsonl"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
    print(json.dumps({k: payload[k] for k in ("timestamp", "markets_scanned", "opportunity_count", "agent_count", "mode", "orders_submitted")}), flush=True)
    return payload


def main():
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    interval = max(15, int(os.getenv("SHADOW_INTERVAL_SECONDS", "60")))
    print(f"shadow worker online; public market data; interval={interval}s; LIVE DISABLED", flush=True)
    while not STOP:
        started = time.monotonic()
        try:
            run_cycle()
        except MarketDataError as exc:
            print(f"market-data cycle failed: {exc}", flush=True)
        except Exception as exc:
            print(f"shadow cycle error: {type(exc).__name__}: {exc}", flush=True)
        elapsed = time.monotonic() - started
        deadline = time.monotonic() + max(1, interval - elapsed)
        while not STOP and time.monotonic() < deadline:
            time.sleep(min(1, deadline - time.monotonic()))
    print("shadow worker stopped", flush=True)

if __name__ == "__main__":
    main()
