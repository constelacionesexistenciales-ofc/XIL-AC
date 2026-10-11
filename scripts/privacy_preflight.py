"""Inspección local preventiva antes de copiar contenido a una API remota.

Lee texto por entrada estándar, no realiza conexiones de red y nunca imprime el texto
recibido ni los fragmentos que hayan coincidido con reglas.
"""
from __future__ import annotations

import json
import sys

from core.privacy_detector import detect_sensitive_content


def main() -> int:
    text = sys.stdin.read()
    finding = detect_sensitive_content(text)
    if finding.should_warn:
        result = {
            "status": "blocked",
            "risk": finding.risk,
            "categories": list(finding.categories),
            "notice": (
                "No enviar este contenido a una API remota. La detección es heurística "
                "y no garantiza identificar todos los datos sensibles."
            ),
        }
        exit_code = 2
    else:
        result = {
            "status": "no_signal_detected",
            "risk": finding.risk,
            "categories": [],
            "notice": (
                "No se detectaron señales explícitas. Esto no garantiza que el texto "
                "esté libre de datos sensibles."
            ),
        }
        exit_code = 0
    print(json.dumps(result, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
