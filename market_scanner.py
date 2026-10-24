from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class MarketSnapshot:
    exchange: str
    symbol: str
    price: float
    change_pct: float
    volume_accel: float
    liquidity_score: float
    momentum_score: float
    spread_bps: float

@dataclass(frozen=True)
class Opportunity:
    symbol: str
    direction: str
    score: float
    trigger: str

class WholeMarketScanner:
    """Ranks every supplied tradable market; thresholds trigger investigation, not orders."""
    def __init__(self, breakout_pct: float = 10.0, breakdown_pct: float = -10.0, max_per_minute: int = 100):
        self.breakout_pct = breakout_pct
        self.breakdown_pct = breakdown_pct
        self.max_per_minute = max_per_minute

    def scan(self, markets: Iterable[MarketSnapshot]) -> list[Opportunity]:
        found: list[Opportunity] = []
        for m in markets:
            trigger = None
            direction = None
            if m.change_pct >= self.breakout_pct:
                trigger, direction = "BREAKOUT", "LONG"
            elif m.change_pct <= self.breakdown_pct:
                trigger, direction = "BREAKDOWN", "SHORT"
            if not trigger:
                continue
            score = (
                min(abs(m.change_pct), 50.0) * 0.35
                + min(max(m.volume_accel, 0.0), 10.0) * 10.0 * 0.25
                + m.liquidity_score * 0.20
                + m.momentum_score * 0.20
                - min(max(m.spread_bps, 0.0), 100.0) * 0.10
            )
            found.append(Opportunity(m.symbol, direction, round(score, 4), trigger))
        found.sort(key=lambda x: x.score, reverse=True)
        return found[: self.max_per_minute]
