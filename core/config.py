from dataclasses import dataclass
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

    def validate(self) -> None:
        if self.environment not in {"development", "test", "staging", "production"}:
            raise ValueError("APP_ENV must be development, test, staging or production")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL is invalid")
        if self.environment == "production" and not os.getenv("XILAC_API_TOKEN", "").strip():
            raise ValueError("XILAC_API_TOKEN is required in production")
        if self.environment == "production" and not os.getenv("DATABASE_URL", "").strip():
            raise ValueError("DATABASE_URL is required in production")
        if self.environment == "production" and not self.risk_gate_enabled:
            raise ValueError("RISK_GATE_ENABLED cannot be disabled in production")
