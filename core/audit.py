"""Registro de auditoría sin almacenar transcripciones ni contenido de sesión."""
from __future__ import annotations

from uuid import UUID

from core.db import connection


def record_audit_event(
    execution_id: str,
    event_type: str,
    actor_id: str,
    outcome: str,
) -> None:
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_events (execution_id, event_type, actor_id, outcome)
            VALUES (%s, %s, %s, %s)
            """,
            (UUID(execution_id), event_type, actor_id, outcome),
        )
