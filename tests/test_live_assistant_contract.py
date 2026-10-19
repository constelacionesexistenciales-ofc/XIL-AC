from copy import deepcopy

import pytest

from core.live_assistant_contract import (
    LiveSuggestion,
    SuggestionContractError,
    parse_live_suggestion,
)


def valid_payload():
    return {
        "schema_version": "1.0",
        "mode": "suggest",
        "question": {
            "primary": "¿Qué notás en vos antes de decidir?",
            "alternatives": ["¿Qué imaginás que podría pasar?"],
        },
        "evidence": [
            {
                "kind": "fact",
                "text": "La persona relata que duda antes de acercarse.",
                "source_turn": "turn-3",
            }
        ],
        "phenomenological": {
            "focus": "El momento previo a la decisión.",
            "proposal": "Explorar qué observa, imagina y elige en ese momento.",
        },
        "hypotheses": [
            {
                "text": "La anticipación podría influir en su decisión.",
                "status": "open",
                "evidence_for": ["La persona relata dudas previas."],
                "missing_evidence": ["Qué piensa y siente en ese momento."],
                "alternative": "La decisión también podría depender del contexto.",
            }
        ],
        "pending_question": False,
        "risk_flags": [],
        "abstention_reason": None,
        "provenance": {
            "policy_version": "1",
            "prompt_version": "1",
            "model_version": "synthetic-test",
        },
    }


def test_valid_suggestion_parses_to_immutable_contract():
    result = parse_live_suggestion(valid_payload())
    assert isinstance(result, LiveSuggestion)
    assert result.mode == "suggest"
    assert result.question_primary == "¿Qué notás en vos antes de decidir?"
    assert len(result.question_alternatives) == 1
    assert result.hypotheses[0].status == "open"


def test_unknown_top_level_field_is_rejected():
    payload = valid_payload()
    payload["send_to_consultant"] = True
    with pytest.raises(SuggestionContractError, match="keys invalid"):
        parse_live_suggestion(payload)


def test_more_than_two_alternatives_is_rejected():
    payload = valid_payload()
    payload["question"]["alternatives"] = ["A", "B", "C"]
    with pytest.raises(SuggestionContractError, match="too many items"):
        parse_live_suggestion(payload)


def test_suggestion_requires_evidence_and_exploration():
    payload = valid_payload()
    payload["evidence"] = []
    with pytest.raises(SuggestionContractError, match="requires a primary question"):
        parse_live_suggestion(payload)


def test_open_hypothesis_requires_missing_evidence():
    payload = valid_payload()
    payload["hypotheses"][0]["missing_evidence"] = []
    with pytest.raises(SuggestionContractError, match="must state missing evidence"):
        parse_live_suggestion(payload)


def test_pending_question_requires_wait_mode():
    payload = valid_payload()
    payload["pending_question"] = True
    with pytest.raises(SuggestionContractError, match="requires wait mode"):
        parse_live_suggestion(payload)


def test_wait_mode_allows_abstention_without_a_question():
    payload = valid_payload()
    payload.update(
        {
            "mode": "wait",
            "question": {"primary": None, "alternatives": []},
            "evidence": [],
            "phenomenological": {"focus": None, "proposal": None},
            "hypotheses": [],
            "pending_question": True,
            "abstention_reason": "La respuesta a la pregunta anterior aún no está disponible.",
        }
    )
    result = parse_live_suggestion(payload)
    assert result.mode == "wait"
    assert result.question_primary is None
    assert result.abstention_reason is not None


def test_blocked_mode_requires_risk_flag():
    payload = valid_payload()
    payload.update(
        {
            "mode": "blocked",
            "question": {"primary": None, "alternatives": []},
            "evidence": [],
            "phenomenological": {"focus": None, "proposal": None},
            "hypotheses": [],
            "pending_question": False,
            "abstention_reason": "La comprobación de privacidad no está disponible.",
        }
    )
    with pytest.raises(SuggestionContractError, match="risk flag"):
        parse_live_suggestion(payload)


def test_blocked_mode_with_risk_flag_has_no_suggestions():
    payload = valid_payload()
    payload.update(
        {
            "mode": "blocked",
            "question": {"primary": None, "alternatives": []},
            "evidence": [],
            "phenomenological": {"focus": None, "proposal": None},
            "hypotheses": [],
            "pending_question": False,
            "risk_flags": ["privacy_preflight_failed"],
            "abstention_reason": "La comprobación de privacidad no está disponible.",
        }
    )
    result = parse_live_suggestion(payload)
    assert result.mode == "blocked"
    assert result.question_primary is None


@pytest.mark.parametrize("mode", ["execute", "auto_send", "diagnose", ""])
def test_unapproved_mode_is_rejected(mode):
    payload = valid_payload()
    payload["mode"] = mode
    with pytest.raises(SuggestionContractError, match="mode"):
        parse_live_suggestion(payload)


def test_overlong_question_is_rejected():
    payload = valid_payload()
    payload["question"]["primary"] = "x" * 281
    with pytest.raises(SuggestionContractError, match="exceeds 280"):
        parse_live_suggestion(payload)


def test_non_boolean_pending_question_is_rejected():
    payload = valid_payload()
    payload["pending_question"] = "false"
    with pytest.raises(SuggestionContractError, match="must be a boolean"):
        parse_live_suggestion(payload)


def test_input_payload_is_not_mutated():
    payload = valid_payload()
    original = deepcopy(payload)
    parse_live_suggestion(payload)
    assert payload == original


def test_unexpected_nested_action_field_is_rejected():
    payload = valid_payload()
    payload["question"]["execute_tool"] = "anything"
    with pytest.raises(SuggestionContractError, match="keys invalid"):
        parse_live_suggestion(payload)
