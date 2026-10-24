from research.multi_exchange_feed import (
    CoinbasePublicFeed, KrakenPublicFeed, MultiExchangePublicFeed
)


def test_kraken_public_ticker_normalizes_snapshot():
    def fake(url, timeout):
        assert url.endswith("/0/public/Ticker")
        return {"error": [], "result": {
            "XBTUSD": {"c": ["110", "1"], "o": "100", "v": ["10", "20"],
                       "b": ["109", "1"], "a": ["111", "1"]},
            "ETHUSD": {"c": ["20", "1"], "o": "20", "v": ["5", "10"],
                       "b": ["19.9", "1"], "a": ["20.1", "1"]},
            "ETHBTC": {"c": ["0.1", "1"], "o": "0.09", "v": ["5", "10"],
                       "b": ["0.099", "1"], "a": ["0.101", "1"]},
        }}
    rows = KrakenPublicFeed(request_json=fake).fetch_markets()
    assert len(rows) == 2
    btc = next(x for x in rows if x["symbol"] == "XBTUSD")
    assert btc["exchange"] == "kraken"
    assert btc["price"] == 110
    assert round(btc["change_pct"], 2) == 10.0
    assert btc["quote_volume_24h"] == 2200


def test_coinbase_public_products_normalize_ticker_and_stats():
    def fake(url, timeout):
        if url.endswith("/products"):
            return [
                {"product_id": "BTC-USD", "quote_currency": "USD", "status": "online"},
                {"product_id": "ETH-BTC", "quote_currency": "BTC", "status": "online"},
                {"product_id": "DOGE-USD", "quote_currency": "USD", "status": "offline"},
            ]
        if url.endswith("/BTC-USD/ticker"):
            return {"price": "110", "bid": "109", "ask": "111"}
        if url.endswith("/BTC-USD/stats"):
            return {"open": "100", "volume": "2"}
        raise AssertionError(url)
    rows = CoinbasePublicFeed(request_json=fake).fetch_markets()
    assert len(rows) == 1
    assert rows[0]["symbol"] == "BTC-USD"
    assert rows[0]["exchange"] == "coinbase"
    assert rows[0]["change_pct"] == 10
    assert rows[0]["quote_volume_24h"] == 220


def test_multi_exchange_feed_combines_feeds_and_records_failures():
    class FakeFeed:
        def __init__(self, name, fail=False):
            self.name, self.fail = name, fail
        def fetch_markets(self):
            if self.fail:
                raise RuntimeError("offline")
            return [{"exchange": self.name, "symbol": self.name.upper(),
                     "price": 1, "change_pct": 0, "quote_volume_24h": 1,
                     "trade_count_24h": 1, "volume_accel": 0, "liquidity_score": 0,
                     "momentum_score": 0, "spread_bps": 1, "observed_at": 1}]

    feed = MultiExchangePublicFeed(enabled=("binance", "kraken", "coinbase"))
    feed.feeds = {
        "binance": FakeFeed("binance"),
        "kraken": FakeFeed("kraken", fail=True),
        "coinbase": FakeFeed("coinbase"),
    }
    rows = feed.fetch_markets()
    assert {x["exchange"] for x in rows} == {"binance", "coinbase"}
    assert "kraken" in feed.errors
