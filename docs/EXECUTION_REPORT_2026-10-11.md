# Informe de ejecución técnica — 2026-10-11

## Estado ejecutivo

El repositorio `constelacionesexistenciales-ofc/XIL-AC` tiene la rama predeterminada `main`. La búsqueda web protegida, las pruebas de navegador y el límite compartido de solicitudes PostgreSQL aparecen integrados mediante las PR #20, #22 y #23. Los commits de integración se identificaron en el historial de GitHub.

La PR #13 se cerró como sustituida y no se fusionó directamente. No usar su rama antigua como fuente de verdad.

## Resultados comprobados en el repositorio

- La ruta `POST /v1/research` está presente en `core/api.py`.
- La búsqueda requiere token/rol autorizado, control de privacidad heurístico, límite compartido y registro de auditoría antes de llamar al proveedor.
- `core/evidence_registry.py` valida estructura y procedencia y permite abstenerse cuando la evidencia no alcanza.
- La interfaz universal llama a la API y diferencia resultados recuperados de una síntesis no generada.
- Compose pasa la variable `BRAVE_SEARCH_API_KEY` al contenedor sin incluir una clave real en Git.
- `CFE_SESSION_PROCESSING_ENABLED=false` permanece como valor predeterminado; no se declara conectado el motor CFE.
- El historial reciente incluye commits que reportan CI satisfactoria para las integraciones anteriores; el estado del commit más reciente debe verificarse en la ejecución de CI correspondiente antes de afirmar que la rama actual pasó todas las pruebas.
- El CodeQL consultado para el commit anterior terminó con error de configuración al intentar publicar resultados porque el análisis de código no estaba habilitado para el repositorio privado. Esto no equivale a una alerta confirmada en el código, ni a una revisión de seguridad aprobada.

## Cambios de endurecimiento propuestos en esta rama

- Validación de URL de fuentes HTTPS con límite de longitud, sin credenciales embebidas ni puertos no estándar.
- Rechazo de nombres locales y direcciones IP no públicas en enlaces de resultados.
- Validación estricta de destinos de redirección del proveedor.
- Pruebas adversariales para URL con credenciales, host local, IP privada, puerto no estándar, espacios y URL malformada.

Estos cambios se consideran **propuestos**, no aprobados ni integrados, hasta que la CI de la rama finalice y los cambios sean revisados.

## Cinco fases y estado real

### Fase 1 — Estabilización
Se revisaron los archivos de API, proveedor, registro de evidencia, limitación de solicitudes, Compose, pruebas y documentación. La ejecución local completa no se realizó desde esta sesión; debe usarse CI para validar el cambio propuesto.

### Fase 2 — Búsqueda
La recuperación mediante Brave está implementada en el código. La prueba real de extremo a extremo queda pendiente de una clave válida en el entorno. Se añadió endurecimiento de URL en una rama propuesta.

### Fase 3 — Seguridad
Autenticación, roles, auditoría previa y límites compartidos aparecen implementados. La evaluación heurística de privacidad no es una garantía. CodeQL sigue bloqueado por configuración/función no habilitada; OIDC y secretos reales deben validarse en el entorno de destino.

### Fase 4 — Motor de investigación
El registro de evidencia está implementado, pero la recuperación sistemática de contenido, evaluación semántica, contraste entre afirmaciones y síntesis con citas no están completados. No describir el sistema como motor autónomo completo.

### Fase 5 — Producción
No completada. Faltan prueba E2E con proveedor real, configuración de identidad/secretos, observabilidad y retención, presupuesto de proveedor, recuperación/carga, despliegue real y aprobación de la puerta de producción.

## Intervenciones externas requeridas

1. Configurar `BRAVE_SEARCH_API_KEY` como secreto del entorno de ejecución.
2. Habilitar o confirmar la disponibilidad de CodeQL/code scanning en la configuración y plan del repositorio.
3. Proveer un entorno autorizado para verificar OIDC, secretos y despliegue cuando se alcance esa etapa.

Nunca compartir secretos por chat ni guardarlos en Git.

## Regla de publicación

No integrar ni desplegar automáticamente por el solo hecho de que se hayan creado commits. La rama debe tener CI verde, revisión de cambios y evidencia de pruebas aplicables. La decisión de publicación y la aprobación de producción siguen siendo humanas.
