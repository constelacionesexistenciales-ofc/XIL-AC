"""API mínima de XIL-AC con control de roles, auditoría y respuestas honestas."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.audit import record_audit_event
from core.auth import Principal, require_roles
from core.config import Settings
from core.db import check_database
from core.middleware import MaxRequestBodySizeMiddleware
from core.trace import new_trace

settings = Settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings.validate()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.3.1",
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None,
    lifespan=lifespan,
)
app.add_middleware(MaxRequestBodySizeMiddleware, max_bytes=256 * 1024)


class ProcessRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    mode: str = Field(default="session_support", pattern="^(session_support|report_draft)$")


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


@app.post("/v1/process")
def process(
    request: ProcessRequest,
    principal: Principal = Depends(require_roles("facilitator", "admin")),
) -> JSONResponse:
    # No registrar la transcripción: solo se conserva un evento técnico mínimo.
    _ = request.mode, request.text
    trace = new_trace()
    try:
        record_audit_event(
            trace.execution_id,
            "process.request",
            principal.subject,
            "engine_not_implemented",
        )
    except Exception:
        # No ejecutar operaciones sensibles si la auditoría no puede persistirse.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo registrar la auditoría; la solicitud fue bloqueada.",
        ) from None
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "execution_id": trace.execution_id,
            "status": "not_implemented",
            "message": "El motor de procesamiento todavía no está conectado.",
        },
    )
