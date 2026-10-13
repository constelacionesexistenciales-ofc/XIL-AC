"""Indicadores de movimiento de sesión; almacena puntuaciones mínimas, no transcripciones."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from psycopg.types.json import Jsonb

from core.db import connection


class SessionObjective(StrEnum):
    STABILIZATION = "stabilization"
    AVAILABILITY = "availability"
    EXPLORATION = "exploration"
    INTEGRATION = "integration"
    ACTION = "action"
    OTHER = "other"


class SnapshotPhase(StrEnum):
    ARRIVAL = "arrival"
    DURING = "during"
    CLOSING = "closing"


class ScoreSource(StrEnum):
    CONSULTANTE = "consultante_self_report"
    FACILITATOR = "facilitator_observation"
    JOINT = "jointly_reviewed"


class ScoreSet(BaseModel):
    """0–4; None significa NE (no evaluable), nunca cero por defecto."""
    model_config = ConfigDict(extra="forbid")
    availability: int | None = Field(default=None, ge=0, le=4)
    action_capacity: int | None = Field(default=None, ge=0, le=4)
    integration_capacity: int | None = Field(default=None, ge=0, le=4)
    phenomenological_movement: int | None = Field(default=None, ge=0, le=4)
    vitality_energy: int | None = Field(default=None, ge=0, le=4)
    coping_availability: int | None = Field(default=None, ge=0, le=4)


class SessionStart(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objective: SessionObjective


class SnapshotInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phase: SnapshotPhase
    source: ScoreSource
    scores: ScoreSet


class SessionMovementError(Exception):
    """Error de estado o pertenencia de una sesión."""


def score_delta(initial: dict, final: dict) -> dict:
    """Devuelve variaciones solo cuando ambas puntuaciones son evaluables."""
    return {
        key: final.get(key) - initial.get(key)
        if initial.get(key) is not None and final.get(key) is not None
        else None
        for key in ScoreSet.model_fields
    }


def create_session(actor_id: str, objective: SessionObjective) -> dict:
    session_id = uuid4()
    now = datetime.now(timezone.utc)
    with connection() as conn:
        conn.execute(
            """INSERT INTO session_movement_sessions
               (session_id, actor_id, objective, created_at)
               VALUES (%s, %s, %s, %s)""",
            (session_id, actor_id, objective.value, now),
        )
    return {"session_id": str(session_id), "objective": objective.value,
            "created_at": now.isoformat(), "status": "open"}


def add_snapshot(actor_id: str, session_id: UUID, item: SnapshotInput) -> dict:
    snapshot_id = uuid4()
    now = datetime.now(timezone.utc)
    scores = item.scores.model_dump(mode="json")
    with connection() as conn:
        session = conn.execute(
            """SELECT closed_at FROM session_movement_sessions
               WHERE session_id = %s AND actor_id = %s FOR UPDATE""",
            (session_id, actor_id),
        ).fetchone()
        if session is None:
            raise SessionMovementError("session_not_found")
        if session[0] is not None:
            raise SessionMovementError("session_closed")
        existing = conn.execute(
            """SELECT phase FROM session_movement_snapshots
               WHERE session_id = %s AND phase IN ('arrival', 'closing')""",
            (session_id,),
        ).fetchall()
        phases = {row[0] for row in existing}
        if item.phase.value == "arrival" and "arrival" in phases:
            raise SessionMovementError("arrival_already_recorded")
        if item.phase.value == "during" and "arrival" not in phases:
            raise SessionMovementError("arrival_required")
        if item.phase.value == "closing" and "arrival" not in phases:
            raise SessionMovementError("arrival_required")
        conn.execute(
            """INSERT INTO session_movement_snapshots
               (snapshot_id, session_id, actor_id, phase, source, scores, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (snapshot_id, session_id, actor_id, item.phase.value, item.source.value,
             Jsonb(scores), now),
        )
        if item.phase.value == "closing":
            conn.execute(
                """UPDATE session_movement_sessions SET closed_at = %s
                   WHERE session_id = %s AND actor_id = %s""",
                (now, session_id, actor_id),
            )
    return {"snapshot_id": str(snapshot_id), "session_id": str(session_id),
            "phase": item.phase.value, "source": item.source.value,
            "scores": scores, "created_at": now.isoformat()}


def get_session(actor_id: str, session_id: UUID) -> dict:
    with connection() as conn:
        session = conn.execute(
            """SELECT objective, created_at, closed_at FROM session_movement_sessions
               WHERE session_id = %s AND actor_id = %s""",
            (session_id, actor_id),
        ).fetchone()
        if session is None:
            raise SessionMovementError("session_not_found")
        rows = conn.execute(
            """SELECT snapshot_id, phase, source, scores, created_at
               FROM session_movement_snapshots
               WHERE session_id = %s AND actor_id = %s ORDER BY created_at""",
            (session_id, actor_id),
        ).fetchall()
    snapshots = [
        {"snapshot_id": str(row[0]), "phase": row[1], "source": row[2],
         "scores": row[3] if isinstance(row[3], dict) else json.loads(row[3]),
         "created_at": row[4].isoformat()}
        for row in rows
    ]
    arrival = next((x for x in snapshots if x["phase"] == "arrival"), None)
    closing = next((x for x in snapshots if x["phase"] == "closing"), None)
    return {
        "session_id": str(session_id), "objective": session[0],
        "created_at": session[1].isoformat(),
        "closed_at": session[2].isoformat() if session[2] else None,
        "status": "closed" if session[2] else "open",
        "snapshots": snapshots,
        "delta": score_delta(arrival["scores"], closing["scores"]) if arrival and closing else None,
        "interpretation_notice": (
            "Indicadores descriptivos para revisión del facilitador; no son un diagnóstico "
            "ni una medida clínica validada. NE significa no evaluable."
        ),
    }
