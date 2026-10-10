import pytest

from core.config import Settings


def test_production_requires_api_token(monkeypatch):
    monkeypatch.delenv("XILAC_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="XILAC_API_TOKEN"):
        Settings(environment="production").validate()


def test_production_requires_database(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings(environment="production").validate()


def test_production_does_not_allow_disabling_risk_gate(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    with pytest.raises(ValueError, match="RISK_GATE_ENABLED"):
        Settings(environment="production", risk_gate_enabled=False).validate()


def test_invalid_environment_is_rejected():
    with pytest.raises(ValueError, match="APP_ENV"):
        Settings(environment="prod").validate()
