# Plan de pruebas — cierre post-sesión

## Unitarias incluidas

- Orden exacto de las siete etapas.
- Bloqueo cuando no se confirma el fin de sesión.
- Bloqueo de sesiones reales con procesamiento deshabilitado.
- Bloqueo previo a ejecutar etapas si faltan componentes.
- Bloqueo ante salida vacía o error de handler.
- Revisión humana obligatoria al finalizar.
- Huella de transcripción en lugar de copiar su contenido a la respuesta.

## Pendientes de integración / entorno

- Evento real de cierre frente a pausas, desconexiones y sesiones reanudadas.
- Idempotencia distribuida entre procesos y reinicios.
- Persistencia de estados y recuperación tras fallos.
- Integración TRACE y auditoría con base de datos.
- Autorización y aislamiento entre facilitadores.
- Flujo completo con adaptadores reales y datos sintéticos.
- Verificación de que no se envían transcripciones a proveedores externos.
- CI, análisis estático, seguridad y revisión de privacidad.
