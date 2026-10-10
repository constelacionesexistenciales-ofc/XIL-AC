"""Comprobación local previa al envío; nunca transmite ni imprime el texto analizado."""
from __future__ import annotations

import json
import sys

from core.privacy_detector import detect_sensitive_content


def main() -> int:
    if sys.stdin.isatty():
        print(json.dumps({"status": "input_required", "notice": "Pasá el texto por entrada estándar; no lo incluyas como argumento."}, ensure_ascii=False))
        return 64

    finding = detect_sensitive_content(sys.stdin.read())
    if finding.should_warn:
        result = {
            "status": "blocked",
            "risk": finding.risk,
            "categories": list(finding.categories),
            "notice": "No transmitas este contenido. La comprobación es heurística y no sustituye la revisión humana.",
        }
        exit_code = 2
    else:
        result = {
            "status": "no_signal_detected",
            "risk": finding.risk,
            "categories": [],
            "notice": "No se detectaron señales explícitas. Esto no garantiza que el texto esté libre de datos sensibles.",
        }
        exit_code = 0

    print(json.dumps(result, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
