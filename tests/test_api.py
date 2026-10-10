from fastapi.testclient import TestClient
from core.api import app

client = TestClient(app)

def test_liveness_is_public_and_minimal():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_process_fails_closed_without_token(monkeypatch):
    monkeypatch.delenv("XILAC_API_TOKEN", raising=False)
    response = client.post("/v1/process", json={"text": "contenido privado"})
    assert response.status_code == 503

def test_process_rejects_wrong_token(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    response = client.post("/v1/process", headers={"Authorization": "Bearer wrong"}, json={"text": "x"})
    assert response.status_code == 401
