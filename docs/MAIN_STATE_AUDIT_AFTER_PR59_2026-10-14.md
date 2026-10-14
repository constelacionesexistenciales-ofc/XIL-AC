# XIL-AC — auditoría de estado posterior a PR #59

**Fecha de corte:** 2026-10-14  
**Rama auditada:** `main`  
**SHA confirmado:** `22d0165cfdedc360120b56e96f9b97a55b8cfa2b`  
**Decisión de producción:** **NO-GO**. No habilitar sesiones reales ni procesamiento remoto.

## 1. Evidencia de la integración más reciente

La PR [#59](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/59) está fusionada en `main`. Su objetivo fue ampliar las regresiones de fidelidad de la asistencia en vivo (LIVE-16 a LIVE-22): atribución emocional no expresada, invención de historia personal, humor impuesto, intervención prematura, filtración de análisis interno, declaración falsa de éxito y simulación de ejecución.

Los checks asociados a la PR terminaron correctamente:
- [CI](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38496318959): éxito.
- [CodeQL](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38496318880): éxito.
- [SAST alternativo](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38496318918): éxito.

Tras la fusión, el análisis CodeQL de `main` también terminó correctamente: [ejecución 38496597810](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38496597810).

## 2. Pull requests pendientes y decisión de integración

| PR | Estado verificado | Próximo paso seguro |
|---|---|---|
| [#28 — endurecimiento de investigación](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/28) | Conflictos con `main`; checks asociados a un SHA anterior; análisis CodeQL omitido en esos checks. | Reconstruir selectivamente sobre el `main` actual. Preservar las protecciones de redirecciones ya integradas y añadir pruebas sin sobrescribirlas. |
| [#35 — seguridad de imagen/SAST](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/35) | Conflictos con `main`; el cambio retira un workflow CodeQL duplicado y añade controles de imagen/SAST. | Reconciliarlo con #28 y revisar los informes de imagen/SBOM. No integrar la rama divergente tal cual. |
| [#36 — indicador de movimiento de sesión](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/36) | Cambios extensos; pruebas funcionales y navegador previas aprobadas, pero hay ejecuciones CodeQL fallidas/neutral y la rama requiere actualización. | Rebasar/reconstruir, repetir todas las comprobaciones y revisar migración, autorización y borrado antes de considerar integración. |
| [#44 — matriz de integración](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/44) | Documento basado en un SHA anterior a #59. | Actualizar el documento al SHA actual antes de integrarlo. |
| [#3 — setup-python 7](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/3) | Checks de pruebas, navegador y SAST aprobados; CodeQL aparece neutral y el estado combinado requiere reconciliación. | Revalidar contra `main` actual y revisión humana antes de fusionar. |
| [#4 — checkout 7](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/4) | Checks de pruebas, navegador y SAST aprobados; CodeQL aparece neutral y el estado combinado requiere reconciliación. | Revalidar contra `main` actual y revisión humana antes de fusionar. |

No se fusionó ninguna de estas PR durante esta auditoría.

## 3. Cinco etapas: resultado

1. **Verificar la integración #59 — COMPLETADA.** Fusión y checks exitosos confirmados.
2. **Resolver PR de seguridad #28/#35 — EN CURSO.** Detectados conflictos y solapamiento; la integración directa sería insegura. Requiere reconstrucción selectiva.
3. **Revalidar dependencias #3/#4 — PARCIAL.** Los checks individuales listados están aprobados salvo CodeQL neutral; falta un estado combinado inequívoco sobre la base actual y revisión humana.
4. **Pruebas externas de seguridad — BLOQUEADAS POR ENTORNO.** No hay evidencia aquí de pruebas reales de DNS rebinding/SSRF con control de egreso, OIDC/JWT con proveedor real, restauración PostgreSQL, carga, failover ni rollback. No deben registrarse como ejecutadas.
5. **Evidencia y Puerta de Producción — ACTUALIZADA, NO APROBADA.** Se documentan los SHA, checks y pendientes. La aprobación requiere evidencias reproducibles, revisión independiente cuando corresponda y autorización humana explícita.

## 4. Bloqueos de producción que permanecen

- El filtro de privacidad debe ejecutarse localmente antes de transmitir contenido a una API remota.
- Ejecutar pruebas adversariales reales de SSRF y DNS rebinding y comprobar controles de salida de red.
- Verificar OIDC/JWT, emisor, audiencia, firma, expiración y roles con el proveedor del entorno objetivo.
- Demostrar consentimiento, minimización, retención, exportación, borrado efectivo y redacción de logs.
- Probar PostgreSQL de producción, TLS, migraciones, backups cifrados y restauración.
- Medir carga, fallos, recuperación y rollback.
- Validar el comportamiento del modelo con casos CFE sintéticos y revisión humana.
- Mantener `CFE_SESSION_PROCESSING_ENABLED=false` y la Puerta de Producción cerrada.

**Conclusión:** la fusión #59 fortalece la fidelidad de la asistencia y sus pruebas, pero no sustituye las verificaciones externas de seguridad, datos e infraestructura necesarias para autorizar producción.
