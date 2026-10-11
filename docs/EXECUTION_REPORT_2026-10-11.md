# Informe de ejecución técnica — 2026-10-11

## Estado ejecutivo

El repositorio `constelacionesexistenciales-ofc/XIL-AC` tiene la rama predeterminada `main`. La búsqueda web protegida, las pruebas de navegador y el límite compartido de solicitudes PostgreSQL aparecen integrados mediante las PR #20, #22 y #23.

La PR #13 se cerró como sustituida y no se fusionó directamente. No usar su rama antigua como fuente de verdad.

## Resultados comprobados en el repositorio

- La ruta `POST /v1/research` está presente en `core/api.py`.
- La búsqueda requiere token/rol autorizado, control de privacidad heurístico, límite compartido y registro de auditoría antes de llamar al proveedor.
- `core/evidence_registry.py` valida estructura y procedencia y permite abstenerse cuando la evidencia no alcanza.
- La interfaz universal llama a la API y diferencia resultados recuperados de una síntesis no generada.
- Compose pasa la variable `BRAVE_SEARCH_API_KEY` al contenedor sin incluir una clave real en Git.
- `CFE_SESSION_PROCESSING_ENABLED=false` permanece como valor predeterminado; no se declara conectado el motor CFE.
- En la ejecución CI #227 para el commit previo de esta rama, Compose, instalación, Bandit, Ruff y pytest finalizaron correctamente: **96 pruebas aprobadas, 1 advertencia de deprecación**. Esta evidencia corresponde a ese commit; los cambios posteriores deben volver a pasar CI.
- CodeQL fue omitido en la rama actual por la condición del flujo de trabajo para repositorios privados. Una ejecución anterior sí falló al intentar publicar resultados porque GitHub informó que el análisis de código no estaba habilitado. Esto no equivale a una alerta confirmada en el código ni a una revisión de seguridad aprobada.

## Cambios de endurecimiento propuestos en esta rama

- Validación de URL de fuentes HTTPS con límite de longitud, sin credenciales embebidas ni puertos no estándar.
- Rechazo de nombres locales y direcciones IP no públicas en enlaces de resultados.
- Validación estricta de destinos de redirección del proveedor.
- Pruebas adversariales para URL con credenciales, host local, IP privada, puerto no estándar, espacios y URL malformada.

Estos cambios se consideran **propuestos**, no aprobados ni integrados, hasta que la CI de la versión finalice y los cambios sean revisados.

## Cinco fases y estado real

### Fase 1 — Estabilización
Se revisaron los archivos de API, proveedor, registro de evidencia, limitación de solicitudes, Compose, pruebas y documentación. CI pasó en el commit previo de la rama; los cambios más recientes necesitan su propia ejecución verde. No se ejecutó una prueba local en esta sesión.

### Fase 2 — Búsqueda
La recuperación mediante Brave está implementada en el código. La prueba real de extremo a extremo queda pendiente de una clave válida en el entorno. Se añadió endurecimiento de URL en una rama propuesta.

### Fase 3 — Seguridad
Autenticación, roles, auditoría previa y límites compartidos aparecen implementados. La evaluación heurística de privacidad no es una garantía. CodeQL no está validado para esta rama: la ejecución actual se omite en repositorios privados y la ejecución anterior falló por configuración de code scanning. OIDC y secretos reales deben validarse en el entorno de destino.

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


## Addendum — avance de fases 3–5 (2026-10-11)

### Fase 3 — endurecimiento y QA
- Se endureció la validación de URL tanto en los resultados del proveedor como en el registro de evidencia: HTTPS obligatorio, sin credenciales incrustadas, puertos no estándar, hosts locales ni direcciones IP no públicas.
- Se añadieron pruebas adversariales para las URL y pruebas del preflight local de privacidad.
- Se incorporó el flujo `.github/workflows/dependency-audit.yml` con `pip-audit` en PR, push, ejecución manual y calendario semanal.
- CI #245 pasó en el commit `3ab5b2786afc79e608ef2b946f23ac744c11c867`: **112 pruebas aprobadas**, 1 advertencia de deprecación; Compose, Bandit y Ruff pasaron.
- Auditoría de dependencias #12: **aprobada**.
- CodeQL #187: **omitido** por la condición del flujo para repositorios privados. No se interpreta como análisis aprobado.

### Fase 4 — evaluación de procedencia (parcial)
- Se agregó `core/research_assessment.py` y el campo `source_assessment` en la respuesta de investigación.
- La evaluación informa recuento de fuentes, dominios únicos, diversidad, duplicados y metadatos faltantes.
- No calcula una puntuación ficticia de credibilidad y declara explícitamente que el contenido no fue verificado.
- El registro de evidencia ahora exige URL HTTPS públicas.
- Pendiente: recuperación segura del contenido de páginas, extracción limitada y con controles, evaluación del contenido, contraste semántico entre fuentes y síntesis con citas verificables. No declarar el motor autónomo completo.

### Fase 5 — producción (NO-GO)
- La auditoría de dependencias y las pruebas de CI no equivalen a una validación de producción.
- Continúan pendientes: E2E real con clave autorizada de Brave; disponibilidad de CodeQL; OIDC y secretos gestionados en entorno objetivo; límites de gasto; observabilidad; política y pruebas de retención/borrado; pruebas de carga, recuperación, restauración y despliegue real; revisión y aprobación humana.
- `CFE_SESSION_PROCESSING_ENABLED=false` sigue siendo el valor predeterminado. No habilitar sesiones reales.

### Enlaces de ejecución
- CI #245: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38156565941
- Auditoría de dependencias #12: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38156565918
- CodeQL omitido #187: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38156565889
- PR de trabajo: https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/28
