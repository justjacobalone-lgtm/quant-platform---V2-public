from dataclasses import dataclass

@dataclass
class Divergence:
    symbol: str
    reference_price: float
    shadow_price: float
    divergence_bps: float

class DivergenceMonitor:
    def __init__(self, threshold_bps: float = 25.0):
        self.threshold_bps = threshold_bps

    def check(self, d: Divergence) -> dict:
        return {
            "symbol": d.symbol,
            "divergence_bps": d.divergence_bps,
            "alert": abs(d.divergence_bps) >= self.threshold_bps,
        }
