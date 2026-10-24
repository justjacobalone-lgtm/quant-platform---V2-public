from research.market_scanner import MarketSnapshot, WholeMarketScanner
from risk.position_guard import PositionGuard

def test_whole_market_scanner_promotes_breakout_and_breakdown():
    markets = [
        MarketSnapshot("x", "AAA", 1, 12, 2, 90, 90, 5),
        MarketSnapshot("x", "BBB", 1, -11, 2, 90, 90, 5),
        MarketSnapshot("x", "CCC", 1, 3, 2, 90, 90, 5),
    ]
    found = WholeMarketScanner().scan(markets)
    assert [x.trigger for x in found] == ["BREAKOUT", "BREAKDOWN"]

def test_position_guard_enforces_ten_percent_boundary():
    d = PositionGuard(10).evaluate(100, 90, 1.0)
    assert d.action == "EXIT"
    assert d.reason == "emergency_loss_boundary"

def test_position_guard_exits_when_profitable_momentum_decays():
    d = PositionGuard(10).evaluate(100, 108, 0.10)
    assert d.action == "EXIT"
    assert d.reason == "momentum_decay_profit_lock"


def test_agent_arena_builds_one_hundred_research_profiles():
    from research.multi_agent import AgentArena
    arena = AgentArena(100)
    assert len(arena.profiles) == 100
    assert arena.profiles[0].agent_id == "agent-001"
    assert arena.profiles[-1].agent_id == "agent-100"
    assert all(profile.agent_id.startswith("agent-") for profile in arena.profiles)


def test_agent_arena_evaluates_candidates_without_claiming_trades():
    from research.market_scanner import Opportunity
    from research.multi_agent import AgentArena
    results = AgentArena(100).evaluate([Opportunity("BTCUSDT", "LONG", 40.0, "BREAKOUT")])
    assert len(results) == 100
    assert all(item["mode"] == "RESEARCH_ONLY" for item in results)
    assert all("BTCUSDT" in [x["symbol"] for x in item["candidates"]] for item in results)


def test_shadow_cycle_writes_results_without_orders(tmp_path):
    from shadow.worker import run_cycle
    from research.market_scanner import MarketSnapshot

    class FakeFeed:
        def fetch_markets(self):
            return [{"exchange": "test", "symbol": "TESTUSDT", "price": 2.0,
                     "change_pct": 12.0, "volume_accel": 2.0, "liquidity_score": 80.0,
                     "momentum_score": 70.0, "spread_bps": 2.0}]

    out = tmp_path / "results.jsonl"
    result = run_cycle(feed=FakeFeed(), output_path=out)
    assert result["markets_scanned"] == 1
    assert result["agent_count"] == 100
    assert result["mode"] == "SHADOW"
    assert result["orders_submitted"] == 0
    assert out.exists() and '"TESTUSDT"' in out.read_text()
