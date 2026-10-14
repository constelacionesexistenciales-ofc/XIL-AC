"""Orquestación segura del cierre post-sesión; no ejecuta ni transmite sesiones reales.

Este módulo define el orden y las precondiciones. La conexión al motor CFE y al evento
real de cierre queda deliberadamente fuera hasta que exista un adaptador aprobado.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Callable


class Stage(StrEnum):
    LAST_READING = "last_reading_feedback"
    PHENOMENOLOGICAL_REVIEW = "full_session_phenomenological_review"
    FACILITATOR_REPORT = "facilitator_report"
    CONSULTANT_REPORT = "consultant_report"
    PROCESS_AUDIT = "process_audit"
    ASSISTANT_AUDIT = "assistant_operational_audit"
    TESTING_AND_IMPROVEMENTS = "testing_results_and_improvements"


REQUIRED_ORDER = tuple(Stage)


@dataclass(frozen=True)
class PostSessionRequest:
    execution_id: str
    session_id: str
    transcript: str
    session_end_confirmed: bool
    synthetic_data: bool = True
    processing_enabled: bool = False


@dataclass(frozen=True)
class StageResult:
    stage: Stage
    status: str
    output: str = ""


@dataclass(frozen=True)
class PostSessionResult:
    execution_id: str
    transcript_sha256: str
    status: str
    stages: tuple[StageResult, ...]
    human_review_required: bool = True


class PostSessionBlocked(ValueError):
    """Solicitud bloqueada por precondiciones de seguridad."""


def run_post_session(
    request: PostSessionRequest,
    handlers: dict[Stage, Callable[[PostSessionRequest, tuple[StageResult, ...]], str]],
) -> PostSessionResult:
    """Ejecuta el flujo en orden estricto y falla de forma cerrada.

    Los handlers son inyectados por el integrador. No se registra ni devuelve la
    transcripción; el resumen de salida solo contiene su huella criptográfica.
    """
    if not request.execution_id.strip() or not request.session_id.strip():
        raise PostSessionBlocked("Se requieren execution_id y session_id.")
    if not request.session_end_confirmed:
        raise PostSessionBlocked("El cierre de sesión no fue confirmado.")
    if not request.transcript.strip():
        raise PostSessionBlocked("No hay transcripción completa para revisar.")
    if not request.synthetic_data and not request.processing_enabled:
        raise PostSessionBlocked("El procesamiento de sesiones reales está deshabilitado.")
    if set(handlers) != set(REQUIRED_ORDER):
        raise PostSessionBlocked("Falta uno o más componentes obligatorios del flujo.")

    results: list[StageResult] = []
    for stage in REQUIRED_ORDER:
        try:
            output = handlers[stage](request, tuple(results))
        except Exception:
            # No se propagan mensajes que podrían contener datos de sesión.
            raise PostSessionBlocked(f"Se bloqueó el flujo en la etapa {stage.value}.") from None
        if not isinstance(output, str) or not output.strip():
            raise PostSessionBlocked(f"La etapa {stage.value} no produjo una salida válida.")
        results.append(StageResult(stage=stage, status="completed", output=output))

    return PostSessionResult(
        execution_id=request.execution_id,
        transcript_sha256=sha256(request.transcript.encode("utf-8")).hexdigest(),
        status="awaiting_human_review",
        stages=tuple(results),
        human_review_required=True,
    )
