import pytest

from core.config import Settings


def test_staging_requires_oidc_configuration():
    with pytest.raises(ValueError, match="OIDC_ISSUER"):
        Settings(environment="staging").validate()


def test_production_requires_database(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(
        environment="production",
        oidc_issuer="https://identity.example.test/",
        oidc_audience="xilac-api",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
    )
    with pytest.raises(ValueError, match="DATABASE_URL"):
        settings.validate()


def test_production_does_not_allow_disabling_risk_gate(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    settings = Settings(
        environment="production",
        oidc_issuer="https://identity.example.test/",
        oidc_audience="xilac-api",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
        risk_gate_enabled=False,
    )
    with pytest.raises(ValueError, match="RISK_GATE_ENABLED"):
        settings.validate()


def test_oidc_urls_must_use_https():
    settings = Settings(
        environment="production",
        oidc_issuer="http://identity.example.test/",
        oidc_audience="xilac-api",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
    )
    with pytest.raises(ValueError, match="HTTPS"):
        settings.validate()
