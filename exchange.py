from dataclasses import dataclass
from typing import Protocol

@dataclass
class OrderIntent:
    symbol: str
    side: str
    quantity: float
    limit_price: float | None = None
    client_order_id: str | None = None

class ExchangeAdapter(Protocol):
    def health(self) -> dict: ...
    def place_order(self, intent: OrderIntent) -> dict: ...
    def cancel_all(self, symbol: str | None = None) -> dict: ...

class PaperExchange:
    def health(self):
        return {"exchange": "paper", "connected": True}

    def place_order(self, intent: OrderIntent):
        return {"status": "SIMULATED", "symbol": intent.symbol, "side": intent.side,
                "quantity": intent.quantity, "client_order_id": intent.client_order_id}

    def cancel_all(self, symbol=None):
        return {"status": "SIMULATED_CANCEL", "symbol": symbol}
