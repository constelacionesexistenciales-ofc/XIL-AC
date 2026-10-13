from fastapi.testclient import TestClient

import core.auth as auth
import core.api as api
from core.config import Settings

client = TestClient(api.app)


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
    assert "no envíes" in response.json()["notice"].lower()


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


def test_session_movement_ui_is_mounted():
    response = client.get("/session-movement/")
    assert response.status_code == 200
    assert "Indicador de movimiento" in response.text


def test_session_movement_api_is_disabled_by_default(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "settings", Settings(session_movement_enabled=False))
    response = client.post(
        "/v1/session-movement/sessions",
        headers={"Authorization": "Bearer test-secret"},
        json={"objective": "stabilization"},
    )
    assert response.status_code == 423
    assert response.json()["detail"]["code"] == "SESSION_MOVEMENT_DISABLED"


def test_session_movement_start_requires_facilitator_role(monkeypatch):
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
        lambda *args: {"sub": "auditor-1", "roles": ["auditor"]},
    )
    monkeypatch.setattr(api, "settings", Settings(session_movement_enabled=True))
    response = client.post(
        "/v1/session-movement/sessions",
        headers={"Authorization": "Bearer valid-test-token"},
        json={"objective": "stabilization"},
    )
    assert response.status_code == 403


def test_session_movement_start_returns_created_session_without_database(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "settings", Settings(session_movement_enabled=True))
    monkeypatch.setattr(api, "record_audit_event", lambda *args: None)
    monkeypatch.setattr(
        api, "create_session",
        lambda actor_id, objective: {
            "session_id": "2f4d30ab-44e5-48df-8c6d-cdbad0f11d4b",
            "objective": objective.value,
            "created_at": "2026-10-13T12:00:00+00:00",
            "status": "open",
        },
    )
    response = client.post(
        "/v1/session-movement/sessions",
        headers={"Authorization": "Bearer test-secret"},
        json={"objective": "stabilization"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert response.json()["objective"] == "stabilization"


def test_session_movement_rejects_invalid_scores_before_storage(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setattr(api, "settings", Settings(session_movement_enabled=True))
    response = client.post(
        "/v1/session-movement/sessions/2f4d30ab-44e5-48df-8c6d-cdbad0f11d4b/snapshots",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "phase": "arrival",
            "source": "jointly_reviewed",
            "scores": {"availability": 9},
        },
    )
    assert response.status_code == 422
