# Informe técnico consolidado XIL-AC — actualización 2026-10-11

## Criterio de lectura

Este informe separa código integrado, CI, validación en entorno y autorización de uso. CI verde valida el commit probado; no demuestra despliegue productivo, calidad de investigación real ni autonomía integral. CodeQL figura omitido en estas ejecuciones por la configuración del repositorio privado; no debe presentarse como aprobado.

## Integraciones verificadas

| PR | Estado | Alcance integrado | Evidencia |
|---|---|---|---|
| #16 | Integrada | Auditoría maestra, corrección de regresión, filtros CI y Bandit | [CI #16](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38112692175) |
| #12 | Integrada | Puerta de preparación para producción; procesamiento CFE bloqueado | [CI #12](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38113158685) |
| #19 | Integrada | Prototipo local de privacidad Windows, autenticación local y página de revisión sin transmisión | [CI](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38143792470) · [Empaquetado Windows](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38143792482) · [CI main posterior](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38144221200) |
| #20 | Integrada | Endpoint de búsqueda autenticado, filtro de privacidad, auditoría previa, adaptador Brave, registro de evidencias, abstención explícita e interfaz | [CI de integración](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38144825234) · [CI main posterior](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38144929140) |
| #22 | Integrada | Evaluación tecnológica documental y pruebas de navegador Chromium | [CI](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145095662) · [Chromium](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145095578) · [CI main posterior](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145165234) |
| #23 | Integrada | Límite compartido PostgreSQL, migración, 429/503 fail-closed, limpieza y pruebas de concurrencia | [CI de integración](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145508597) · [CI main posterior](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145583477) |
| #24 | Integrada | Primer evaluador determinista de permisos, lista permitida, riesgo y Human Gate; no ejecuta acciones | [CI de integración](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145641082) · [CI main posterior en verificación](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145706232) |

## Resultado de los seis objetivos de trabajo

1. **Auditoría maestra:** cerrada en #16.
2. **Conflictos y dependencias:** resueltos por reconstrucción controlada de #11 → #19 y #13 → #20; #14 → #22 y #15 → #23 quedaron integradas en ese orden. Las PR originales #11 y #13 se cerraron como sustituidas, con explicación en sus cuerpos; no se fusionaron directamente. Sus implementaciones reconstruidas se integraron mediante #19 y #20.
3. **Integración y pruebas:** #19, #20, #22, #23 y #24 tienen CI de rama exitosa; las CI posteriores de main están confirmadas para #19–#23. La ejecución post-#24 estaba en curso en la última consulta.
4. **Informe técnico:** este documento actualiza el estado y las evidencias en un único lugar.
5. **Investigación y autonomía:** se integró búsqueda web inicial con trazabilidad de fuentes y abstención; se añadió una primera puerta de políticas de autonomía. No existe todavía síntesis automática contrastada ni planificador de tareas que ejecute acciones.
6. **Producción y piloto:** no completados. Falta infraestructura real, secretos, OIDC real, prueba real con proveedor, observabilidad operativa, pruebas de carga/seguridad/recuperación y protocolo de piloto autorizado.

## Capacidades actuales y límites

| Área | Estado | Qué significa realmente |
|---|---|---|
| Revisión local de privacidad | Prototipo integrado | La app local no envía texto; la detección es heurística y no garantiza anonimización. La ejecución automatizada de Windows no equivale a instalación validada en un equipo real. |
| Búsqueda web | Integrada en código | Endpoint autenticado; la consulta se transmite al proveedor si se configura la clave. La clave real no se ha confirmado en un entorno autorizado. |
| Evidencias | Integrado, inicial | Cada resultado se registra como fuente y el informe incluye abstención explícita; no se extraen afirmaciones ni se contrastan fuentes todavía. |
| Rate limit | Integrado en código y probado en CI | PostgreSQL compartido, límite atómico, 429/Retry-After y 503 si falla el almacenamiento; aún falta observarlo en despliegue real y programar/monitorizar la limpieza. |
| Puerta de autonomía | Integrada, inicial | Decide entre denegar, esperar aprobación o autorizar una acción catalogada. No ejecuta la acción ni autentica una aprobación humana real. |
| TRACE | Parcial | Hay `execution_id` para la búsqueda y la decisión de autonomía; falta enlazar toda la cadena de tareas y persistir eventos completos de forma operativa. |
| Procesamiento de sesiones CFE | Deshabilitado | No habilitar `POST /v1/process`; el motor CFE no está conectado. |
| Infraestructura productiva | No demostrada | Compose local y CI con PostgreSQL no equivalen a un servicio cloud seguro y desplegado. |
| Piloto | No ejecutado | No hay evidencia de un piloto supervisado ni de autorización operativa de un entorno real. |

## Bloqueos externos o de autorización

- Configurar `BRAVE_SEARCH_API_KEY` como secreto fuera de Git y ejecutar una búsqueda de extremo a extremo con consulta pública no sensible.
- Elegir/configurar proveedor OIDC real y gestor de secretos.
- Disponer de infraestructura privada para preproducción, observabilidad, backups y restauración.
- Definir responsable, límites y criterios de aceptación del piloto. El uso de datos reales de consultantes requiere autorización separada y evaluación de privacidad específica.

## Decisión actual

**XIL-AC no está aprobado para producción ni para procesar sesiones reales de consultantes.** El motor de investigación es una primera versión de recuperación y registro de fuentes, no un sistema autónomo de investigación completo. La puerta de autonomía es un control de política, no un ejecutor. Mantener bloqueado el procesamiento CFE hasta superar las puertas de calidad, privacidad, seguridad y autorización.
