import pytest
from fastapi.testclient import TestClient

import core.auth as auth
import core.api as api
from core.config import Settings

client = TestClient(api.app)


@pytest.fixture(autouse=True)
def bypass_shared_rate_limit_for_unrelated_api_tests(monkeypatch):
    monkeypatch.setattr(api, "enforce_rate_limit", lambda *args, **kwargs: None)


def test_liveness_is_public_and_minimal():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_fails_when_database_is_unavailable(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "not_ready"


def test_oversized_body_is_rejected_before_parsing():
    response = client.post(
        "/v1/process",
        content=b"x" * (300 * 1024),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


def test_process_fails_closed_without_token(monkeypatch):
    monkeypatch.delenv("XILAC_API_TOKEN", raising=False)
    response = client.post("/v1/process", json={"text": "contenido privado"})
    assert response.status_code == 503


def test_process_rejects_wrong_token(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    response = client.post(
        "/v1/process",
        headers={"Authorization": "Bearer wrong"},
        json={"text": "x"},
    )
    assert response.status_code == 401


def test_process_returns_standard_privacy_warning_when_disabled(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)
    response = client.post(
        "/v1/process",
        headers={"Authorization": "Bearer test-secret"},
        json={"text": "texto de prueba"},
    )
    assert response.status_code == 423
    assert response.json()["status"] == "temporarily_blocked"
    assert "no recomendamos seguir con esta operación" in response.json()["notice"]
    assert "No envíes" in response.json()["notice"]


def test_process_flags_sensitive_content_without_echoing_matches(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    sensitive = "Nombre completo: Persona Ejemplo. Contacto: alexis@example.com"
    response = client.post(
        "/v1/process",
        headers={"Authorization": "Bearer test-secret"},
        json={"text": sensitive},
    )
    assert response.status_code == 423
    body = response.json()
    assert body["status"] == "privacy_warning"
    assert body["code"] == "POSSIBLE_SENSITIVE_CONTENT"
    assert "identificador_directo" in body["categories"]
    assert "alexis@example.com" not in response.text
    assert "Persona Ejemplo" not in response.text


def test_process_fails_closed_when_audit_storage_fails(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "settings", Settings(cfe_session_processing_enabled=True))

    def fail_audit(*args):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(api, "record_audit_event", fail_audit)
    response = client.post(
        "/v1/process",
        headers={"Authorization": "Bearer test-secret"},
        json={"text": "texto privado"},
    )
    assert response.status_code == 503
    assert "auditoría" in response.json()["detail"]


def test_oidc_role_without_permission_is_denied(monkeypatch):
    monkeypatch.setattr(
        auth,
        "settings",
        Settings(
            environment="staging",
            oidc_issuer="https://identity.example.test/",
            oidc_audience="xilac-api",
            oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
        ),
    )
    monkeypatch.setattr(
        auth,
        "_verify_oidc_token",
        lambda *args: {"sub": "consultant-1", "roles": ["auditor"]},
    )
    response = client.post(
        "/v1/process",
        headers={"Authorization": "Bearer valid-test-token"},
        json={"text": "texto privado"},
    )
    assert response.status_code == 403


def test_oidc_missing_configuration_fails_closed(monkeypatch):
    monkeypatch.setattr(auth, "settings", Settings(environment="staging"))
    response = client.post(
        "/v1/process",
        headers={"Authorization": "Bearer token"},
        json={"text": "texto privado"},
    )
    assert response.status_code == 503


def test_research_requires_authentication(monkeypatch):
    monkeypatch.delenv("XILAC_API_TOKEN", raising=False)
    response = client.post("/v1/research", json={"query": "climate adaptation"})
    assert response.status_code == 503


def test_research_blocks_sensitive_queries_before_provider(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)

    def unexpected_search(*args, **kwargs):
        raise AssertionError("provider must not be called for flagged query")

    monkeypatch.setattr(api, "search_web", unexpected_search)
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "mi diagnóstico de salud mental"},
    )
    assert response.status_code == 423
    assert response.json()["code"] == "POSSIBLE_SENSITIVE_CONTENT"


def test_research_fails_closed_when_audit_storage_fails(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")

    def fail_audit(*args):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(api, "record_audit_event", fail_audit)
    monkeypatch.setattr(
        api,
        "search_web",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not run")),
    )
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "renewable energy trends"},
    )
    assert response.status_code == 503
    assert "auditoría" in response.json()["detail"]


def test_research_returns_real_provider_results_without_query_logging(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    audit_events = []
    monkeypatch.setattr(api, "record_audit_event", lambda *args: audit_events.append(args))
    monkeypatch.setattr(
        api,
        "search_web",
        lambda query, count: {
            "provider": "brave_search",
            "query": query,
            "retrieved_at": "2026-10-10T12:00:00+00:00",
            "result_count": 1,
            "results": [{
                "title": "Renewable energy outlook",
                "url": "https://example.org/energy",
                "domain": "example.org",
                "description": "A source description",
                "published_at": None,
            }],
        },
    )
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "renewable energy trends", "count": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["synthesis_status"] == "not_generated"
    assert body["results"][0]["url"] == "https://example.org/energy"
    assert len(audit_events) == 1
    assert "renewable energy trends" not in repr(audit_events)


def test_research_requires_configured_provider(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "renewable energy trends"},
    )
    assert response.status_code == 503
    assert "no está configurada" in response.json()["detail"]


def test_research_rejects_blank_queries(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "   "},
    )
    assert response.status_code == 422


def test_research_ui_is_served_by_the_api():
    response = client.get("/research-ui/")
    assert response.status_code == 200
    assert "INVESTIGACIÓN UNIVERSAL" in response.text


def test_research_allows_general_medical_topics(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)
    monkeypatch.setattr(
        api,
        "search_web",
        lambda query, count: {
            "provider": "brave_search",
            "query": query,
            "retrieved_at": "2026-10-10T12:00:00+00:00",
            "result_count": 0,
            "results": [],
        },
    )
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "diagnóstico temprano de ELA: evidencia clínica", "domain": "science"},
    )
    assert response.status_code == 200
    assert response.json()["domain"] == "science"



def test_research_rate_limit_returns_429_and_retry_after(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(
        api,
        "enforce_rate_limit",
        lambda *args, **kwargs: (_ for _ in ()).throw(api.RateLimitExceeded(17)),
    )
    monkeypatch.setattr(
        api,
        "record_audit_event",
        lambda *args: (_ for _ in ()).throw(AssertionError("audit must not run")),
    )
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "renewable energy trends"},
    )
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "17"
    assert "límite temporal" in response.json()["detail"]


def test_research_rate_limit_fails_closed_if_storage_is_unavailable(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(
        api,
        "enforce_rate_limit",
        lambda *args, **kwargs: (_ for _ in ()).throw(api.RateLimitStorageUnavailable()),
    )
    monkeypatch.setattr(
        api,
        "record_audit_event",
        lambda *args: (_ for _ in ()).throw(AssertionError("audit must not run")),
    )
    response = client.post(
        "/v1/research",
        headers={"Authorization": "Bearer test-secret"},
        json={"query": "renewable energy trends"},
    )
    assert response.status_code == 503
    assert "límite de uso" in response.json()["detail"]
