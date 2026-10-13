from fastapi.testclient import TestClient

import core.api as api

client = TestClient(api.app)


def _auth(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-research-token")
    return {"Authorization": "Bearer test-research-token"}


def test_research_requires_authentication(monkeypatch):
    monkeypatch.delenv("XILAC_API_TOKEN", raising=False)
    response = client.post("/v1/research", json={"query": "climate adaptation"})
    assert response.status_code == 503


def test_research_blocks_sensitive_query_before_provider(monkeypatch):
    headers = _auth(monkeypatch)
    called = []
    monkeypatch.setattr(api, "search_web", lambda *args: called.append(args))
    response = client.post(
        "/v1/research",
        headers=headers,
        json={"query": "Mi diagnóstico es ansiedad y mi correo es alexis@example.com"},
    )
    assert response.status_code == 423
    assert response.json()["status"] == "privacy_warning"
    assert "alexis@example.com" not in response.text
    assert called == []


def test_research_blocks_when_audit_fails(monkeypatch):
    headers = _auth(monkeypatch)
    monkeypatch.setattr(api, "enforce_rate_limit", lambda *args, **kwargs: None)
    def fail_audit(*args):
        raise RuntimeError("storage unavailable")
    monkeypatch.setattr(api, "record_audit_event", fail_audit)
    called = []
    monkeypatch.setattr(api, "search_web", lambda *args: called.append(args))
    response = client.post(
        "/v1/research",
        headers=headers,
        json={"query": "climate adaptation", "confirm_public_query": True},
    )
    assert response.status_code == 503
    assert called == []


def test_research_provider_not_configured_fails_closed(monkeypatch):
    headers = _auth(monkeypatch)
    monkeypatch.setattr(api, "enforce_rate_limit", lambda *args, **kwargs: None)
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)
    monkeypatch.setattr(
        api,
        "search_web",
        lambda *args: (_ for _ in ()).throw(api.ResearchProviderNotConfigured()),
    )
    response = client.post(
        "/v1/research",
        headers=headers,
        json={"query": "climate adaptation", "confirm_public_query": True},
    )
    assert response.status_code == 503


def test_research_success_returns_trace_and_disclaims_synthesis(monkeypatch):
    headers = _auth(monkeypatch)
    monkeypatch.setattr(api, "enforce_rate_limit", lambda *args, **kwargs: None)
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)
    monkeypatch.setattr(
        api,
        "search_web",
        lambda query, count, domain: {
            "provider": "brave_search",
            "query": query,
            "retrieved_at": "2026-10-11T00:00:00+00:00",
            "result_count": 1,
            "results": [
                {
                    "title": "Source",
                    "url": "https://example.org/source",
                    "domain": "example.org",
                    "description": "Evidence",
                    "published_at": None,
                }
            ],
        },
    )
    response = client.post(
        "/v1/research",
        headers=headers,
        json={
            "query": "climate adaptation",
            "confirm_public_query": True,
            "domain": "science",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["execution_id"]
    assert body["synthesis_status"] == "not_generated"
    assert body["evidence_registry_valid"] is True
    assert body["research_report"]["evidence"][0]["evidence_id"] == "e1"
    assert body["research_report"]["claims"][0]["status"] == "abstain"
    assert body["result_count"] == 1
    assert body["domain"] == "science"


def test_research_requires_explicit_public_query_confirmation(monkeypatch):
    headers = _auth(monkeypatch)
    called = []
    monkeypatch.setattr(api, "search_web", lambda *args: called.append(args))
    response = client.post("/v1/research", headers=headers, json={"query": "climate adaptation"})
    assert response.status_code == 423
    assert response.json()["code"] == "PUBLIC_RESEARCH_CONFIRMATION_REQUIRED"
    assert called == []

def test_research_blocks_session_material_before_provider(monkeypatch):
    headers = _auth(monkeypatch)
    called = []
    monkeypatch.setattr(api, "search_web", lambda *args: called.append(args))
    queries = [
        "Preparar un resumen de la " + "sesión con un consultante",
        "Redactar el " + "informe de sesión para paciente",
        "Analizar la " + "transcripción de la sesión",
        "Preparar " + "notas de la sesión",
    ]
    for query in queries:
        response = client.post(
            "/v1/research",
            headers=headers,
            json={"query": query, "confirm_public_query": True},
        )
        assert response.status_code == 423, query
        assert response.json()["code"] == "POSSIBLE_SENSITIVE_CONTENT", query
    assert called == []
