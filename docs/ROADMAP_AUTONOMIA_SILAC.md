# Hoja de ruta maestra de autonomía — XIL-AC / SILAC

**Auditoría:** 2026-10-11  
**Estado:** plan de ejecución versionado; no constituye certificación de producción.  
**Rama de trabajo:** `audit/roadmap-autonomia-2026-10-11`  
**Regla de seguridad:** `POST /v1/process` y el procesamiento de sesiones reales CFE permanecen deshabilitados hasta aprobación humana explícita y cierre documentado de los controles aplicables.

## 1. Resumen ejecutivo de la auditoría

### Evidencias observadas

- El repositorio tiene una base Python/FastAPI, controles de roles, registro de auditoría sin transcripciones, detector heurístico de posibles datos sensibles, límite del cuerpo HTTP, migraciones y pruebas.
- El commit `6c26e40b605753f9d511ad7dd24ac210b0dde7df` en `feat/production-readiness-rate-limits` tiene ejecuciones satisfactorias de CI y de pruebas de navegador:
  - CI: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38103043488
  - Navegador: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38103043479
- Las PR #13, #14 y #15 están abiertas y en borrador. La #14 tiene como base la rama de la #13; la #15 tiene como base la rama de la #14. No se consideran integradas en `main`.
- Las ramas inspeccionadas informan `protected: false`, incluida `main`. Debe activarse protección mediante la configuración disponible en GitHub; el intento de consultar rulesets no estuvo disponible por restricciones del plan/permisos.
- CodeQL, según el archivo observado en `main`, se ejecuta en `main` y en solicitudes dirigidas a `main`; no cubre automáticamente todas las ramas de desarrollo.
- La búsqueda Brave es un adaptador inicial de recuperación de resultados, no un motor completo de investigación. Requiere secreto externo y una prueba de extremo a extremo; aún faltan extracción de evidencia, contraste, síntesis citada y evaluación.
- El límite compartido por PostgreSQL y la limpieza por lotes están en la rama de desarrollo de la PR #15. Faltan evidencias de concurrencia real, programación/monitorización de la limpieza y límites de gasto del proveedor.
- La autenticación OIDC/JWT está implementada como ruta técnica, pero requiere pruebas con un proveedor real, claims de roles y casos negativos.
- No hay evidencia de despliegue productivo verificado, restauración probada, observabilidad operativa ni piloto real aprobado.
- El detector de privacidad es heurístico y no ofrece garantía de detección total. El control del servidor ocurre después de que la solicitud ya llegó a la API; no sustituye una revisión local previa al envío.

### Dictamen

**NO APTO PARA PRODUCCIÓN REAL.** Se puede continuar el desarrollo en ramas y con datos sintéticos. No introducir datos identificables de consultantes en la API remota, el proveedor de búsqueda, pruebas en la nube o registros. No habilitar el motor CFE real sin una revisión y autorización específica.

## 2. Las 6 etapas originales y sus 30 pasos

Cada paso debe pasar por: **auditoría → diseño → implementación → pruebas → criterio de aceptación → evidencia → decisión humana de avanzar, corregir o bloquear**.

### Etapa I — Base, seguridad y control

1. Inventariar módulos, capacidades reales, duplicaciones, dependencias y deuda técnica.
2. Consolidar ramas y solicitudes de integración; definir una secuencia sin dependencias circulares ni duplicaciones.
3. Proteger `main`, exigir verificaciones pertinentes y ampliar análisis de seguridad a ramas/PR activas.
4. Validar OIDC/JWT real, roles mínimos y pruebas negativas de autorización.
5. Cerrar controles operativos: secretos, cuotas/gasto, límites compartidos, limpieza, observabilidad, respaldo y recuperación.

**Salida de etapa:** flujo de integración seguro, permisos probados y lista P0 con evidencias.

### Etapa II — Motor de investigación real

6. Definir un contrato común de proveedor y adaptadores intercambiables.
7. Implementar recuperación controlada, límites de tamaño/tiempo, protección SSRF y lista de protocolos permitidos.
8. Diseñar un registro de evidencias con URL, fecha, tipo de fuente, fragmento/localizador y procedencia.
9. Contrastar fuentes independientes, contradicciones, vacíos, sesgos y evidencia contraria.
10. Generar síntesis con citas por afirmación, incertidumbre explícita y abstención ante evidencia insuficiente.

**Salida de etapa:** investigación reproducible y trazable, evaluada con un corpus de referencia.

### Etapa III — Autonomía de tareas

11. Crear un planificador que descomponga objetivos en subtareas verificables.
12. Orquestar herramientas con permisos mínimos, límites de tiempo y presupuesto.
13. Persistir estado, checkpoints, reintentos limitados y recuperación tras fallos.
14. Validar resultados mediante pruebas, reglas y verificadores independientes.
15. Definir niveles de autonomía y puertas de aprobación humana según riesgo.

**Salida de etapa:** tareas acotadas que se completan, verifican y recuperan sin afirmar éxito no comprobado.

### Etapa IV — Memoria y mejora controlada

16. Crear memoria técnica con procedencia, vigencia, permisos y recuperación verificable.
17. Implementar enrutamiento de modelos por tarea, calidad, privacidad, latencia y coste.
18. Mantener una batería de evaluación de regresión, seguridad, citas, calidad y coste.
19. Establecer un ciclo de mejora controlada con propuesta, evaluación, revisión y aprobación.
20. Versionar conocimiento/configuración y permitir reversión reproducible.

**Salida de etapa:** mejoras medibles sin aprendizaje silencioso ni cambios no auditados.

### Etapa V — Plataforma universal y capacidades CFE

21. Construir interfaz universal de investigación/tareas con estados, evidencias, errores y controles claros.
22. Aislar proyectos, usuarios, permisos, datos y memoria.
23. Añadir audio, voz y transcripción solo con consentimiento, minimización y política de retención.
24. Crear informes y exportaciones con procedencia, control de acceso y redacción de datos sensibles.
25. Integrar módulos especializados CFE (movimiento fenomenológico, UCDM en lenguaje existencial, Análisis Transaccional y Eneagrama) como herramientas asistidas, con hipótesis diferenciadas de hechos y validación humana.

**Salida de etapa:** experiencia integrada, con privacidad, trazabilidad y control humano.

### Etapa VI — Validación y operación

26. Crear un benchmark de autonomía con tareas representativas y criterios de éxito predefinidos.
27. Ejecutar pruebas de seguridad, aislamiento, privacidad, abuso y concurrencia.
28. Medir coste, latencia, disponibilidad, precisión, errores y recuperación.
29. Realizar un piloto privado, limitado y reversible con datos sintéticos o expresamente autorizados.
30. Aprobar por separado cada nivel de autonomía y cada alcance operativo.

**Salida de etapa:** decisión documentada por nivel; nunca una declaración general de “autonomía total” sin métricas.

## 3. Próximos 20 pasos de ejecución

Ordenados por dependencia. Un paso no se marca como completado hasta que exista evidencia verificable.

| N.º | Acción | Criterio de cierre |
|---:|---|---|
| 1 | Congelar una fotografía de estado: ramas, PR, commits, flujos y estructura | Inventario con fecha y SHA, reproducible |
| 2 | Comparar PR #11–#15 y ramas relacionadas para solapamientos y dependencias | Matriz de archivos/cambios, dependencias y riesgos |
| 3 | Revisar pruebas y resultados por SHA exacto en cada PR candidata | Registro de CI, navegador y análisis de seguridad por SHA |
| 4 | Definir la secuencia de integración y actualizar bases de las PR solo después de revisión | Grafo sin cadenas innecesarias; cada PR apunta a la base prevista |
| 5 | Activar protección de `main` desde la configuración disponible en GitHub | Reglas visibles; impedir integración sin verificaciones requeridas cuando el plan lo permita |
| 6 | Ampliar CI/CodeQL a ramas y PR de desarrollo relevantes | Flujos disparan donde corresponde; pruebas de configuración |
| 7 | Revisar permisos de acciones, dependencias y actualizaciones abiertas de Dependabot | Permisos mínimos, cambios revisados y pruebas verdes |
| 8 | Validar contrato de autenticación y autorización con casos negativos | Tests para token ausente/inválido/expirado, issuer/audience incorrectos, rol ausente/no autorizado |
| 9 | Ejecutar prueba OIDC contra un proveedor real en entorno privado | Evidencia redactada, sin publicar tokens; fallo cerrado verificado |
| 10 | Probar límite compartido PostgreSQL con concurrencia y varias instancias simuladas | 429/Retry-After, cambio de ventana, aislamiento de sujetos y fallo cerrado probados |
| 11 | Completar límites de coste/cuota para el proveedor de búsqueda | Exceso de cuota bloqueado, alertas y presupuesto comprobados |
| 12 | Programar y monitorizar limpieza de buckets; verificar retención | Ejecución periódica observable, lotes, fallos y retención probados |
| 13 | Completar revisión de seguridad web según el despliegue elegido | CORS, CSP, CSRF/cookies, TLS y cabeceras justificadas y probadas |
| 14 | Ejecutar extremo a extremo de la búsqueda con secreto válido y consulta sintética | Resultados reales, errores/timeouts y auditoría sin consulta verificados |
| 15 | Definir contrato común para proveedores de búsqueda | Pruebas de contrato y comportamiento común; Brave desacoplado |
| 16 | Implementar recuperación segura de páginas autorizadas | Protección SSRF, límites, MIME/tamaño, redirecciones y contenido malicioso probados |
| 17 | Crear estructura de evidencia y extracción de afirmaciones | Cada afirmación enlaza fragmento/localizador y fuente; trazabilidad conservada |
| 18 | Construir contraste de fuentes y detección de contradicciones | Corpus de prueba con convergencias, contradicciones y vacíos evaluados |
| 19 | Implementar síntesis con citas, incertidumbre y abstención | Métricas de fidelidad de citas y respuestas sin evidencia; no inventar referencias |
| 20 | Crear benchmark de calidad/coste/latencia y puerta de aceptación para investigación | Umbrales predefinidos, informe reproducible y decisión de avance documentada |

### Dependencias críticas

- Los pasos 1–4 preceden a la consolidación de PR.
- Los pasos 5–13 son controles previos a exponer el servicio a usuarios.
- Los pasos 14–19 construyen el motor de investigación, no solo una interfaz de búsqueda.
- El paso 20 permite decidir si el motor es suficientemente fiable para una beta privada.
- El procesamiento de sesiones CFE queda fuera de esta autorización de desarrollo general y sigue cerrado hasta una aprobación específica.

## 4. Niveles de autonomía propuestos

| Nivel | Capacidad | Control requerido |
|---|---|---|
| A1 — Asistente | Responde y explica; no ejecuta acciones externas | Revisión del usuario |
| A2 — Investigador | Busca, compara y sintetiza con evidencia | Citas, incertidumbre y revisión |
| A3 — Ejecutor acotado | Ejecuta tareas técnicas aprobadas y pruebas | Alcance, presupuesto, permisos y validación |
| A4 — Adaptativo supervisado | Propone mejoras basadas en métricas y evaluaciones | Aprobación para cambios persistentes y reversión |
| A5 — Operación supervisada | Mantiene tareas operativas dentro de límites explícitos | Monitorización, límites, alertas, rollback y autorización humana |

Estos niveles son una propuesta de arquitectura; no son certificaciones actuales de XIL-AC.

## 5. Registro de ejecución

- [x] Auditoría inicial del repositorio, PR, ramas, CI, CodeQL, API, autenticación y puerta de producción.
- [x] Verificación de CI y pruebas de navegador satisfactorias en el commit `6c26e40b605753f9d511ad7dd24ac210b0dde7df`.
- [x] Identificación de bloqueos: ramas sin protección, PR encadenadas sin integrar, OIDC real por verificar, cuotas, observabilidad, recuperación y motor de investigación incompleto.
- [x] Creación de esta hoja de ruta en una rama de auditoría.
- [ ] Revisión y CI de esta hoja de ruta.
- [ ] Integración controlada de la secuencia PR #13–#15.
- [ ] Cierre de los pasos 1–13.
- [ ] Cierre de los pasos 14–20 y evaluación de salida de etapa.
- [ ] Continuar etapas III–VI según las puertas de aceptación anteriores.

## 6. Regla de reporte

Todo informe futuro debe distinguir claramente:
1. **Propuesto**: diseño o decisión pendiente.
2. **Implementado**: código/documentación presentes en una rama.
3. **Probado**: evidencia de ejecución asociada al SHA.
4. **Integrado**: cambio incorporado a la rama objetivo.
5. **Operativo**: servicio ejecutándose y verificado en su entorno real.
6. **Aprobado**: persona responsable acepta el alcance y riesgo documentados.

Nunca usar “completado”, “autónomo” o “producción” como sinónimos entre estos estados.
