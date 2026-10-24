"""Deterministic research league. Agents rank ideas; none can submit orders."""
from __future__ import annotations
from dataclasses import dataclass
from statistics import mean
from typing import Iterable

@dataclass
class AgentScore:
    agent: str
    pnl: float
    drawdown: float
    hit_rate: float

@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    move_weight: float
    liquidity_weight: float
    momentum_weight: float
    spread_penalty: float
    min_score: float

class AgentArena:
    """A 100-profile transparent research league, not a trained or profitable AI claim."""
    def __init__(self, agent_count: int = 100):
        self.agent_count = max(1, min(int(agent_count), 1000))
        self.profiles = [self._profile(i) for i in range(self.agent_count)]

    @staticmethod
    def _profile(i: int) -> AgentProfile:
        # Diverse fixed parameter variants for reproducible comparison.
        return AgentProfile(
            agent_id=f"agent-{i + 1:03d}",
            move_weight=0.15 + ((i * 7) % 21) / 100,
            liquidity_weight=0.10 + ((i * 11) % 21) / 100,
            momentum_weight=0.10 + ((i * 13) % 21) / 100,
            spread_penalty=0.03 + ((i * 3) % 10) / 100,
            min_score=3.0 + (i % 8),
        )

    def evaluate(self, opportunities: Iterable[object]) -> list[dict]:
        results = []
        for profile in self.profiles:
            ranked = []
            for op in opportunities:
                # Market scanner Opportunity contains score/trigger; avoid fabricated PnL.
                score = float(getattr(op, "score", 0.0))
                trigger = str(getattr(op, "trigger", "UNKNOWN"))
                if score >= profile.min_score:
                    adjusted = score * profile.move_weight + profile.liquidity_weight + profile.momentum_weight - profile.spread_penalty
                    ranked.append({"symbol": str(getattr(op, "symbol", "")), "trigger": trigger,
                                   "raw_score": score, "agent_score": round(adjusted, 4)})
            ranked.sort(key=lambda x: x["agent_score"], reverse=True)
            results.append({"agent": profile.agent_id, "candidates": ranked[:10],
                            "candidate_count": len(ranked), "mode": "RESEARCH_ONLY"})
        return results

    def rank(self, scores: list[AgentScore]):
        return sorted(scores, key=lambda s: (s.pnl - 2.0 * s.drawdown + 0.25 * s.hit_rate), reverse=True)

    def consensus(self, scores: list[AgentScore]):
        if not scores:
            return {"agents": 0, "mean_pnl": 0.0}
        return {"agents": len(scores), "mean_pnl": mean(s.pnl for s in scores)}
