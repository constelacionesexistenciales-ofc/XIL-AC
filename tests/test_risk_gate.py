import pytest
from core.risk_gate import evaluate

@pytest.mark.parametrize("level", ["high", "critical", " HIGH "])
def test_high_risk_is_blocked(level):
    decision = evaluate(level)
    assert not decision.allowed
    assert decision.requires_human_review

def test_low_risk_is_allowed():
    assert evaluate("low").allowed

def test_unknown_risk_fails_closed():
    assert not evaluate("unknown").allowed
