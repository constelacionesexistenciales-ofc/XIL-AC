# Auditoría de integración de funcionalidades en main — 2026-10-13

Rama auditada: main  
SHA del árbol consultado: 4256457dc35ca71965e7c7224b6a3f4cb8f7a5fc  
Rama de esta auditoría: audit/main-integration-matrix-2026-10-13  
Estado: auditoría estática basada en árbol, documentación y código consultados. No equivale a ejecución local ni certificación de producción.

## Dictamen

XIL-AC tiene una base Python/FastAPI con autenticación, límites de solicitud, trazabilidad, control de riesgo, auditoría, detección heurística de privacidad, persistencia/migraciones, búsqueda web inicial, enrutamiento de modelos y una puerta local de escritorio en prototipo. No es correcto declarar integradas todas las capacidades del producto: el README y los documentos de módulos identifican explícitamente funciones incompletas y bloqueos.

**No activar CFE_SESSION_PROCESSING_ENABLED ni transmitir datos reales de consultantes.** El motor CFE no está conectado de extremo a extremo; la inspección de privacidad de la API ocurre después de recibir la solicitud y no sustituye el filtro local previo a cualquier transmisión.

## 1. Inventario observado en main

### Núcleo y API
- core/api.py: aplicación FastAPI y rutas HTTP.
- core/config.py: configuración y validación de entorno.
- core/auth.py, core/middleware.py, core/rate_limit.py: autenticación/autorización, límites de cuerpo y limitación de solicitudes.
- core/trace.py, core/audit.py, core/risk_gate.py, core/autonomy.py: trazabilidad, auditoría técnica, decisión de riesgo y autorización acotada de acciones.
- core/db.py, scripts/migrate.py, migrations/: acceso y migraciones de persistencia.
- tests/: pruebas unitarias, de API, migraciones, investigación, límites, privacidad y navegador.

### Investigación y modelos
- core/research.py, core/research_eval.py, core/evidence_registry.py: búsqueda inicial, evaluación básica y registros de evidencia.
- core/model_router.py, core/provider_contracts.py, core/local_inference.py: enrutamiento y contratos de proveedores e inferencia local.
- El README indica que la búsqueda recupera resultados, pero aún no sintetiza ni contrasta afirmaciones. No describirla como motor autónomo completo.

### Sesión y escritorio
- core/post_session.py: orquestador post-sesión con handlers inyectados y precondiciones; no está conectado al motor CFE ni a un evento real de cierre.
- desktop-gateway/: prototipo local de Windows y motor de revisión preventiva; su README exige pruebas manuales de instalación, ejecución, desinstalación y seguridad.
- docs/LIVE_SESSION_ASSISTANT_SPEC.md y docs/LIVE_SESSION_ASSISTANT_QA.md: especificación y criterios de QA; no demuestran comportamiento de un motor en vivo conectado.
- docs/PRODUCTION_GATE_CHECKLIST.md: lista de control explícitamente no aprobada.

## 2. Matriz de integración

Estados:
- **Presente (código identificado):** el componente existe en main; no implica validación de extremo a extremo.
- **Parcial / requiere prueba:** existe un componente, pero su conexión o alcance es limitado.
- **No integrado / bloqueado:** la documentación declara que falta o el flujo completo no está demostrado.
- **No verificado:** no se afirma ausencia; falta evidencia suficiente en esta auditoría.

| Funcionalidad | Evidencia en main | Estado | Acción requerida |
|---|---|---|---|
| Aplicación/API principal | core/api.py | Presente | Verificar rutas y contratos desde cliente hasta salida. |
| Configuración estricta | core/config.py | Presente | Probar matriz por entorno y errores de configuración. |
| Identidad y roles | core/auth.py | Parcial | Probar proveedor OIDC/JWT real, audiencia, firma, expiración y matriz RBAC en entorno de prueba. |
| TRACE / execution_id | core/trace.py | Presente | Verificar propagación por cada etapa y correlación con auditoría. |
| Gate de riesgo | core/risk_gate.py, core/autonomy.py | Presente | Probar que todos los efectos externos pasan por un gate único y fallan de forma segura. |
| Auditoría técnica | core/audit.py | Parcial | Comprobar cobertura y ausencia de transcripciones, secretos y datos personales en logs. |
| Detección de contenido sensible en API | core/privacy_detector.py, core/api.py | Parcial | Mantener como barrera adicional; no es filtro previo a transmisión. |
| Filtro local obligatorio previo al envío | desktop-gateway/privacy_engine.py, scripts/privacy_preflight.py | Parcial | Conectar obligatoriamente en el cliente real; bloquear ante incertidumbre/error o detector no disponible. |
| PostgreSQL y migraciones | core/db.py, migrations/ | Parcial | Ejecutar migración limpia, upgrade, recuperación y permisos en entorno aislado. |
| Límite de peticiones | core/rate_limit.py | Presente | Probar distribución, concurrencia, almacenamiento no disponible y límites por identidad. |
| Investigación web inicial | core/research.py | Parcial | Probar proveedor real con secreto externo; límites, fallos y respuesta segura. |
| Síntesis con citas por afirmación | core/evidence_registry.py, core/research_eval.py | Parcial / no demostrada integralmente | Implementar y probar vínculo entre afirmación, fuente, fecha, contradicción e incertidumbre. |
| Enrutamiento multi-proveedor | core/model_router.py, core/provider_contracts.py | Parcial | Validar selección, timeout, fallback, límites de coste y contratos de salida. |
| Inferencia local | core/local_inference.py | Parcial | Ejecutar modelo real aislado y medir calidad en español, latencia, memoria y licencia. |
| Motor de sesión CFE | README y política operativa declaran que no está conectado | No integrado / bloqueado | Crear adaptador con datos sintéticos y contrato formal; no activar sesiones reales. |
| Asistencia en vivo y anticipación silenciosa | Especificación/QA documental | No demostrada en ejecución | Conectar motor y ejecutar evaluaciones de fidelidad, espera, no invención y priorización. |
| Análisis CFE/AT e hipótesis validadas | Requisitos documentados; integración completa no probada | No verificado / pendiente | Implementar flujo dato → patrón → hipótesis → validación y preservar contradicciones. |
| Informes post-sesión | core/post_session.py, docs/POST_SESSION_AUTOMATION.md | Parcial; motor desconectado | Conectar handlers con datos sintéticos, persistencia idempotente y revisión humana. |
| Informe al consultante | Etapa declarada en core/post_session.py | No integrado de extremo a extremo | Verificar lenguaje cotidiano, fidelidad, separación del informe interno y aprobación antes de compartir. |
| Puerta local Windows | desktop-gateway/ y flujo de compilación | Prototipo | Completar pruebas manuales de instalación, actualización, desinstalación y seguridad. |
| Interfaz universal de investigación | Rutas y pruebas de navegador identificadas | Parcial | Confirmar experiencia integrada y accesibilidad móvil/escritorio en entorno ejecutable. |
| Observabilidad, backups y restauración | Requisitos en documentos de producción | No verificado | Probar alertas sin contenido sensible, backup cifrado y restauración en entorno aislado. |
| Seguridad de cadena de suministro | Workflows CI/SAST/CodeQL/Dependabot | Parcial | Verificar resultados de la punta actual de la rama; revisar artefactos, SBOM y hallazgos HIGH/CRITICAL. |
| Pruebas de extremo a extremo | Suite existente, cobertura completa no demostrada | Parcial | Crear pruebas verticales desde solicitud sintética hasta resultado, TRACE y auditoría. |
| Puerta de producción | docs/PRODUCTION_GATE_CHECKLIST.md | NO APROBADA | Cerrar cada P0 con evidencia reproducible y aprobación humana explícita. |

## 3. Bloqueos prioritarios y orden de resolución

### P0 — Seguridad antes de cualquier procesamiento real
1. Verificar CI/SAST/escaneo de imagen en el SHA candidato actual y conservar informes completos.
2. Integrar el filtro local de privacidad antes de cualquier transmisión, con cierre seguro ante fallo.
3. Probar OIDC/JWT y RBAC contra un proveedor de prueba real; probar identidades y roles autorizados/no autorizados.
4. Ejecutar pruebas adversariales SSRF, IPv4/IPv6, redirecciones, DNS rebinding y límites de recursos.
5. Confirmar TLS, secretos, migraciones, permisos de base de datos, backups cifrados y restauración.
6. Garantizar que logs, artefactos y TRACE no incluyan transcripciones ni secretos.

### P1 — Contrato de integración y funciones principales
7. Documentar el grafo real de llamadas: ruta API → autenticación → privacidad → gate → servicio → persistencia → TRACE/auditoría → respuesta.
8. Definir contrato común de módulo: entrada, salida, errores, estado, riesgo, permisos, timeout y execution_id.
9. Implementar pruebas de integración con PostgreSQL y una prueba vertical sintética de cada ruta crítica.
10. Conectar el motor CFE detrás de una interfaz explícita, manteniendo la bandera de procesamiento desactivada.
11. Conectar el orquestador post-sesión a handlers sintéticos y luego a un adaptador aprobado; revisión humana obligatoria.
12. Convertir los criterios de asistencia en vivo en evaluaciones de comportamiento ejecutables, no solo pruebas documentales.

### P2 — Investigación y autonomía
13. Validar búsqueda con proveedor real y después implementar recuperación segura y citas por afirmación.
14. Probar contradicciones, incertidumbre y diversidad de fuentes sin inventar una puntuación de fiabilidad.
15. Ejecutar inferencia local y medir calidad/latencia/coste; revisar licencias de modelos.
16. Probar interfaz web y puerta local en equipos aislados, con pruebas móviles y de escritorio.
17. Ejecutar carga, fallos de proveedor, recuperación, rollback y revisión independiente.
18. Completar Production Gate solo después de adjuntar evidencia por requisito.

## 4. Pruebas de aceptación mínimas

- Una solicitud no autorizada se rechaza antes de ejecutar la operación.
- Un fallo del detector de privacidad, del almacenamiento de límites o de una dependencia crítica no permite continuar de forma insegura.
- Cada operación produce un execution_id correlacionable sin almacenar la transcripción en los logs.
- Las hipótesis permanecen diferenciadas de datos y patrones; las contradicciones no se eliminan automáticamente.
- Un informe al consultante no se comparte sin revisión y aprobación humana.
- Una caída del proveedor o la base de datos devuelve error seguro, sin filtrar secretos ni contenido sensible.
- El procesamiento de sesiones reales sigue deshabilitado durante toda esta fase.
- El candidato exacto que se pretende integrar/desplegar tiene CI y escaneos revisados y aprobados.

## 5. Límites de esta auditoría

Esta revisión confirma rutas y módulos en el árbol de main y contrasta código/documentación representativos. No ejecuta el repositorio, no certifica los resultados actuales de CI, no valida un proveedor externo ni prueba una instalación Windows. Cada afirmación de ejecución debe acreditarse con el enlace del workflow, SHA exacto, artefacto y resultado.

**Decisión actual: NO-GO para producción y para procesamiento de sesiones reales.** El siguiente trabajo debe comenzar por P0 y por el grafo de integración de la API, sin fusionar propuestas en borrador automáticamente.
