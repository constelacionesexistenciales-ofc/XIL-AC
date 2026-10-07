from dataclasses import dataclass


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    requires_human_review: bool
    reason: str


def evaluate(
    risk_level: str,
    human_override_enabled: bool = True,
) -> RiskDecision:

    level = risk_level.lower()

    if level in {"high", "critical"}:
        return RiskDecision(
            allowed=False,
            requires_human_review=human_override_enabled,
            reason="High-risk action requires human review.",
        )

    return RiskDecision(
        allowed=True,
        requires_human_review=False,
        reason="No elevated risk detected.",
    )