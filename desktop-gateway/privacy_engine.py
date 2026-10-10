"""Motor local heurístico. No realiza operaciones de red ni devuelve fragmentos detectados."""
from __future__ import annotations

import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Review:
    decision: str
    risk: str
    categories: tuple[str, ...]
    message: str

_RULES: tuple[tuple[str, str, str], ...] = (
    ("correo electrónico", "identificador directo", r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    ("teléfono con formato", "identificador directo", r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]\d{3,4}[\s.-]?\d{3,4}(?!\w)"),
    ("documento etiquetado", "identificador directo", r"\b(?:DNI|CUIL|CUIT|documento|pasaporte)\s*(?:n(?:ro|úm(?:ero)?)?\.?\s*)?[:#-]?\s*[A-Z0-9.-]{6,}\b"),
    ("nombre etiquetado", "identificador directo", r"\b(?:nombre completo|nombre y apellido|nombre del consultante|consultante|paciente)\s*[:=]\s*[^\n,;]{2,80}"),
    ("domicilio etiquetado", "ubicación personal", r"\b(?:domicilio|direcci[oó]n|vive en|reside en)\s*[:=]?\s*[^\n,;]{5,100}"),
    ("fecha de nacimiento", "dato personal", r"\b(?:fecha de nacimiento|naci[oó] el|nacimiento)\s*[:=]?\s*\d{1,4}[/-]\d{1,2}[/-]\d{1,4}"),
    ("información de salud", "información de salud", r"\b(?:diagn[oó]stico|medicaci[oó]n|medicamento|psiquiatra|psic[oó]logo|historia cl[ií]nica|internaci[oó]n|tratamiento psicol[oó]gico|salud mental)\b"),
    ("violencia o abuso", "alta sensibilidad", r"\b(?:abuso sexual|violencia sexual|violencia dom[eé]stica|maltrato infantil|agresi[oó]n sexual|trata de personas)\b"),
    ("riesgo autolesivo", "alta sensibilidad", r"\b(?:suicidio|suicida|autolesi[oó]n|hacerme da[nñ]o|quitarme la vida)\b"),
    ("sexualidad o intimidad", "información íntima", r"\b(?:orientaci[oó]n sexual|vida sexual|relaci[oó]n sexual|aborto|embarazo no deseado)\b"),
    ("adicciones", "información de salud", r"\b(?:adicci[oó]n|consumo problem[aá]tico|dependencia de sustancias|rehabilitaci[oó]n)\b"),
)
_COMPILED = tuple((label, category, re.compile(pattern, re.IGNORECASE)) for label, category, pattern in _RULES)

def review_text(text: str) -> Review:
    """Clasifica sin conservar ni devolver los valores encontrados.

    El resultado negativo no certifica anonimización. Ninguna revisión permite
    transmitir contenido: la política inicial es siempre sin transmisión.
    """
    if not isinstance(text, str) or not text.strip():
        return Review("REVIEW_REQUIRED", "unknown", ("empty_or_unverifiable",),
                      "No hay contenido suficiente para revisar. No se habilita ninguna operación remota.")
    findings = [(label, category) for label, category, pattern in _COMPILED if pattern.search(text)]
    categories = tuple(sorted({category for _, category in findings}))
    if "alta sensibilidad" in categories:
        risk = "high"
        decision = "DENY"
        message = "Señales de alta sensibilidad. No compartir ni enviar este contenido."
    elif findings:
        risk = "medium"
        decision = "REVIEW_REQUIRED"
        message = "Se detectaron posibles datos sensibles. Revisá y minimizá manualmente; no se permite envío remoto."
    else:
        risk = "no_signal_detected"
        decision = "REVIEW_REQUIRED"
        message = "No se detectaron señales explícitas. Esto no prueba que el texto sea anónimo o seguro; la transmisión sigue bloqueada."
    return Review(decision, risk, tuple(label for label, _ in findings),
                  message)
