"""Limpieza por lotes de buckets antiguos del limitador compartido.

Ejecutar periódicamente como tarea operativa (por ejemplo, una vez al día).
Solo imprime el número total eliminado; nunca registra identidades ni consultas.
"""
from __future__ import annotations

import os

from core.db import connection


def cleanup_expired_rate_limits(
    *, retention_days: int | None = None, batch_size: int = 10_000
) -> int:
    """Elimina en transacciones pequeñas los buckets cuyo último uso es antiguo."""
    if retention_days is None:
        try:
            retention_days = int(os.getenv("RATE_LIMIT_RETENTION_DAYS", "2"))
        except ValueError:
            raise ValueError("RATE_LIMIT_RETENTION_DAYS debe ser un entero") from None
    if retention_days < 1:
        raise ValueError("retention_days debe ser al menos 1")
    if batch_size < 1 or batch_size > 100_000:
        raise ValueError("batch_size debe estar entre 1 y 100000")

    total_deleted = 0
    while True:
        with connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM rate_limit_buckets
                WHERE ctid IN (
                    SELECT ctid
                    FROM rate_limit_buckets
                    WHERE updated_at < now() - (%s * interval '1 day')
                    ORDER BY updated_at
                    LIMIT %s
                )
                """,
                (retention_days, batch_size),
            )
            deleted = max(0, cursor.rowcount)
        total_deleted += deleted
        if deleted < batch_size:
            return total_deleted


def main() -> None:
    deleted = cleanup_expired_rate_limits()
    print(f"Buckets de limitación antiguos eliminados: {deleted}")


if __name__ == "__main__":
    main()
