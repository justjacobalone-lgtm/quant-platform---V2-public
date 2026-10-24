from execution.exchange import OrderIntent

class OrderGuard:
    def __init__(self, risk_governor, state):
        self.risk = risk_governor
        self.state = state

    def validate(self, intent: OrderIntent) -> tuple[bool, str]:
        if self.state.get("halted"):
            return False, "HALTED"
        if self.state.get("mode") != "LIVE":
            return True, "SIMULATION_OR_SHADOW"
        notional = intent.quantity * (intent.limit_price or 0)
        if not self.risk.approve(notional):
            return False, "RISK_LIMIT"
        return True, "APPROVED"
