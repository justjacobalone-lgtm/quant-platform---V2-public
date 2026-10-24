"""Public, unauthenticated Binance Spot market-data client.

This module only reads public market data. It never signs requests or places orders.
"""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any

BASE_URL = "https://api.binance.com"


class MarketDataError(RuntimeError):
    """Raised when public market data cannot be retrieved or parsed."""


def _get_json(path: str, timeout: float = 12.0) -> Any:
    request = Request(
        BASE_URL + path,
        headers={"User-Agent": "QuantPlatformOS-shadow/1.0", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise MarketDataError(f"Binance returned HTTP {response.status} for {path}")
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MarketDataError(f"Public market-data request failed for {path}: {exc}") from exc


class BinancePublicFeed:
    """Fetches the current USDT-quoted spot universe and ticker/book snapshots."""

    def __init__(self, quote_asset: str = "USDT", timeout: float = 12.0):
        self.quote_asset = quote_asset.upper()
        self.timeout = timeout

    def fetch_markets(self) -> list[dict[str, Any]]:
        # Exchange metadata avoids accidentally scanning leveraged tokens or delisted symbols.
        exchange_info = _get_json("/api/v3/exchangeInfo", self.timeout)
        allowed = {
            item["symbol"] for item in exchange_info.get("symbols", [])
            if item.get("status") == "TRADING"
            and item.get("quoteAsset") == self.quote_asset
            and item.get("isSpotTradingAllowed", True)
            and not item.get("symbol", "").endswith(("UP" + self.quote_asset, "DOWN" + self.quote_asset))
        }
        tickers = _get_json("/api/v3/ticker/24hr", self.timeout)
        books = _get_json("/api/v3/ticker/bookTicker", self.timeout)
        book_by_symbol = {b.get("symbol"): b for b in books if b.get("symbol") in allowed}
        snapshots = []
        for ticker in tickers:
            symbol = ticker.get("symbol")
            if symbol not in allowed:
                continue
            try:
                price = float(ticker["lastPrice"])
                change = float(ticker["priceChangePercent"])
                quote_volume = max(float(ticker.get("quoteVolume", 0.0)), 0.0)
                count = max(int(ticker.get("count", 0)), 0)
                book = book_by_symbol.get(symbol, {})
                bid, ask = float(book.get("bidPrice", 0.0)), float(book.get("askPrice", 0.0))
                mid = (bid + ask) / 2 if bid > 0 and ask > 0 else price
                spread_bps = ((ask - bid) / mid * 10000) if bid > 0 and ask >= bid and mid > 0 else 100.0
                # These are deliberately transparent proxies, not claimed order-book depth metrics.
                liquidity_score = min(100.0, quote_volume / 100_000.0)
                volume_accel = min(10.0, count / 10_000.0)
                momentum_score = min(100.0, abs(change) * 4.0)
                if price <= 0:
                    continue
                snapshots.append({
                    "exchange": "binance", "symbol": symbol, "price": price,
                    "change_pct": change, "quote_volume_24h": quote_volume,
                    "trade_count_24h": count, "volume_accel": volume_accel,
                    "liquidity_score": liquidity_score, "momentum_score": momentum_score,
                    "spread_bps": max(0.0, spread_bps), "observed_at": time.time(),
                })
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
        snapshots.sort(key=lambda x: x["quote_volume_24h"], reverse=True)
        return snapshots
