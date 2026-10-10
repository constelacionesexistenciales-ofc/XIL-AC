from dataclasses import dataclass


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    requires_human_review: bool
    reason: str


_VALID_LEVELS = {"low", "medium", "high", "critical"}


def evaluate(risk_level: str, human_override_enabled: bool = True) -> RiskDecision:
    level = risk_level.strip().lower()
    if level not in _VALID_LEVELS:
        return RiskDecision(False, True, "Unknown risk level; blocked by default.")
    if level in {"high", "critical"}:
        return RiskDecision(False, True, "High-risk action requires explicit human review.")
    return RiskDecision(True, False, "No elevated risk detected.")
