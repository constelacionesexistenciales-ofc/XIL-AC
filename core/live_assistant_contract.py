"""Strict, side-effect-free contract for live phenomenological suggestions.

This module validates structured suggestions only. It does not call a model, transmit
session content, persist transcripts, render UI, or enable CFE session processing.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

Mode = Literal["suggest", "wait", "blocked"]
EvidenceKind = Literal["fact", "observation", "unknown"]
HypothesisStatus = Literal["open", "supported", "contradicted", "discarded"]

_TOP_KEYS = {
    "schema_version",
    "mode",
    "question",
    "evidence",
    "phenomenological",
    "hypotheses",
    "pending_question",
    "risk_flags",
    "abstention_reason",
    "provenance",
}
_QUESTION_KEYS = {"primary", "alternatives"}
_EVIDENCE_KEYS = {"kind", "text", "source_turn"}
_PHENOMENOLOGICAL_KEYS = {"focus", "proposal"}
_HYPOTHESIS_KEYS = {"text", "status", "evidence_for", "missing_evidence", "alternative"}
_PROVENANCE_KEYS = {"policy_version", "prompt_version", "model_version"}
_MODES = {"suggest", "wait", "blocked"}
_EVIDENCE_KINDS = {"fact", "observation", "unknown"}
_HYPOTHESIS_STATUSES = {"open", "supported", "contradicted", "discarded"}


class SuggestionContractError(ValueError):
    """Raised when generated suggestion data violates the strict contract."""


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    kind: EvidenceKind
    text: str
    source_turn: str | None


@dataclass(frozen=True, slots=True)
class Hypothesis:
    text: str
    status: HypothesisStatus
    evidence_for: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    alternative: str | None


@dataclass(frozen=True, slots=True)
class LiveSuggestion:
    schema_version: str
    mode: Mode
    question_primary: str | None
    question_alternatives: tuple[str, ...]
    evidence: tuple[EvidenceItem, ...]
    phenomenological_focus: str | None
    phenomenological_proposal: str | None
    hypotheses: tuple[Hypothesis, ...]
    pending_question: bool
    risk_flags: tuple[str, ...]
    abstention_reason: str | None
    provenance: tuple[tuple[str, str], ...]


def _mapping(value: object, field: str, expected_keys: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SuggestionContractError(f"{field} must be an object")
    keys = set(value.keys())
    if keys != expected_keys:
        missing = expected_keys - keys
        extra = keys - expected_keys
        raise SuggestionContractError(
            f"{field} keys invalid (missing={sorted(missing)}, extra={sorted(extra)})"
        )
    if not all(isinstance(key, str) for key in value):
        raise SuggestionContractError(f"{field} keys must be strings")
    return value


def _text(value: object, field: str, *, optional: bool = False, limit: int = 500) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str):
        raise SuggestionContractError(f"{field} must be a string")
    if not value.strip():
        raise SuggestionContractError(f"{field} must not be empty")
    if len(value) > limit:
        raise SuggestionContractError(f"{field} exceeds {limit} characters")
    return value.strip()


def _string_list(
    value: object, field: str, *, maximum: int, item_limit: int = 500
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SuggestionContractError(f"{field} must be a list")
    if len(value) > maximum:
        raise SuggestionContractError(f"{field} has too many items")
    return tuple(
        _text(item, f"{field}[{index}]", limit=item_limit)  # type: ignore[arg-type]
        for index, item in enumerate(value)
    )  # type: ignore[return-value]


def parse_live_suggestion(payload: Mapping[str, Any]) -> LiveSuggestion:
    """Validate and normalize a model output; never execute or persist its contents."""
    data = _mapping(payload, "payload", _TOP_KEYS)
    version = _text(data["schema_version"], "schema_version", limit=20)
    if version != "1.0":
        raise SuggestionContractError("unsupported schema_version")

    mode = _text(data["mode"], "mode", limit=20)
    if mode not in _MODES:
        raise SuggestionContractError("mode is not allowed")

    question = _mapping(data["question"], "question", _QUESTION_KEYS)
    primary = _text(question["primary"], "question.primary", optional=True, limit=280)
    alternatives = _string_list(
        question["alternatives"], "question.alternatives", maximum=2, item_limit=280
    )

    raw_evidence = data["evidence"]
    if not isinstance(raw_evidence, list) or len(raw_evidence) > 8:
        raise SuggestionContractError("evidence must be a list of at most 8 items")
    evidence_items: list[EvidenceItem] = []
    for index, raw in enumerate(raw_evidence):
        item = _mapping(raw, f"evidence[{index}]", _EVIDENCE_KEYS)
        kind = _text(item["kind"], f"evidence[{index}].kind", limit=20)
        if kind not in _EVIDENCE_KINDS:
            raise SuggestionContractError(f"evidence[{index}].kind is not allowed")
        text = _text(item["text"], f"evidence[{index}].text", limit=400)
        source_turn = _text(
            item["source_turn"], f"evidence[{index}].source_turn", optional=True, limit=80
        )
        evidence_items.append(EvidenceItem(kind, text, source_turn))  # type: ignore[arg-type]

    phenomenological = _mapping(
        data["phenomenological"], "phenomenological", _PHENOMENOLOGICAL_KEYS
    )
    focus = _text(
        phenomenological["focus"], "phenomenological.focus", optional=True, limit=280
    )
    proposal = _text(
        phenomenological["proposal"], "phenomenological.proposal", optional=True, limit=500
    )

    raw_hypotheses = data["hypotheses"]
    if not isinstance(raw_hypotheses, list) or len(raw_hypotheses) > 4:
        raise SuggestionContractError("hypotheses must be a list of at most 4 items")
    hypotheses: list[Hypothesis] = []
    for index, raw in enumerate(raw_hypotheses):
        item = _mapping(raw, f"hypotheses[{index}]", _HYPOTHESIS_KEYS)
        statement = _text(item["text"], f"hypotheses[{index}].text", limit=400)
        status = _text(item["status"], f"hypotheses[{index}].status", limit=20)
        if status not in _HYPOTHESIS_STATUSES:
            raise SuggestionContractError(f"hypotheses[{index}].status is not allowed")
        evidence_for = _string_list(
            item["evidence_for"], f"hypotheses[{index}].evidence_for", maximum=5
        )
        missing = _string_list(
            item["missing_evidence"], f"hypotheses[{index}].missing_evidence", maximum=5
        )
        alternative = _text(
            item["alternative"], f"hypotheses[{index}].alternative", optional=True, limit=400
        )
        if not missing:
            raise SuggestionContractError(
                f"hypotheses[{index}] must state missing evidence for every status"
            )
        hypotheses.append(
            Hypothesis(
                statement, status, evidence_for, missing, alternative  # type: ignore[arg-type]
            )
        )

    pending = data["pending_question"]
    if not isinstance(pending, bool):
        raise SuggestionContractError("pending_question must be a boolean")
    risk_flags = _string_list(data["risk_flags"], "risk_flags", maximum=12, item_limit=80)
    reason = _text(data["abstention_reason"], "abstention_reason", optional=True, limit=240)

    provenance_data = _mapping(data["provenance"], "provenance", _PROVENANCE_KEYS)
    provenance = tuple(
        (
            key,
            _text(provenance_data[key], f"provenance.{key}", limit=80),  # type: ignore[arg-type]
        )
        for key in sorted(_PROVENANCE_KEYS)
    )

    if mode == "suggest":
        if not primary or not evidence_items or not focus or not proposal:
            raise SuggestionContractError(
                "suggest mode requires a primary question, evidence, focus and proposal"
            )
        if pending:
            raise SuggestionContractError(
                "pending_question requires wait mode unless the facilitator requests alternatives"
            )
        if reason is not None:
            raise SuggestionContractError("suggest mode must not include abstention_reason")
    else:
        if primary is not None or alternatives or focus is not None or proposal is not None:
            raise SuggestionContractError("wait/blocked modes must not include suggestions")
        if reason is None:
            raise SuggestionContractError("wait/blocked modes require abstention_reason")
        if mode == "blocked" and not risk_flags:
            raise SuggestionContractError("blocked mode requires at least one risk flag")

    return LiveSuggestion(
        schema_version=version,  # type: ignore[arg-type]
        mode=mode,  # type: ignore[arg-type]
        question_primary=primary,
        question_alternatives=alternatives,
        evidence=tuple(evidence_items),
        phenomenological_focus=focus,
        phenomenological_proposal=proposal,
        hypotheses=tuple(hypotheses),
        pending_question=pending,
        risk_flags=risk_flags,
        abstention_reason=reason,
        provenance=provenance,  # type: ignore[arg-type]
    )
