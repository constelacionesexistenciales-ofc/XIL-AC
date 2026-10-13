# Indicador de movimiento de sesión

Interfaz de facilitación servida en /session-movement/. Usa la API autenticada de XIL-AC para registrar puntuaciones mínimas en llegada, durante y cierre, y recuperar el resumen posterior. No contiene campos para nombres, transcripciones ni notas libres.

## Estado de disponibilidad
El indicador está desactivado por defecto. Para prueba local autorizada, aplicar migrations/0003_session_movement_metrics.sql, configurar SESSION_MOVEMENT_ENABLED=true, DATABASE_URL y XILAC_API_TOKEN, e iniciar la API. No habilitar datos reales de consultantes ni exponer públicamente antes de completar la Puerta de Producción.

El token se mantiene en memoria de la página, no se guarda en almacenamiento persistente. El identificador de sesión debe copiarse si se necesita recuperar el resumen después de recargar.
