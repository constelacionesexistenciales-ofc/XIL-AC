from contextlib import contextmanager

import pytest

import scripts.cleanup_rate_limits as cleanup


class FakeCursor:
    def __init__(self, rowcount):
        self.rowcount = rowcount


class FakeConnection:
    def __init__(self, counts):
        self.counts = counts
        self.calls = []

    def execute(self, query, parameters):
        assert "DELETE FROM rate_limit_buckets" in query
        assert "LIMIT %s" in query
        self.calls.append(parameters)
        return FakeCursor(self.counts.pop(0))


def test_cleanup_deletes_in_bounded_committed_batches(monkeypatch):
    fake = FakeConnection([2, 2, 1])
    opens = []

    @contextmanager
    def connection():
        opens.append(True)
        yield fake

    monkeypatch.setattr(cleanup, "connection", connection)
    assert cleanup.cleanup_expired_rate_limits(retention_days=3, batch_size=2) == 5
    assert len(opens) == 3
    assert fake.calls == [(3, 2), (3, 2), (3, 2)]


@pytest.mark.parametrize(
    ("retention_days", "batch_size"),
    [(0, 10), (-1, 10), (2, 0), (2, 100001)],
)
def test_cleanup_rejects_unsafe_limits(retention_days, batch_size):
    with pytest.raises(ValueError):
        cleanup.cleanup_expired_rate_limits(
            retention_days=retention_days, batch_size=batch_size
        )


def test_cleanup_rejects_invalid_retention_environment(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_RETENTION_DAYS", "forever")
    with pytest.raises(ValueError, match="RATE_LIMIT_RETENTION_DAYS"):
        cleanup.cleanup_expired_rate_limits()
