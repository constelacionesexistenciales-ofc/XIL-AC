from contextlib import contextmanager

import pytest

import core.rate_limit as rate_limit


class FakeResult:
    def __init__(self, count):
        self.count = count

    def fetchone(self):
        return (self.count,)


class FakeConnection:
    def __init__(self, counts):
        self.counts = counts
        self.parameters = None

    def execute(self, query, parameters):
        assert "ON CONFLICT" in query
        self.parameters = parameters
        return FakeResult(self.counts.pop(0))


@contextmanager
def fake_db(connection):
    yield connection


def test_rate_limit_allows_requests_within_limit(monkeypatch):
    fake = FakeConnection([1, 2, 3])
    monkeypatch.setattr(rate_limit, "connection", lambda: fake_db(fake))
    for _ in range(3):
        rate_limit.enforce_rate_limit("user-1", "research", limit=3, window_seconds=60, now=121)
    assert fake.parameters[1:] == ("research", 120)


def test_rate_limit_rejects_over_limit_with_retry_after(monkeypatch):
    fake = FakeConnection([4])
    monkeypatch.setattr(rate_limit, "connection", lambda: fake_db(fake))
    with pytest.raises(rate_limit.RateLimitExceeded) as caught:
        rate_limit.enforce_rate_limit("user-1", "research", limit=3, window_seconds=60, now=121)
    assert caught.value.retry_after == 59


def test_rate_limit_hashes_subject_before_persisting(monkeypatch):
    fake = FakeConnection([1])
    monkeypatch.setattr(rate_limit, "connection", lambda: fake_db(fake))
    rate_limit.enforce_rate_limit("private-subject", "research", now=121)
    assert fake.parameters[0] != "private-subject"
    assert len(fake.parameters[0]) == 64


def test_rate_limit_fails_closed_when_database_is_unavailable(monkeypatch):
    @contextmanager
    def unavailable():
        raise RuntimeError("database unavailable")
        yield  # pragma: no cover

    monkeypatch.setattr(rate_limit, "connection", unavailable)
    with pytest.raises(rate_limit.RateLimitStorageUnavailable):
        rate_limit.enforce_rate_limit("user-1", "research")


@pytest.mark.parametrize(
    ("limit", "window_seconds"),
    [(0, 60), (10, 0), (-1, 60)],
)
def test_rate_limit_rejects_invalid_configuration(limit, window_seconds):
    with pytest.raises(ValueError):
        rate_limit.enforce_rate_limit(
            "user-1", "research", limit=limit, window_seconds=window_seconds
        )

def test_rate_limit_uses_new_bucket_after_window_rollover(monkeypatch):
    fake = FakeConnection([1, 1])
    monkeypatch.setattr(rate_limit, "connection", lambda: fake_db(fake))
    rate_limit.enforce_rate_limit("user-1", "research", limit=1, window_seconds=60, now=119)
    rate_limit.enforce_rate_limit("user-1", "research", limit=1, window_seconds=60, now=120)
    # Each request is assigned to its own fixed-window bucket at the boundary.
    assert fake.parameters[2] == 120


def test_rate_limit_isolates_subjects_and_scopes(monkeypatch):
    fake = FakeConnection([1, 1, 1])
    monkeypatch.setattr(rate_limit, "connection", lambda: fake_db(fake))
    rate_limit.enforce_rate_limit("user-1", "research", now=121)
    first_subject_hash, first_scope, first_bucket = fake.parameters
    rate_limit.enforce_rate_limit("user-2", "research", now=121)
    second_subject_hash, second_scope, second_bucket = fake.parameters
    rate_limit.enforce_rate_limit("user-1", "admin-research", now=121)
    third_subject_hash, third_scope, third_bucket = fake.parameters
    assert first_subject_hash != second_subject_hash
    assert first_scope == second_scope == "research"
    assert third_scope == "admin-research"
    assert first_bucket == second_bucket == third_bucket == 120


def test_rate_limit_rejects_empty_subject(monkeypatch):
    with pytest.raises(ValueError, match="subject"):
        rate_limit.enforce_rate_limit("   ", "research")
