"""Limitación de solicitudes compartida por PostgreSQL y segura ante fallos."""
from __future__ import annotations

import hashlib
import time

from core.db import connection


class RateLimitExceeded(Exception):
    """El actor superó el límite del ámbito durante la ventana actual."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = max(1, retry_after)
        super().__init__("rate limit exceeded")


class RateLimitStorageUnavailable(Exception):
    """No se pudo consultar/actualizar el límite compartido; debe bloquearse."""


def enforce_rate_limit(
    subject: str,
    scope: str,
    *,
    limit: int = 30,
    window_seconds: int = 60,
    now: int | None = None,
) -> None:
    """Cuenta una solicitud en un bucket fijo atómico compartido entre réplicas.

    El subject se transforma en SHA-256 antes de persistirse. Si PostgreSQL no
    está disponible, se falla de forma cerrada en lugar de omitir el control.
    """
    if not subject.strip():
        raise ValueError("subject must not be empty")
    if not scope.strip() or len(scope) > 80:
        raise ValueError("scope must contain 1 to 80 characters")
    if limit < 1 or window_seconds < 1:
        raise ValueError("limit and window_seconds must be positive")

    current = int(time.time()) if now is None else now
    bucket_start = current // window_seconds * window_seconds
    subject_hash = hashlib.sha256(subject.encode("utf-8")).hexdigest()
    try:
        with connection() as conn:
            row = conn.execute(
                """
                INSERT INTO rate_limit_buckets
                    (subject_hash, scope, bucket_start, request_count)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (subject_hash, scope, bucket_start)
                DO UPDATE SET
                    request_count = rate_limit_buckets.request_count + 1,
                    updated_at = now()
                RETURNING request_count
                """,
                (subject_hash, scope, bucket_start),
            ).fetchone()
    except Exception:
        raise RateLimitStorageUnavailable from None

    if not row or not isinstance(row[0], int):
        raise RateLimitStorageUnavailable
    if row[0] > limit:
        raise RateLimitExceeded(bucket_start + window_seconds - current)
