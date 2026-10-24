# Multi-exchange public market data

The shadow worker now uses `research.multi_exchange_feed.MultiExchangePublicFeed` by default.
It aggregates unauthenticated public spot snapshots from Binance, Kraken, and Coinbase Exchange.

## Configuration

```dotenv
PUBLIC_MARKET_EXCHANGES=binance,kraken,coinbase
COINBASE_MAX_PRODUCTS=40
SHADOW_INTERVAL_SECONDS=60
BREAKOUT_PCT=10
MAX_OPPORTUNITIES_PER_CYCLE=100
```

`COINBASE_MAX_PRODUCTS` is currently applied through the feed constructor (default 40); to change it in the worker, set the constructor argument in `shadow/worker.py` or wire the environment variable there. The cap avoids an unbounded burst of public requests because Coinbase Exchange exposes per-product ticker/stat endpoints.

## Normalized snapshot fields

Each exchange produces the shared fields `exchange`, `symbol`, `price`, `change_pct`,
`quote_volume_24h`, `trade_count_24h`, `volume_accel`, `liquidity_score`,
`momentum_score`, `spread_bps`, and `observed_at`.

These are research/monitoring values. The volume acceleration, liquidity, and momentum scores
are simple proxies, not exchange-provided institutional metrics. The current opportunity scanner
uses 24-hour change as a broad screening signal; it does not yet confirm a short-window
candlestick breakout.

## Safety and operational limits

- Public market data only; no credentials are required for these feed calls.
- This code does not place, sign, or authorize orders.
- If one exchange fails, available markets from the other enabled exchanges are retained and
  the error is included in the worker result.
- If every enabled exchange fails, the cycle raises a `MarketDataError`.
- The automated tests use canned API responses. They validate parsing and aggregation, not
  live network reachability or the exchanges' current availability.
