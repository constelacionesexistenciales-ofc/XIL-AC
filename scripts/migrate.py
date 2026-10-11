"""Ejecutor simple e idempotente de migraciones SQL numeradas."""
from __future__ import annotations

import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "migrations"


def main() -> None:
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        raise SystemExit("DATABASE_URL es obligatoria para ejecutar migraciones.")

    with psycopg.connect(dsn, connect_timeout=5) as conn:
        # Serialize migration runners across instances; session lock releases on disconnect.
        conn.execute("SELECT pg_advisory_lock(721840913)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        applied = {
            row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }
        for path in sorted(MIGRATIONS.glob("[0-9]*.sql")):
            version = path.stem
            if version in applied:
                continue
            sql = path.read_text(encoding="utf-8")
            with conn.transaction():
                conn.execute(sql, prepare=False)
                conn.execute(
                    "INSERT INTO schema_migrations(version) VALUES (%s)",
                    (version,),
                )
            print(f"Aplicada migración: {version}")
        conn.execute("SELECT pg_advisory_unlock(721840913)")


if __name__ == "__main__":
    main()
