import os
from uuid import uuid4

import psycopg
import pytest

from core.audit import record_audit_event
from scripts.migrate import main


def test_migration_runner_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(SystemExit, match="DATABASE_URL"):
        main()


def test_migrations_apply_idempotently_to_postgresql(monkeypatch):
    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL no está configurada")
    monkeypatch.setenv("DATABASE_URL", dsn)

    main()
    main()

    with psycopg.connect(dsn) as conn:
        version = conn.execute(
            "SELECT version FROM schema_migrations WHERE version = %s",
            ("0001_initial",),
        ).fetchone()
        rate_limit_version = conn.execute(
            "SELECT version FROM schema_migrations WHERE version = %s",
            ("0002_rate_limit_buckets",),
        ).fetchone()
        avc_version = conn.execute(
            "SELECT version FROM schema_migrations WHERE version = %s",
            ("0003_avc_archive",),
        ).fetchone()
        table = conn.execute("SELECT to_regclass('public.audit_events')").fetchone()
        rate_limit_table = conn.execute(
            "SELECT to_regclass('public.rate_limit_buckets')"
        ).fetchone()
        avc_conversations = conn.execute(
            "SELECT to_regclass('public.avc_conversations')"
        ).fetchone()
        avc_messages = conn.execute(
            "SELECT to_regclass('public.avc_messages')"
        ).fetchone()

    assert version == ("0001_initial",)
    assert rate_limit_version == ("0002_rate_limit_buckets",)
    assert avc_version == ("0003_avc_archive",)
    assert table == ("audit_events",)
    assert rate_limit_table == ("rate_limit_buckets",)
    assert avc_conversations == ("avc_conversations",)
    assert avc_messages == ("avc_messages",)


def test_audit_event_persists_without_session_content(monkeypatch):
    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL no está configurada")
    monkeypatch.setenv("DATABASE_URL", dsn)
    execution_id = str(uuid4())

    record_audit_event(execution_id, "test.event", "test-actor", "ok")

    with psycopg.connect(dsn) as conn:
        event = conn.execute(
            """
            SELECT execution_id::text, event_type, actor_id, outcome
            FROM audit_events
            WHERE execution_id = %s
            """,
            (execution_id,),
        ).fetchone()

    assert event == (execution_id, "test.event", "test-actor", "ok")
