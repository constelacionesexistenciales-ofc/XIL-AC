"""API mínima de XIL-AC: autenticación fail-closed y comprobaciones honestas."""
from __future__ import annotations

import hmac
import os
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.config import Settings
from core.db import check_database
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
    try:
        database_ok = check_database()
    except Exception:
        database_ok = False
    if not database_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "database": "unavailable"},
        )
    return {"status": "ready", "database": "available"}


@app.post("/v1/process", dependencies=[Depends(require_token)])
def process(request: ProcessRequest) -> JSONResponse:
    # No simular procesamiento ni registrar la transcripción: el motor CFE
    # debe conectarse y probarse antes de habilitar este endpoint.
    _ = request.mode, request.text
    trace = new_trace()
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "execution_id": trace.execution_id,
            "status": "not_implemented",
            "message": "El motor de procesamiento todavía no está conectado.",
        },
    )
