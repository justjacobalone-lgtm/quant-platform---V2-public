from collections import deque

class MicroWindowEngine:
    """Bounded micro-window feature accumulator for research/shadow use."""
    def __init__(self, size: int = 32):
        self.window = deque(maxlen=size)

    def push(self, tick: dict):
        self.window.append(tick)

    def features(self):
        if not self.window:
            return {}
        bids = [x["bid"] for x in self.window]
        asks = [x["ask"] for x in self.window]
        return {
            "samples": len(self.window),
            "mid_last": (bids[-1] + asks[-1]) / 2,
            "mid_min": min((b + a) / 2 for b, a in zip(bids, asks)),
            "mid_max": max((b + a) / 2 for b, a in zip(bids, asks)),
        }
