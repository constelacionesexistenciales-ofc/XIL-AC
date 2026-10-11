"""Deterministic authorization gate for bounded autonomous actions.

This module decides whether an action may proceed. It does not execute actions,
call providers, or replace the human operator's responsibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.trace import new_trace

GateState = Literal["denied", "awaiting_approval", "authorized"]
_VALID_RISKS = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class ActionPolicy:
    action_id: str
    required_permissions: frozenset[str]
    risk_level: str
    external_effect: bool = False
    human_approval_required: bool = False


@dataclass(frozen=True, slots=True)
class GateDecision:
    execution_id: str
    action_id: str
    state: GateState
    reason: str
    missing_permissions: tuple[str, ...] = ()

    @property
    def may_execute(self) -> bool:
        return self.state == "authorized"


class AutonomyGate:
    """Fail-closed policy evaluator for a fixed registry of permitted actions."""

    def __init__(self, policies: tuple[ActionPolicy, ...] | list[ActionPolicy]) -> None:
        self._policies = {policy.action_id: policy for policy in policies}
        self._registry_valid = (
            len(self._policies) == len(policies)
            and all(policy.action_id.strip() for policy in policies)
        )

    def evaluate(
        self,
        action_id: str,
        granted_permissions: frozenset[str] | set[str],
        *,
        human_approved: bool = False,
    ) -> GateDecision:
        trace = new_trace()
        if not self._registry_valid:
            return GateDecision(
                trace.execution_id, action_id, "denied", "invalid_action_registry"
            )

        policy = self._policies.get(action_id)
        if policy is None:
            return GateDecision(
                trace.execution_id, action_id, "denied", "action_not_allowlisted"
            )

        if policy.risk_level not in _VALID_RISKS:
            return GateDecision(
                trace.execution_id, action_id, "denied", "unknown_risk_level"
            )

        missing = tuple(sorted(policy.required_permissions - frozenset(granted_permissions)))
        if missing:
            return GateDecision(
                trace.execution_id,
                action_id,
                "denied",
                "required_permission_missing",
                missing,
            )

        approval_needed = (
            policy.human_approval_required
            or policy.external_effect
            or policy.risk_level == "high"
        )
        if approval_needed and not human_approved:
            return GateDecision(
                trace.execution_id, action_id, "awaiting_approval", "human_gate_required"
            )

        return GateDecision(
            trace.execution_id, action_id, "authorized", "policy_checks_passed"
        )
