import os, time

class RiskGovernor:
    def __init__(self):
        self.max_order_notional = float(os.getenv("MAX_ORDER_NOTIONAL", "1000"))
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", "100"))
        self.halted = False

    def heartbeat(self):
        if self.halted:
            return
        # Production hook: reconcile positions, limits, stale orders,
        # exchange connectivity and kill-switch state.
        return True

    def approve(self, notional: float) -> bool:
        return (not self.halted) and notional <= self.max_order_notional

    def halt(self):
        self.halted = True
