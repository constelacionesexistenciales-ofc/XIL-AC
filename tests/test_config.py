import pytest
from core.config import Settings


def test_production_requires_api_token(monkeypatch):
    monkeypatch.delenv("XILAC_API_TOKEN", raising=False)
    with pytest.raises(ValueError):
        Settings(environment="production").validate()


def test_production_does_not_allow_disabling_risk_gate(monkeypatch):
    monkeypatch.setenv("XILAC_API_TOKEN", "test-secret")
    with pytest.raises(ValueError):
        Settings(environment="production", risk_gate_enabled=False).validate()
