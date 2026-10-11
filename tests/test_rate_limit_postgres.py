from concurrent.futures import ThreadPoolExecutor
import os
from hashlib import sha256
from uuid import uuid4

import psycopg
import pytest

from core.rate_limit import RateLimitExceeded, enforce_rate_limit


def test_rate_limit_is_shared_and_persisted_in_postgresql(monkeypatch):
    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL is not configured")
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
    dsn = __import__("os").getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL is not configured")
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
