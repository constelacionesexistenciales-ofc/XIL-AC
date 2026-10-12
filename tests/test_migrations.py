import os
from concurrent.futures import ThreadPoolExecutor
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
        table = conn.execute("SELECT to_regclass('public.audit_events')").fetchone()
        rate_limit_table = conn.execute(
            "SELECT to_regclass('public.rate_limit_buckets')"
        ).fetchone()
        versions = conn.execute("SELECT version FROM schema_migrations").fetchall()

    assert version == ("0001_initial",)
    assert table == ("audit_events",)
    assert rate_limit_table == ("rate_limit_buckets",)
    assert ("0002_rate_limit_buckets",) in versions


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



def test_rate_limit_is_shared_and_persisted_in_postgresql(monkeypatch):
    from hashlib import sha256

    from core.rate_limit import RateLimitExceeded, enforce_rate_limit

    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL no está configurada")
    monkeypatch.setenv("DATABASE_URL", dsn)
    subject = f"rate-limit-test-{uuid4()}"

    enforce_rate_limit(subject, "research-integration", limit=2, window_seconds=60)
    enforce_rate_limit(subject, "research-integration", limit=2, window_seconds=60)
    with pytest.raises(RateLimitExceeded):
        enforce_rate_limit(subject, "research-integration", limit=2, window_seconds=60)

    subject_hash = sha256(subject.encode("utf-8")).hexdigest()
    with psycopg.connect(dsn) as conn:
        row = conn.execute(
            """
            SELECT request_count FROM rate_limit_buckets
            WHERE subject_hash = %s AND scope = %s
            ORDER BY bucket_start DESC LIMIT 1
            """,
            (subject_hash, "research-integration"),
        ).fetchone()
    assert row is not None
    assert row[0] == 3



def test_rate_limit_enforces_limit_across_concurrent_requests(monkeypatch):
    from core.rate_limit import RateLimitExceeded, enforce_rate_limit

    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL no está configurada")
    monkeypatch.setenv("DATABASE_URL", dsn)
    subject = f"rate-limit-concurrent-{uuid4()}"

    def attempt(_):
        try:
            enforce_rate_limit(
                subject,
                "research-concurrency",
                limit=3,
                window_seconds=60,
            )
            return "allowed"
        except RateLimitExceeded:
            return "limited"

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(attempt, range(10)))

    assert outcomes.count("allowed") == 3
    assert outcomes.count("limited") == 7
