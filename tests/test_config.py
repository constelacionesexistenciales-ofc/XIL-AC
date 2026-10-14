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


def test_production_cannot_enable_unimplemented_session_engine(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    settings = Settings(
        environment="production",
        oidc_issuer="https://identity.example.test/",
        oidc_audience="xilac-api",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
        cfe_session_processing_enabled=True,
    )
    with pytest.raises(ValueError, match="CFE_SESSION_PROCESSING_ENABLED"):
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


@pytest.mark.parametrize(
    "issuer,jwks",
    [
        ("https:///missing-host", "https://identity.example.test/keys"),
        ("https://identity.example.test/", "https://user:pass@identity.example.test/keys"),
        ("https://identity.example.test/?token=secret", "https://identity.example.test/keys"),
        ("https://identity.example.test/", "https://identity.example.test/keys#fragment"),
        ("https://identity.example.test/", "https://identity.example.test:99999/keys"),
    ],
)
def test_oidc_endpoints_reject_ambiguous_or_credential_bearing_urls(issuer, jwks):
    settings = Settings(
        environment="production",
        oidc_issuer=issuer,
        oidc_audience="xilac-api",
        oidc_jwks_url=jwks,
    )
    with pytest.raises(ValueError, match="absolute HTTPS URL"):
        settings.validate()


def test_oidc_endpoints_accept_absolute_https_urls(monkeypatch):
    settings = Settings(
        environment="production",
        oidc_issuer="https://identity.example.test/tenant",
        oidc_audience="xilac-api",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
    )
    # Set only the unrelated required database and gate prerequisites.
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    settings.validate()
