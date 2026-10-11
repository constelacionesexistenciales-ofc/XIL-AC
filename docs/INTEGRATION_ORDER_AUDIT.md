# Auditoría de solapamientos y orden de integración — XIL-AC

**Fecha:** 2026-10-11  
**Rama de trabajo:** `audit/roadmap-autonomia-2026-10-11`  
**Estado:** auditoría de archivos y dependencias; no implica aprobación ni integración.

## 1. Inventario observado

| PR | Rama / base | Alcance | Riesgo principal |
|---|---|---|---|
| #11 | `feature/local-presend-privacy-review-v0.4.1` → `main` | Puerta local de privacidad de escritorio para Windows: cuenta local, almacenamiento protegido, revisión previa al envío, instalador y pruebas. | Cambios en README y puerta de producción; requiere pruebas de instalación y seguridad en Windows. |
| #12 | `audit/production-readiness-2026-10-10` → `main` | Auditoría de producción, configuración, API y bloqueo preventivo del procesamiento de sesiones. | Solapa API, configuración, pruebas y documentos con #13 y #15. |
| #13 | `feat/universal-research-experience` → `main` | Interfaz universal, adaptador Brave, endpoint de investigación, roles, privacidad y auditoría. | Solapa API, detector de privacidad, README y puerta de producción con #12/#15. Requiere secreto externo para prueba real. |
| #14 | `feat/owned-research-engine-evaluation` → base #13 | Evaluación documental de tecnologías y pruebas de navegador. | Depende de #13; no es un motor propio integrado ni una auditoría legal/benchmark completo. |
| #15 | `feat/production-readiness-rate-limits` → base #14 | Límite compartido PostgreSQL, migración, limpieza, pruebas y backlog operativo. | Depende de #13 y #14; solapa API, configuración, CI, Compose y documentación. |
| #16 | `audit/roadmap-autonomia-2026-10-11` → `main` | Hoja de ruta, ampliación de filtros CI, ajuste de CodeQL y regresión del aviso de privacidad. | Cambios pequeños en CI/CodeQL y una prueba de API; no integra funciones de producto. |

## 2. Mapa de solapamientos

- **README.md:** #11, #12, #13 y #15. Riesgo de perder instrucciones o sobrescribir documentación al resolver conflictos.
- **docs/PRODUCTION_GATE.md:** #11, #12, #13 y #15. Debe quedar una única lista de puertas y estados, con requisitos verificables.
- **core/api.py:** #12, #13 y #15. Es el solapamiento de mayor riesgo: bloqueo de sesiones, detector de privacidad, endpoint de investigación y limitación de solicitudes deben convivir sin debilitar el bloqueo por defecto.
- **core/config.py / .env.example / compose.yaml:** #13 y #15, y configuración también en #12. Consolidar nombres y valores predeterminados sin incluir secretos.
- **tests/test_api.py:** #12, #13, #15 y #16. Resolver en una sola secuencia y preservar pruebas negativas de autenticación, privacidad, límites y fallo cerrado.
- **CI:** #14/#15 modifican el flujo de pruebas de navegador y CI; #16 modifica filtros de ramas y añade escaneo Bandit. Revisar conjuntamente los disparadores para evitar pruebas omitidas o duplicadas.
- **Documentación de investigación:** #13 agrega el plan de investigación; #14 agrega evaluación tecnológica; #15 agrega backlog. Mantener diferencias claras entre plan, evaluación y capacidad realmente operativa.
- **Migraciones / límites:** #15 incorpora `0002_rate_limit_buckets.sql`; comprobar compatibilidad con el esquema actual y con despliegues nuevos/actualizados antes de integrar.
- **Privacidad local vs. API remota:** #11 ofrece una revisión previa local; #12/#13 mantienen controles de servidor. No son intercambiables: el control del servidor ocurre después del envío y no reemplaza la revisión local.

## 3. Orden de integración recomendado

No integrar las seis PR en bloque. La secuencia propuesta, condicionada a pruebas verdes y revisión de cada diff, es:

1. **#16 — Herramientas de calidad y hoja de ruta.** Primero corregir la aserción de mayúsculas/minúsculas del aviso, validar los flujos CI/CodeQL y ejecutar el nuevo análisis Bandit. CodeQL se omite para repositorios privados cuando la publicación de resultados no está disponible; Bandit aporta un control estático alternativo en CI. Esta omisión no equivale a un análisis CodeQL satisfactorio.
2. **#12 — Puerta de seguridad y preparación de producción.** Revisar API/configuración y mantener el procesamiento de sesiones cerrado por defecto. Resolver primero los conflictos conceptuales con #13/#15 antes de integrar.
3. **#11 — Puerta local de privacidad.** Integrar cuando pasen pruebas de Windows/instalador y revisión del almacenamiento protegido. Reconciliar README y puerta de producción con el resultado de #12.
4. **#13 — Investigación universal con búsqueda protegida.** Rebasar sobre la base actualizada, revisar de nuevo endpoint/API y controles de privacidad, ejecutar pruebas unitarias y prueba de extremo a extremo con consulta sintética y secreto configurado directamente en GitHub.
5. **#14 — Evaluación tecnológica y pruebas de navegador.** Mantenerla encima de #13; no presentarla como motor de investigación implementado.
6. **#15 — Límite compartido y preparación operativa.** Integrar sobre #14 solo tras pruebas de migración, concurrencia, 429/Retry-After, aislamiento de sujeto/alcance y fallo cerrado ante indisponibilidad de base de datos.

**Regla de rebase:** al integrar cada base, actualizar la siguiente rama dependiente y volver a ejecutar todas las pruebas sobre el nuevo SHA. No asumir que una prueba verde en una rama anterior valida el resultado rebajado.

## 4. Puertas mínimas antes de cada integración

- Diff revisado y conflictos resueltos sin descartar controles de seguridad.
- CI, Ruff, pruebas unitarias y de integración satisfactorios en el SHA exacto.
- Pruebas de navegador para cambios de interfaz.
- Pruebas negativas: falta de token, token inválido, rol insuficiente, entrada sensible, base de datos caída y proveedor externo fallido.
- Sin secretos, datos reales de consultantes ni transcripciones en código, fixtures, logs o consultas externas.
- Documentación coherente con lo que el código realmente hace.
- Aprobación humana antes de integrar en `main`; ninguna automatización de esta auditoría autoriza el despliegue ni la activación de sesiones CFE.

## 5. Hallazgos de ejecución que requieren seguimiento

- El CI de PR #16 falló en SHA `867945cbba5b3e7af62c1f9dd33b5e11a59b3a61`: 27 pruebas pasaron y una falló porque la prueba esperaba `No envíes`, mientras el aviso real usa `no envíes`. La prueba se corrigió para comparar sin distinguir mayúsculas/minúsculas.
- CodeQL falló al intentar publicar el análisis en este repositorio privado. El flujo se condicionó para omitir esa publicación si el repositorio es privado; CI incorpora Bandit como análisis estático alternativo. Hay que verificar el resultado del nuevo CI y del análisis Bandit en el SHA final.
- La corrección de la prueba no cambia el aviso ni habilita procesamiento: el gate permanece cerrado.
- Las PR #11–#16 continúan abiertas; esta auditoría no las fusiona.

## 6. Estado de esta etapa

- [x] Enumerar archivos modificados por PR #11–#16.
- [x] Identificar solapamientos críticos y dependencias entre #13 → #14 → #15.
- [x] Recomendar secuencia de integración y puertas de aceptación.
- [x] Corregir la aserción de aviso sensible a mayúsculas/minúsculas.
- [x] Añadir escaneo Bandit a CI y evitar que CodeQL publique en un repositorio privado no compatible.
- [ ] Confirmar CI y Bandit satisfactorios en el SHA final.
- [ ] Revisar cada PR, rebasar dependencias y comenzar integraciones controladas.

**Dictamen:** etapa 01 documentada; etapa 02 en curso. Ninguna PR se considera integrada y XIL-AC no está certificado para producción.
