import os
from uuid import UUID, uuid4
import pytest

from core.db import connection
from core.session_movement import (
    ScoreSet,
    SessionMovementError,
    SessionObjective,
    SnapshotInput,
    SnapshotPhase,
    ScoreSource,
    add_snapshot,
    create_session,
    get_session,
)


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="requires CI PostgreSQL")
def test_session_movement_persists_snapshots_and_isolates_owner(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_DATABASE_URL"])
    actor = "facilitator-" + str(uuid4())
    other_actor = "other-" + str(uuid4())
    session = create_session(actor, SessionObjective.STABILIZATION)
    session_id = session["session_id"]
    try:
        add_snapshot(
            actor,
            UUID(session_id),
            SnapshotInput(
                phase=SnapshotPhase.ARRIVAL,
                source=ScoreSource.JOINT,
                scores=ScoreSet(availability=1, vitality_energy=2, coping_availability=1),
            ),
        )
        add_snapshot(
            actor,
            __import__("uuid").UUID(session_id),
            SnapshotInput(
                phase=SnapshotPhase.DURING,
                source=ScoreSource.FACILITATOR,
                scores=ScoreSet(availability=2),
            ),
        )
        add_snapshot(
            actor,
            __import__("uuid").UUID(session_id),
            SnapshotInput(
                phase=SnapshotPhase.CLOSING,
                source=ScoreSource.JOINT,
                scores=ScoreSet(availability=3, vitality_energy=3, coping_availability=4),
            ),
        )
        report = get_session(actor, __import__("uuid").UUID(session_id))
        assert report["status"] == "closed"
        assert report["delta"]["availability"] == 2
        assert report["delta"]["vitality_energy"] == 1
        assert report["delta"]["coping_availability"] == 3
        assert "MOVIMIENTO DURANTE EL ENCUENTRO" in report["report_block"]
        with pytest.raises(SessionMovementError, match="session_not_found"):
            get_session(other_actor, __import__("uuid").UUID(session_id))
    finally:
        with connection() as conn:
            conn.execute(
                "DELETE FROM session_movement_sessions WHERE session_id = %s",
                (__import__("uuid").UUID(session_id),),
            )
