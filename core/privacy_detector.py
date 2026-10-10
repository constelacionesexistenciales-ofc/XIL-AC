"""Detector heurístico local de posibles datos sensibles; no garantiza detección completa."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PrivacyFinding:
    """Resultado sin valores detectados para no reproducir datos personales."""

    risk: str
    categories: tuple[str, ...]
    should_warn: bool


# Las reglas detectan señales explícitas; no identifican personas ni diagnostican.
_RULES: tuple[tuple[str, str, str], ...] = (
    (
        "email",
        "identificador_directo",
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    ),
    (
        "telefono_formateado",
        "identificador_directo",
        r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]\d{3,4}[\s.-]?\d{3,4}(?!\w)",
    ),
    (
        "documento_explicito",
        "identificador_directo",
        r"\b(?:DNI|CUIL|CUIT|documento|pasaporte)\s*"
        r"(?:n(?:ro|úm(?:ero)?)?\.?\s*)?[:#-]?\s*[A-Z0-9.-]{6,}\b",
    ),
    (
        "nombre_etiquetado",
        "identificador_directo",
        r"\b(?:nombre completo|nombre y apellido|nombre del consultante|"
        r"consultante|paciente)\s*[:=]\s*[^\n,;]{2,80}",
    ),
    (
        "domicilio_etiquetado",
        "ubicacion_personal",
        r"\b(?:domicilio|direcci[oó]n|vive en|reside en)\s*[:=]?\s*[^\n,;]{5,100}",
    ),
    (
        "fecha_personal_etiquetada",
        "dato_personal",
        r"\b(?:fecha de nacimiento|naci[oó] el|nacimiento)\s*[:=]?\s*"
        r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}",
    ),
    (
        "dato_clinico",
        "informacion_de_salud",
        r"\b(?:diagn[oó]stico|medicaci[oó]n|medicamento|psiquiatra|psic[oó]logo|"
        r"historia cl[ií]nica|internaci[oó]n|tratamiento psicol[oó]gico|salud mental)\b",
    ),
    (
        "violencia_o_abuso",
        "informacion_de_alta_sensibilidad",
        r"\b(?:abuso sexual|violencia sexual|violencia dom[eé]stica|"
        r"maltrato infantil|agresi[oó]n sexual|trata de personas)\b",
    ),
    (
        "riesgo_autolesivo",
        "informacion_de_alta_sensibilidad",
        r"\b(?:suicidio|suicida|autolesi[oó]n|hacerme da[nñ]o|quitarme la vida)\b",
    ),
    (
        "sexualidad_o_intimidad",
        "informacion_intima",
        r"\b(?:orientaci[oó]n sexual|vida sexual|relaci[oó]n sexual|"
        r"aborto|embarazo no deseado)\b",
    ),
    (
        "adicciones",
        "informacion_de_salud",
        r"\b(?:adicci[oó]n|consumo problem[aá]tico|dependencia de sustancias|"
        r"rehabilitaci[oó]n)\b",
    ),
)

_COMPILED_RULES = tuple(
    (name, category, re.compile(pattern, re.IGNORECASE))
    for name, category, pattern in _RULES
)


def detect_sensitive_content(text: str) -> PrivacyFinding:
    """Detecta señales explícitas y devuelve categorías, nunca el texto coincidente.

    Puede generar falsos positivos y no detecta de forma fiable nombres sin etiqueta,
    identificadores indirectos, contexto implícito ni paráfrasis.
    """
    if not isinstance(text, str) or not text.strip():
        return PrivacyFinding(
            risk="unknown",
            categories=("contenido_no_verificable",),
            should_warn=True,
        )

    matched_categories: set[str] = set()
    matched_rules: set[str] = set()
    for rule_name, category, pattern in _COMPILED_RULES:
        if pattern.search(text):
            matched_categories.add(category)
            matched_rules.add(rule_name)

    if not matched_rules:
        return PrivacyFinding(
            risk="no_signal_detected",
            categories=(),
            should_warn=False,
        )

    if "informacion_de_alta_sensibilidad" in matched_categories:
        risk = "high"
    elif "identificador_directo" in matched_categories and matched_categories.intersection(
        {"informacion_de_salud", "informacion_intima", "ubicacion_personal"}
    ):
        risk = "high"
    elif "identificador_directo" in matched_categories:
        risk = "medium"
    else:
        risk = "medium"

    return PrivacyFinding(
        risk=risk,
        categories=tuple(sorted(matched_categories)),
        should_warn=True,
    )
