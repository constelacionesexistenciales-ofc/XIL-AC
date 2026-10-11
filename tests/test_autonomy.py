import re

from core.autonomy import ActionPolicy, AutonomyGate


def test_unknown_action_is_denied():
    gate = AutonomyGate([])
    decision = gate.evaluate("shell.execute", {"admin"})
    assert decision.state == "denied"
    assert decision.reason == "action_not_allowlisted"
    assert not decision.may_execute


def test_missing_permission_is_denied():
    gate = AutonomyGate(
        [ActionPolicy("research.search", frozenset({"research:search"}), "low")]
    )
    decision = gate.evaluate("research.search", {"research:read"})
    assert decision.state == "denied"
    assert decision.missing_permissions == ("research:search",)


def test_unknown_risk_fails_closed():
    gate = AutonomyGate([ActionPolicy("unknown.risk", frozenset(), "unknown")])
    decision = gate.evaluate("unknown.risk", set())
    assert decision.state == "denied"
    assert decision.reason == "unknown_risk_level"


def test_high_risk_action_requires_explicit_human_approval():
    gate = AutonomyGate(
        [ActionPolicy("deployment.promote", frozenset({"deploy"}), "high")]
    )
    waiting = gate.evaluate("deployment.promote", {"deploy"})
    assert waiting.state == "awaiting_approval"
    approved = gate.evaluate(
        "deployment.promote", {"deploy"}, human_approved=True
    )
    assert approved.state == "authorized"
    assert approved.may_execute


def test_external_side_effect_requires_human_approval():
    gate = AutonomyGate(
        [ActionPolicy("provider.send", frozenset({"research:send"}), "low", external_effect=True)]
    )
    assert gate.evaluate("provider.send", {"research:send"}).state == "awaiting_approval"
    assert gate.evaluate(
        "provider.send", {"research:send"}, human_approved=True
    ).state == "authorized"


def test_low_risk_internal_action_can_be_authorized_with_permission():
    gate = AutonomyGate(
        [ActionPolicy("report.validate", frozenset({"report:validate"}), "low")]
    )
    decision = gate.evaluate("report.validate", {"report:validate"})
    assert decision.state == "authorized"
    assert re.fullmatch(r"[0-9a-f-]{36}", decision.execution_id)


def test_duplicate_policy_ids_invalidate_registry():
    policies = [
        ActionPolicy("research.search", frozenset(), "low"),
        ActionPolicy("research.search", frozenset(), "low"),
    ]
    decision = AutonomyGate(policies).evaluate("research.search", set())
    assert decision.state == "denied"
    assert decision.reason == "invalid_action_registry"
