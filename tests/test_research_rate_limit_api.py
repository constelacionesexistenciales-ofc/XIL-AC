from fastapi.testclient import TestClient

import core.api as api

client = TestClient(api.app)


def test_research_rate_limit_returns_429_and_retry_after(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-rate-limit-token")
    monkeypatch.setattr(
        api,
        "enforce_rate_limit",
        lambda *args, **kwargs: (_ for _ in ()).throw(api.RateLimitExceeded(17)),
    )
    provider_calls = []
    monkeypatch.setattr(api, "search_web", lambda *args: provider_calls.append(args))
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-rate-limit-token"},
        json={"query": "climate adaptation", "confirm_public_query": True},
    )
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "17"
    assert provider_calls == []


def test_research_rate_limit_storage_failure_blocks_provider(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-rate-limit-token")
    monkeypatch.setattr(
        api,
        "enforce_rate_limit",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            api.RateLimitStorageUnavailable()
        ),
    )
    provider_calls = []
    monkeypatch.setattr(api, "search_web", lambda *args: provider_calls.append(args))
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-rate-limit-token"},
        json={"query": "climate adaptation", "confirm_public_query": True},
    )
    assert response.status_code == 503
    assert provider_calls == []
