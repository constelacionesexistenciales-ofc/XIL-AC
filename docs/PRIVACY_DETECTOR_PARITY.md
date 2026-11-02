# Paridad de detectores de privacidad — contrato inicial

**Estado:** implementación candidata; no es una autorización de transmisión ni una puerta universal de salida.  
**Fecha:** 2026-11-02.  
**Relacionado:** issue #81.

## Contrato de riesgo

Los detectores locales comparten un corpus sintético versionado en
`tests/fixtures/privacy_parity_cases.json`.

- `unknown`: entrada vacía o no verificable.
- `no_signal_detected`: ninguna regla explícita coincidió; no equivale a anonimización.
- `medium`: existe al menos una señal explícita sin combinación de riesgo elevado.
- `high`: aparece una señal de alta sensibilidad, o coexisten un identificador directo y un contexto sensible de salud, intimidad o ubicación.

Toda salida continúa bloqueada para transmisión. El detector central expone `should_warn`;
Windows devuelve `DENY` ante riesgo alto y `REVIEW_REQUIRED` en los demás estados;
HTML presenta una clasificación visual. Ninguno autoriza envío.

## Cobertura ejecutable candidata

`tests/test_privacy_parity_contract.py` ejecuta el mismo corpus contra:

1. `core.privacy_detector.detect_sensitive_content` (API/CLI).
2. `desktop-gateway/privacy_engine.py` (Windows).
3. El JavaScript real de `local-privacy-review/index.html`, aislado en un DOM mínimo de prueba mediante Node.js.

También verifica que la página conserve `connect-src 'none'` y no use APIs de red o almacenamiento persistente.

## Hallazgo corregido en esta candidata

Antes, el detector central clasificaba como `high` la coexistencia de un identificador directo con información de salud, intimidad o ubicación. Windows y HTML solo elevaban a `high` ante términos de alta sensibilidad. Esto podía producir una clasificación inferior para el mismo texto.

La candidata alinea Windows y HTML con la regla combinada y añade regresiones sintéticas para correo + salud, nombre + intimidad y nombre + ubicación.

## Límites que permanecen

- Las reglas siguen siendo heurísticas y pueden producir falsos positivos y falsos negativos.
- El corpus no demuestra detección de identidades indirectas, contexto implícito, paráfrasis ni todos los dialectos.
- Las etiquetas visibles de Windows/HTML y las categorías semánticas de Python siguen siendo representaciones distintas; el contrato de riesgo queda alineado, no toda la taxonomía.
- La prueba HTML usa el JavaScript real con un DOM mínimo; no sustituye pruebas manuales en navegador/dispositivo.
- La paridad de API/CLI/Windows/HTML no intercepta tráfico de otros procesos ni sustituye una compuerta de salida integrada.
- No se ejecutó ni autorizó una sesión real. Production Gate permanece NO-GO.

## Criterio para ampliar y cerrar issue #81

1. Añadir corpus de Unicode, normalización, formatos de teléfono/documento, falsos positivos y entradas adversariales.
2. Acordar taxonomía pública única de categorías, además del nivel de riesgo.
3. Ejecutar las mismas fixtures en instalación real de Windows y navegadores soportados.
4. Medir falsos positivos/falsos negativos con datos sintéticos y revisión humana.
5. Integrar la revisión local como requisito previo de salida en cada cliente, con fallo cerrado.
6. Demostrar que ningún resultado heurístico negativo autoriza transmisión.
