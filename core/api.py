"""API mínima de XIL-AC con control de roles, auditoría y respuestas honestas."""
from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from core.audit import record_audit_event
from core.evidence_registry import EvidenceRecord, ResearchReport, abstention_claim
from core.auth import Principal, require_roles
from core.config import Settings
from core.db import check_database
from core.middleware import MaxRequestBodySizeMiddleware
from core.privacy_detector import detect_research_sensitive_content, detect_sensitive_content
from core.research import (
    ResearchProviderNotConfigured,
    ResearchProviderUnavailable,
    ResearchRateLimited,
    search_web,
)
from core.trace import new_trace

settings = Settings()
PRIVACY_WARNING = (
    "La información recibida contiene o podría contener material sensible; "
    "no recomendamos seguir con esta operación. En esta etapa, no envíes "
    "transcripciones, audios ni datos identificables a la API remota. "
    "Continuá el trabajo de sesiones mediante la interfaz de ChatGPT acordada. "
    "La investigación general y el desarrollo metodológico pueden continuar "
    "por esa interfaz."
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings.validate()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.4.1",
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
    # Defensa adicional: este análisis ocurre después de que el cuerpo llegó a la API.
    # No reemplaza un control local previo al envío ni garantiza detectar todo.
    finding = detect_sensitive_content(request.text)
    if finding.should_warn:
        return JSONResponse(
            status_code=423,
            content={
                "status": "privacy_warning",
                "code": "POSSIBLE_SENSITIVE_CONTENT",
                "risk": finding.risk,
                "categories": list(finding.categories),
                "notice": PRIVACY_WARNING,
            },
        )

    # Gate cerrado por defecto incluso si el detector no encuentra señales.
    if not settings.cfe_session_processing_enabled:
        return JSONResponse(
            status_code=423,
            content={
                "status": "temporarily_blocked",
                "code": "CFE_SESSION_PROCESSING_DISABLED",
                "notice": PRIVACY_WARNING,
            },
        )
    # El motor aún no está conectado; no registrar la transcripción.
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



class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    count: int = Field(default=5, ge=1, le=10)
    domain: str = Field(
        default="general",
        pattern="^(general|science|history|technology|business|education|cfe)$",
    )

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 3:
            raise ValueError("La consulta debe contener al menos 3 caracteres útiles.")
        return normalized


@app.post("/v1/research")
def research(
    request: ResearchRequest,
    principal: Principal = Depends(require_roles("facilitator", "admin")),
) -> JSONResponse:
    """Search public web sources for general research; never stores query text."""
    finding = detect_research_sensitive_content(request.query)
    if finding.should_warn:
        return JSONResponse(
            status_code=423,
            content={
                "status": "privacy_warning",
                "code": "POSSIBLE_SENSITIVE_CONTENT",
                "risk": finding.risk,
                "categories": list(finding.categories),
                "notice": PRIVACY_WARNING,
            },
        )

    trace = new_trace()
    try:
        # Persist intent before sending the query to an external provider.
        record_audit_event(
            trace.execution_id,
            "research.request",
            principal.subject,
            "accepted",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo registrar la auditoría; la búsqueda fue bloqueada.",
        ) from None

    try:
        result = search_web(request.query, request.count)
    except ResearchProviderNotConfigured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La búsqueda web no está configurada. Falta habilitar el proveedor autorizado.",
        ) from None
    except ResearchRateLimited:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El proveedor de búsqueda limitó temporalmente las solicitudes.",
            headers={"Retry-After": "30"},
        ) from None
    except ResearchProviderUnavailable:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El proveedor de búsqueda no está disponible o devolvió una respuesta inválida.",
        ) from None

    evidence_records = [
        EvidenceRecord(
            evidence_id=f"e{index}",
            url=item["url"],
            title=item["title"],
            publisher=item.get("domain") or "publisher_unknown",
            retrieved_at=result["retrieved_at"],
            excerpt=item.get("description") or "",
            source_type="web",
        )
        for index, item in enumerate(result.get("results", []), start=1)
    ]
    research_report = ResearchReport(
        execution_id=trace.execution_id,
        question=request.query,
        evidence=evidence_records,
        claims=[
            abstention_claim(
                "c1",
                (
                    "Se recuperaron fuentes, pero todavía no existe síntesis "
                    "ni contraste automatizado."
                ),
            )
        ],
        limitations=[
            "La recuperación de fuentes no verifica por sí sola la exactitud de su contenido.",
            "No se han contrastado afirmaciones entre fuentes independientes.",
        ],
    )
    if not research_report.is_publishable():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Las fuentes recuperadas no superaron la validación de trazabilidad.",
        )

    return JSONResponse(
        content={
            "execution_id": trace.execution_id,
            "status": "completed",
            "mode": "web_search",
            "domain": request.domain,
            "synthesis_status": "not_generated",
            "evidence_registry_valid": True,
            "research_report": research_report.to_dict(),
            **result,
        }
    )


_UI_DIRECTORY = Path(__file__).resolve().parent.parent / "frontend" / "universal-research"
if _UI_DIRECTORY.is_dir():
    app.mount("/research-ui", StaticFiles(directory=_UI_DIRECTORY, html=True), name="research-ui")
