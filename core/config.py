from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "XIL-AC")
    environment: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    trace_enabled: bool = (
        os.getenv("TRACE_ENABLED", "true").lower() == "true"
    )

    risk_gate_enabled: bool = (
        os.getenv("RISK_GATE_ENABLED", "true").lower() == "true"
    )

    human_override_enabled: bool = (
        os.getenv("HUMAN_OVERRIDE_ENABLED", "true").lower() == "true"
    )