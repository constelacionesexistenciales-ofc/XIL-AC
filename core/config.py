from dataclasses import dataclass
from urllib.parse import urlparse
import os


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"{name} must be true or false")
    return normalized == "true"


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "XIL-AC")
    environment: str = os.getenv("APP_ENV", "development").strip().lower()
    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    trace_enabled: bool = _env_bool("TRACE_ENABLED", True)
    risk_gate_enabled: bool = _env_bool("RISK_GATE_ENABLED", True)
    human_override_enabled: bool = _env_bool("HUMAN_OVERRIDE_ENABLED", True)
    cfe_session_processing_enabled: bool = _env_bool("CFE_SESSION_PROCESSING_ENABLED", False)
    oidc_issuer: str = os.getenv("OIDC_ISSUER", "").strip()
    oidc_audience: str = os.getenv("OIDC_AUDIENCE", "").strip()
    oidc_jwks_url: str = os.getenv("OIDC_JWKS_URL", "").strip()
    oidc_roles_claim: str = os.getenv("OIDC_ROLES_CLAIM", "roles").strip()
    research_rate_limit_requests: int = int(os.getenv("RESEARCH_RATE_LIMIT_REQUESTS", "30"))
    research_rate_limit_window_seconds: int = int(os.getenv("RESEARCH_RATE_LIMIT_WINDOW_SECONDS", "60"))

    def validate(self) -> None:
        if self.environment not in {"development", "test", "staging", "production"}:
            raise ValueError("APP_ENV must be development, test, staging or production")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL is invalid")
        if self.research_rate_limit_requests < 1:
            raise ValueError("RESEARCH_RATE_LIMIT_REQUESTS must be positive")
        if self.research_rate_limit_window_seconds < 1:
            raise ValueError("RESEARCH_RATE_LIMIT_WINDOW_SECONDS must be positive")
        if self.environment in {"staging", "production"}:
            if not self.oidc_issuer:
                raise ValueError("OIDC_ISSUER is required in staging and production")
            if not self.oidc_audience:
                raise ValueError("OIDC_AUDIENCE is required in staging and production")
            if not self.oidc_jwks_url:
                raise ValueError("OIDC_JWKS_URL is required in staging and production")
            if urlparse(self.oidc_issuer).scheme != "https":
                raise ValueError("OIDC_ISSUER must use HTTPS")
            if urlparse(self.oidc_jwks_url).scheme != "https":
                raise ValueError("OIDC_JWKS_URL must use HTTPS")
            if not self.oidc_roles_claim:
                raise ValueError("OIDC_ROLES_CLAIM cannot be empty")
            if not os.getenv("DATABASE_URL", "").strip():
                raise ValueError("DATABASE_URL is required in staging and production")
            if not self.risk_gate_enabled:
                raise ValueError("RISK_GATE_ENABLED cannot be disabled in staging or production")
