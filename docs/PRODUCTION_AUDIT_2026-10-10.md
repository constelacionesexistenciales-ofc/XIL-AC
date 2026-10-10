# Auditoría de preparación para producción — 2026-10-10

## Veredicto
NO APTO PARA PRODUCCIÓN REAL. Apto para continuar el endurecimiento y validar una preproducción con datos sintéticos.

## Hallazgos prioritarios
- P0: el motor CFE no está conectado; el endpoint de procesamiento no ejecuta el método real.
- P0: el detector de privacidad corre en el servidor después de recibir el cuerpo; no evita la transmisión inicial.
- P0: no se verificó un despliegue cloud real ni un proveedor OIDC real.
- P1: retención, borrado, límites de uso, respaldo y restauración requieren implementación y pruebas.
- P1: CI, CodeQL y Dependabot existen en el repositorio, pero no se observaron estados de verificación asociados al último commit consultado. Confirmar CI en una solicitud de integración.
- P1: los planes gratuitos pueden pausarse o carecer de copias de seguridad administradas; no usarlos como archivo maestro.
- P2: el detector heurístico puede omitir identificadores indirectos y generar falsos positivos; medirlo con datos sintéticos.

## Decisión
Mantener el procesamiento de sesiones bloqueado y no enviar contenido real de consultantes a la API remota. No declarar producción hasta que cada control tenga evidencia reproducible y aprobación humana.

## Secuencia de cierre
1. Ejecutar CI y corregir fallos.
2. Verificar en CI la barrera de arranque añadida en esta rama y mantenerla cubierta por prueba de regresión.
3. Crear inspección local previa al envío y medir el detector con corpus sintético.
4. Configurar y probar OIDC, PostgreSQL y secretos en preproducción privada.
5. Probar autorización externa, límites, observabilidad, copias y restauración.
6. Integrar el motor CFE detrás de una puerta independiente y aprobación explícita.