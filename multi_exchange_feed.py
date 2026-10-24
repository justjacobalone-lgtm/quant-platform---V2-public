"""Read-only public market data for Binance, Kraken and Coinbase Exchange.

This module never signs requests or submits orders. It normalizes exchange-specific
responses to the market snapshot schema consumed by the scanner.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from research.binance_public_feed import BinancePublicFeed, MarketDataError

KRAKEN_BASE = "https://api.kraken.com"
COINBASE_BASE = "https://api.exchange.coinbase.com"


def _http_json(url: str, timeout: float = 12.0) -> Any:
    req = Request(url, headers={
        "User-Agent": "QuantPlatformOS-readonly-market-data/1.0",
        "Accept": "application/json",
    })
    try:
        with urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise MarketDataError(f"HTTP {response.status}: {url}")
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MarketDataError(f"Public market-data request failed for {url}: {exc}") from exc


def _snapshot(exchange: str, symbol: str, price: float, open_price: float,
              volume: float, count: int = 0, bid: float = 0.0, ask: float = 0.0) -> dict[str, Any] | None:
    if price <= 0:
        return None
    change = ((price - open_price) / open_price * 100.0) if open_price > 0 else 0.0
    mid = (bid + ask) / 2 if bid > 0 and ask >= bid else price
    spread = ((ask - bid) / mid * 10000.0) if bid > 0 and ask >= bid and mid > 0 else 100.0
    return {
        "exchange": exchange, "symbol": symbol, "price": price,
        "change_pct": change, "quote_volume_24h": max(0.0, volume),
        "trade_count_24h": max(0, count),
        "volume_accel": min(10.0, max(0, count) / 10000.0),
        "liquidity_score": min(100.0, max(0.0, volume) / 100000.0),
        "momentum_score": min(100.0, abs(change) * 4.0),
        "spread_bps": max(0.0, spread), "observed_at": time.time(),
    }


class KrakenPublicFeed:
    """Fetch Kraken public 24h tickers; no API key is required."""

    def __init__(self, quote_assets: tuple[str, ...] = ("USD", "USDT", "USDC"),
                 timeout: float = 12.0, request_json: Callable[[str, float], Any] | None = None):
        self.quote_assets = tuple(x.upper() for x in quote_assets)
        self.timeout = timeout
        self._request_json = request_json or _http_json

    def fetch_markets(self) -> list[dict[str, Any]]:
        data = self._request_json(KRAKEN_BASE + "/0/public/Ticker", self.timeout)
        if data.get("error"):
            raise MarketDataError(f"Kraken API error: {data['error']}")
        result = data.get("result", {})
        snapshots = []
        for pair, ticker in result.items():
            # Kraken internal pair names vary, so filter by the public pair key.
            compact = pair.upper().replace("/", "").replace("-", "")
            quote_ok = any(compact.endswith(q) for q in self.quote_assets)
            if not quote_ok:
                continue
            try:
                price = float(ticker["c"][0])
                open_price = float(ticker["o"])
                volume_base = float(ticker["v"][1])
                volume_quote = volume_base * price
                bid = float(ticker["b"][0])
                ask = float(ticker["a"][0])
                row = _snapshot("kraken", pair, price, open_price, volume_quote,
                                bid=bid, ask=ask)
                if row:
                    snapshots.append(row)
            except (KeyError, TypeError, ValueError, IndexError):
                continue
        snapshots.sort(key=lambda x: x["quote_volume_24h"], reverse=True)
        return snapshots


class CoinbasePublicFeed:
    """Fetch a bounded set of Coinbase Exchange USD/USDT/USDC tickers.

    Coinbase's public API has a per-product ticker endpoint. To avoid firing
    hundreds of requests in one cycle, max_products is bounded and configurable.
    """

    def __init__(self, quote_assets: tuple[str, ...] = ("USD", "USDT", "USDC"),
                 max_products: int = 40, timeout: float = 12.0,
                 request_json: Callable[[str, float], Any] | None = None):
        self.quote_assets = tuple(x.upper() for x in quote_assets)
        self.max_products = max(1, min(int(max_products), 100))
        self.timeout = timeout
        self._request_json = request_json or _http_json

    def fetch_markets(self) -> list[dict[str, Any]]:
        products = self._request_json(COINBASE_BASE + "/products", self.timeout)
        if not isinstance(products, list):
            raise MarketDataError("Coinbase products response was not a list")
        eligible = [
            x for x in products
            if isinstance(x, dict)
            and x.get("status") == "online"
            and x.get("quote_currency", "").upper() in self.quote_assets
            and x.get("trading_disabled") is not True
        ]
        # Stable order makes runs reproducible; users can raise the bounded cap.
        eligible = sorted(eligible, key=lambda x: x.get("product_id", ""))[:self.max_products]
        snapshots = []
        for product in eligible:
            product_id = product.get("product_id")
            if not product_id:
                continue
            try:
                ticker = self._request_json(
                    f"{COINBASE_BASE}/products/{product_id}/ticker", self.timeout
                )
                stats = self._request_json(
                    f"{COINBASE_BASE}/products/{product_id}/stats", self.timeout
                )
                price = float(ticker["price"])
                open_price = float(stats.get("open", 0.0))
                volume_base = float(stats.get("volume", 0.0))
                volume_quote = volume_base * price
                row = _snapshot(
                    "coinbase", product_id, price, open_price, volume_quote,
                    count=0, bid=float(ticker.get("bid", 0.0)),
                    ask=float(ticker.get("ask", 0.0)),
                )
                if row:
                    snapshots.append(row)
            except (MarketDataError, KeyError, TypeError, ValueError):
                # A delisted/temporarily unavailable product should not kill the cycle.
                continue
        snapshots.sort(key=lambda x: x["quote_volume_24h"], reverse=True)
        return snapshots


class MultiExchangePublicFeed:
    """Aggregate public market snapshots across all enabled exchanges."""

    def __init__(self, enabled: tuple[str, ...] | None = None,
                 coinbase_max_products: int = 40):
        self.enabled = tuple(x.lower() for x in (
            enabled or tuple(s.strip() for s in os.getenv(
                "PUBLIC_MARKET_EXCHANGES", "binance,kraken,coinbase"
            ).split(",") if s.strip())
        ))
        self.feeds = {
            "binance": BinancePublicFeed(),
            "kraken": KrakenPublicFeed(),
            "coinbase": CoinbasePublicFeed(max_products=coinbase_max_products),
        }
        unknown = set(self.enabled) - set(self.feeds)
        if unknown:
            raise ValueError(f"Unknown public market exchanges: {sorted(unknown)}")
        self.errors: dict[str, str] = {}

    def fetch_markets(self) -> list[dict[str, Any]]:
        combined = []
        self.errors = {}
        for name in self.enabled:
            try:
                combined.extend(self.feeds[name].fetch_markets())
            except Exception as exc:
                self.errors[name] = f"{type(exc).__name__}: {exc}"
        if not combined:
            details = "; ".join(f"{k}: {v}" for k, v in self.errors.items())
            raise MarketDataError("No exchange returned public markets. " + details)
        return combined
