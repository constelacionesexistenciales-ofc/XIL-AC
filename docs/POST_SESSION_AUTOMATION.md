# Automatización de cierre post-sesión

Estado: **orquestador inicial en rama de propuesta; integración con el motor CFE no realizada**.

## Secuencia obligatoria

1. Devolución de la última lectura del asistente.
2. Análisis fenomenológico de la sesión completa.
3. Informe interno para el facilitador.
4. Informe para enviar al consultante en lenguaje cotidiano y fiel al facilitador.
5. Auditoría del proceso de facilitación.
6. Auditoría de funcionalidad operativa del asistente.
7. Resultados de testing y propuestas de mejora.

El flujo termina en revisión humana. No envía el informe al consultante de forma automática.

## Controles

- Exige confirmación explícita del fin de sesión y transcripción disponible.
- Rechaza handlers incompletos y salidas vacías.
- Ejecuta etapas en orden determinista; ante error, detiene el flujo sin propagar mensajes que puedan contener transcripción.
- Devuelve `execution_id` y huella SHA-256; no incluye transcripción en el resultado.
- Las sesiones reales permanecen bloqueadas cuando el procesamiento está deshabilitado.
- Las pruebas usan datos sintéticos.
- El módulo no activa `CFE_SESSION_PROCESSING_ENABLED` ni modifica la Puerta de Producción.

## Integración pendiente

El integrador debe conectar un evento de cierre fiable, cargar el contexto autorizado, implementar cada handler con el motor correspondiente, persistir idempotencia y estados en almacenamiento compartido, emitir TRACE/auditoría sin contenido sensible y agregar pruebas de integración con PostgreSQL. Debe probarse con datos sintéticos y CI verde antes de solicitar revisión.

## Criterio de aceptación

- Todas las etapas se ejecutan en el orden definido.
- Cualquier precondición faltante, componente ausente o error bloquea el flujo.
- Ningún informe se envía sin aprobación humana.
- Ninguna sesión real se procesa por esta integración mientras la puerta siga cerrada.
- CI y revisión humana deben aprobar el cambio antes de fusionarlo.
