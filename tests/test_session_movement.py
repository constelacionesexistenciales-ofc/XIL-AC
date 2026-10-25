import pytest
from pydantic import ValidationError

from core.session_movement import ScoreSet, SessionObjective, SnapshotInput, score_delta


def test_score_set_accepts_ne_and_zero_as_distinct_values():
    scores = ScoreSet(availability=0, action_capacity=None)
    assert scores.availability == 0
    assert scores.action_capacity is None


@pytest.mark.parametrize("value", [-1, 5])
def test_score_outside_scale_is_rejected(value):
    with pytest.raises(ValidationError):
        ScoreSet(availability=value)


def test_score_set_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ScoreSet(availability=2, diagnosis="not allowed")


def test_delta_only_compares_evaluable_values():
    before = ScoreSet(availability=1, action_capacity=None, vitality_energy=2).model_dump()
    after = ScoreSet(availability=3, action_capacity=4, vitality_energy=1).model_dump()
    delta = score_delta(before, after)
    assert delta["availability"] == 2
    assert delta["action_capacity"] is None
    assert delta["vitality_energy"] == -1


def test_session_objectives_are_explicit():
    assert SessionObjective.STABILIZATION.value == "stabilization"


def test_snapshot_requires_source_and_phase():
    with pytest.raises(ValidationError):
        SnapshotInput(phase="arrival", scores={"availability": 2})
