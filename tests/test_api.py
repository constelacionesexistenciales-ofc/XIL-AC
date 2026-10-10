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
