# Puerta de autonomía — XIL-AC

## Alcance del prototipo

`core/autonomy.py` implementa una decisión determinista previa a la ejecución: lista permitida de acciones, permisos mínimos, nivel de riesgo conocido y aprobación humana explícita para acciones de alto riesgo o con efectos externos.

## Estados

- `denied`: acción desconocida, política inválida, riesgo desconocido o permiso ausente.
- `awaiting_approval`: la acción está permitida por catálogo y permisos, pero requiere aprobación humana.
- `authorized`: supera las verificaciones de política; no significa que la acción ya se haya ejecutado.

Cada evaluación produce un `execution_id`. El módulo no registra por sí mismo la decisión en PostgreSQL y no ejecuta la acción; la integración con TRACE, auditoría persistente, cancelación, presupuesto, reintentos y recuperación es trabajo posterior.

## Límites

- No es un motor autónomo completo ni un planificador de tareas.
- No hay conexión a proveedores ni ejecución de comandos.
- La aprobación se representa como un booleano de entrada para pruebas; una interfaz real debe autenticar quién aprobó, qué alcance autorizó, cuándo y para qué ejecución.
- Los permisos deben proceder de una identidad validada, nunca de texto generado por un modelo.
- Mantener el procesamiento de sesiones CFE bloqueado.
