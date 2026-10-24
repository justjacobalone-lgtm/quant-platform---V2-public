from dataclasses import dataclass

@dataclass(frozen=True)
class PositionDecision:
    action: str
    reason: str
    protected_price: float

class PositionGuard:
    """Per-position emergency boundary plus momentum-decay profit protection."""
    def __init__(self, max_loss_pct: float = 10.0):
        if not 0 < max_loss_pct < 100:
            raise ValueError("max_loss_pct must be between 0 and 100")
        self.max_loss_pct = max_loss_pct

    def evaluate(self, entry: float, current: float, momentum_strength: float) -> PositionDecision:
        if entry <= 0 or current <= 0:
            raise ValueError("prices must be positive")
        floor = entry * (1 - self.max_loss_pct / 100)
        if current <= floor:
            return PositionDecision("EXIT", "emergency_loss_boundary", floor)
        gain_pct = (current / entry - 1) * 100
        if gain_pct > 0 and momentum_strength < 0.25:
            return PositionDecision("EXIT", "momentum_decay_profit_lock", max(floor, current))
        if gain_pct > 0 and momentum_strength < 0.50:
            return PositionDecision("TIGHTEN", "momentum_weakening", max(floor, current * 0.995))
        return PositionDecision("HOLD", "momentum_intact", floor)
