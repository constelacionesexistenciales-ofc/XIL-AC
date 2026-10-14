"""Inspección local preventiva antes de cualquier envío remoto.

Esta utilidad nunca autoriza una transmisión. Un resultado sin señales explícitas no
certifica anonimización ni seguridad, por lo que todos los resultados mantienen el
bloqueo. Lee stdin y no imprime el texto recibido ni los fragmentos detectados.
"""
from __future__ import annotations

import json
import sys

from core.privacy_detector import detect_sensitive_content


def main() -> int:
    text = sys.stdin.read()
    try:
        finding = detect_sensitive_content(text)
        if finding.should_warn:
            risk = finding.risk
            categories = list(finding.categories)
            notice = (
                "Se detectaron o podrían existir datos sensibles. No enviar este "
                "contenido a una API remota; revisá y minimizá manualmente."
            )
        else:
            risk = finding.risk
            categories = list(finding.categories)
            notice = (
                "No se detectaron señales explícitas. Esto no demuestra que el texto "
                "sea anónimo o seguro. La transmisión continúa bloqueada."
            )
    except Exception:
        # Ante cualquier error del detector, no dar una señal de autorización.
        result = {
            "status": "blocked",
            "risk": "unknown",
            "categories": ["privacy_check_failed"],
            "notice": (
                "No se pudo completar la revisión de privacidad. No enviar el contenido."
            ),
        }
        print(json.dumps(result, ensure_ascii=False))
        return 2

    result = {
        "status": "blocked",
        "risk": risk,
        "categories": categories,
        "notice": notice,
    }
    print(json.dumps(result, ensure_ascii=False))
    # Nunca usar código 0 como permiso de transmisión: esta herramienta solo inspecciona.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
