from dataclasses import dataclass

@dataclass(frozen=True)
class RiskLimits:
    max_order_notional: float = 1000.0
    max_daily_loss: float = 100.0
    max_position_notional: float = 5000.0
    max_open_orders: int = 20

class RiskBook:
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self.daily_loss = 0.0
        self.position_notional = 0.0
        self.open_orders = 0

    def approve_order(self, notional: float) -> tuple[bool, str]:
        if notional > self.limits.max_order_notional:
            return False, "ORDER_NOTIONAL_LIMIT"
        if self.position_notional + notional > self.limits.max_position_notional:
            return False, "POSITION_LIMIT"
        if self.open_orders >= self.limits.max_open_orders:
            return False, "OPEN_ORDER_LIMIT"
        if self.daily_loss >= self.limits.max_daily_loss:
            return False, "DAILY_LOSS_LIMIT"
        return True, "APPROVED"
