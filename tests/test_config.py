import pytest

from core.config import Settings


def test_staging_requires_oidc_configuration():
    with pytest.raises(ValueError, match="OIDC_ISSUER"):
        Settings(environment="staging").validate()


def test_production_requires_database(monkeypatch):
    monkeypatch.setenv("OIDC_ISSUER", "https://identity.example.test/")
    monkeypatch.setenv("OIDC_AUDIENCE", "xilac-api")
    monkeypatch.setenv(
        "OIDC_JWKS_URL",
        "https://identity.example.test/.well-known/jwks.json",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings(environment="production").validate()


def test_production_does_not_allow_disabling_risk_gate(monkeypatch):
    monkeypatch.setenv("OIDC_ISSUER", "https://identity.example.test/")
    monkeypatch.setenv("OIDC_AUDIENCE", "xilac-api")
    monkeypatch.setenv(
        "OIDC_JWKS_URL",
        "https://identity.example.test/.well-known/jwks.json",
    )
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    with pytest.raises(ValueError, match="RISK_GATE_ENABLED"):
        Settings(environment="production", risk_gate_enabled=False).validate()


def test_oidc_urls_must_use_https():
    with pytest.raises(ValueError, match="HTTPS"):
        Settings(
            environment="production",
            oidc_issuer="http://identity.example.test/",
            oidc_audience="xilac-api",
            oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
        ).validate()
