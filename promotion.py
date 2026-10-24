STAGES = ("PAPER", "SHADOW", "LIVE_CANDIDATE", "LIVE")

def can_promote(current: str, target: str) -> bool:
    if current not in STAGES or target not in STAGES:
        return False
    return STAGES.index(target) <= STAGES.index(current) + 1

def validate_live_readiness(checks: dict) -> tuple[bool, list[str]]:
    required = [
        "risk_limits_loaded", "kill_switch_ready", "exchange_health",
        "audit_logging", "operator_approval"
    ]
    missing = [k for k in required if not checks.get(k, False)]
    return len(missing) == 0, missing
