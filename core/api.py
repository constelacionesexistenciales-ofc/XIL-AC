"""API mínima; procesos sensibles requieren token y no registran contenido recibido."""
from __future__ import annotations

import hmac
import os
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from core.config import Settings
from core.trace import new_trace

settings = Settings()
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None,
)


class ProcessRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    mode: str = Field(default="session_support", pattern="^(session_support|report_draft)$")


class ProcessResponse(BaseModel):
    execution_id: str
    status: str
    message: str


def require_token(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = os.getenv("XILAC_API_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio protegido no configurado",
        )
    supplied = authorization or ""
    prefix = "Bearer "
    if not supplied.startswith(prefix) or not hmac.compare_digest(
        supplied[len(prefix):], expected
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.on_event("startup")
def validate_settings() -> None:
    settings.validate()


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "database": "not_checked"}


@app.post(
    "/v1/process",
    response_model=ProcessResponse,
    dependencies=[Depends(require_token)],
)
def process(_: ProcessRequest) -> ProcessResponse:
    trace = new_trace()
    return ProcessResponse(
        execution_id=trace.execution_id,
        status="not_implemented",
        message="El motor de procesamiento todavía no está conectado.",
    )
