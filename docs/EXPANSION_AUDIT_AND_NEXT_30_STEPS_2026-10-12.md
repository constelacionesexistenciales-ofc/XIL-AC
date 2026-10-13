# XIL-AC — auditoría de expansión y ejecución de 30 pasos

**Corte de auditoría:** 2026-10-12  
**Rama de trabajo:** `audit/expansion-30-step-execution-2026-10-12`  
**Base auditada:** `main` en `6a483735ac5c88f972ca48dac45b1b0815b3cbdc`  
**Decisión de producción:** NO-GO. El procesamiento de sesiones CFE debe permanecer deshabilitado.

## 1. Resultado ejecutivo

XIL-AC ya dispone de una base ampliable: API FastAPI, autenticación y roles, control de privacidad heurístico, auditoría y `execution_id`, límite de solicitudes, contratos de proveedores, enrutador determinista, adaptador local Ollama optativo, recuperación inicial de fuentes, registro de evidencias, evaluador de políticas de autonomía, interfaz de investigación y pruebas automatizadas.

Esto demuestra **capacidad de expansión arquitectónica**, no autonomía integral ni operación productiva. El enrutador todavía no ejecuta inferencia; el adaptador local no demuestra que Ollama/modelos estén instalados; la investigación recupera y registra fuentes, pero no realiza todavía síntesis contrastada; la puerta de autonomía decide, pero no ejecuta acciones ni autentica una aprobación humana real.

### Evidencia revisada

- Repositorio público y activo: [XIL-AC en GitHub](https://github.com/constelacionesexistenciales-ofc/XIL-AC).
- SHA principal auditado: `6a483735ac5c88f972ca48dac45b1b0815b3cbdc`.
- CI de `main`: [ejecución 38296724126](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38296724126), conclusión `success`.
- SAST alternativo Semgrep/Trivy: [ejecución 38296724110](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38296724110), conclusión `success`. Deben revisarse los informes JSON; el estado exitoso no prueba ausencia absoluta de riesgos.
- CodeQL automático de GitHub en `main`: [ejecución 38305482632](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38305482632), conclusión `success`; se confirmaron análisis exitosos para Python, JavaScript/TypeScript y GitHub Actions.
- La ejecución del workflow avanzado de prueba en PR #35 ([run 38306227059](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38306227059)) terminó en `failure` al cargar SARIF: GitHub indicó que la configuración predeterminada estaba habilitada y no acepta resultados de una configuración avanzada simultánea. La extracción y generación SARIF sí llegaron a completarse.
- Decisión correctiva: eliminar el workflow duplicado y conservar CodeQL Setup predeterminado como fuente única de análisis, en lugar de pedir al usuario que mantenga dos configuraciones incompatibles.
- PR abierta de endurecimiento de investigación: [PR #28](https://github.com/constelacionesexistenciales-ofc/XIL-AC/pull/28). No integrar automáticamente ni duplicar sus cambios.
- Puerta vigente: [docs/PRODUCTION_GATE.md](PRODUCTION_GATE.md).

**Límite de evidencia:** no se pudo confirmar desde esta auditoría el número ni la severidad de las alertas CodeQL. La lista debe revisarse en [Code scanning alerts](https://github.com/constelacionesexistenciales-ofc/XIL-AC/security/code-scanning).

## 2. Primeros 30 pasos: ejecución y estado

Los pasos distinguen inspección, cambio propuesto y validación real. “Preparado en PR” no significa integrado.

| N.º | Acción | Estado | Resultado / criterio de cierre |
|---:|---|---|---|
| 1 | Confirmar repositorio, rama y SHA base | HECHO | Repositorio público; `main` en SHA indicado arriba. |
| 2 | Inspeccionar árbol de archivos y módulos | HECHO | Se confirmó núcleo, API, adaptadores, interfaz, migraciones, scripts y pruebas. |
| 3 | Verificar CI principal de `main` | HECHO | Run 38296724126 terminó en éxito para el SHA auditado. |
| 4 | Verificar ejecución SAST alternativa | HECHO PARCIAL | Run 38296724110 terminó en éxito; falta revisar los artefactos JSON completos y probar detección controlada. |
| 5 | Verificar CodeQL propio | HECHO | Run 38296724238 está omitido; no se considera análisis aprobado. |
| 6 | Contrastar CodeQL automático de GitHub | HECHO | Run 38305482632 terminó en éxito y analizó tres lenguajes/tipos de código. |
| 7 | Resolver la duplicación de CodeQL | CORRECCIÓN EN ESTA RAMA | Se retiró el workflow avanzado duplicado tras verificar que GitHub rechaza su SARIF cuando está habilitado CodeQL predeterminado. Se conserva el análisis predeterminado de GitHub; validar nuevo run tras el cambio. |
| 8 | Revisar alertas CodeQL | BLOQUEADO POR VERIFICACIÓN | El endpoint de alertas no quedó verificable desde esta auditoría; revisar en la interfaz de GitHub. |
| 9 | Revisar puerta de producción y privacidad | HECHO | La puerta mantiene sesiones reales bloqueadas; el filtro de API no reemplaza el filtro local previo al envío. |
| 10 | Registrar resultados y criterios de aceptación | HECHO | Este documento registra evidencia, límites y siguiente secuencia. |
| 11 | Crear rama aislada de corrección | HECHO | Rama `audit/expansion-30-step-execution-2026-10-12`. |
| 12 | Modificar CodeQL sin tocar `main` | HECHO EN RAMA | Commit inicial de cambio: `3928f08516aa1572d3ccaf6c285fc9c6f33eab96`. |
| 13 | Ejecutar CI de la PR #35 | HECHO | [Run 38306227495](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38306227495) terminó en `success` en el SHA `de075f663a18a9d290c800cda505656b887b0426`. |
| 14 | Diagnosticar CodeQL de la PR #35 | HECHO | El run 38306227059 falló al subir SARIF por coexistencia con CodeQL predeterminado; se retiró el workflow avanzado duplicado en esta rama. Falta comprobar el run posterior. |
| 15 | Revisar hallazgos de CodeQL | PENDIENTE | Inspeccionar alertas, severidad, rutas de datos y falsos positivos. |
| 16 | Revisar PR abiertas y evitar integración duplicada | HECHO | PR #28 está abierta; Dependabot #3 y #4 también están abiertas. Revisar conflictos antes de integrar. |
| 17 | Validar acciones de CI fijadas por SHA | PARCIAL | CI y SAST fijan varias acciones; CodeQL en esta rama conserva referencias de versión y necesita decisión/pinning revisado. |
| 18 | Confirmar lockfile reproducible con hashes | PENDIENTE | `pyproject.toml` usa rangos; no se verificó un lockfile con hashes reproducible. |
| 19 | Revisar SBOM de aplicación y contenedor | PARCIAL | CI genera SBOM del entorno Python; falta inventario verificable de imagen de contenedor/digest. |
| 20 | Probar que SAST falla ante un hallazgo controlado | PENDIENTE | Añadir prueba aislada de escáner con hallazgo de laboratorio y comprobar bloqueo. |
| 21 | Revisar SSRF y DNS rebinding | PARCIAL | La PR #28 declara endurecimiento de URL; falta ejecutar y verificar casos adversariales contra el estado que se vaya a integrar. |
| 22 | Revisar límites de red y recursos | PARCIAL | Existen límites de cuerpo, tiempo y respuesta en componentes; falta cobertura adversarial completa por adaptador. |
| 23 | Verificar privacidad previa a la transmisión | PENDIENTE CRÍTICO | Integrar el filtro local en el cliente/interfaz y demostrar que bloquea antes de toda petición externa. |
| 24 | Definir retención, exportación, borrado y consentimiento | PENDIENTE | Documentar y probar ciclo de vida de datos, no solo políticas escritas. |
| 25 | Probar proveedor de búsqueda real | BLOQUEADO POR ENTORNO | Requiere secreto configurado fuera del repositorio y consulta pública no sensible. |
| 26 | Probar inferencia local real | BLOQUEADO POR ENTORNO | Requiere Ollama/modelo instalados, licencia revisada y mediciones reproducibles. |
| 27 | Conectar motor CFE al flujo de forma controlada | PENDIENTE | Usar primero datos sintéticos; mantener deshabilitado el procesamiento real. |
| 28 | Validar OIDC/JWT y RBAC en un entorno real | BLOQUEADO POR CONFIGURACIÓN | El código preparado no sustituye proveedor, claves, emisores, audiencia y pruebas externas reales. |
| 29 | Validar PostgreSQL, secretos, backups y restauración | BLOQUEADO POR ENTORNO | CI usa PostgreSQL de prueba; falta infraestructura objetivo y restauración demostrada. |
| 30 | Ejecutar Puerta de Producción | BLOQUEADO | No aprobar hasta cerrar los P0, evidenciar seguridad/carga/recuperación y obtener aprobación humana explícita. |

### Resultado real de esta ejecución

- Se inspeccionó el estado de GitHub y la arquitectura existente.
- Se confirmó la diferencia entre CI exitosa, CodeQL automático exitoso y workflow CodeQL propio omitido.
- Se creó una rama de trabajo y se preparó una corrección acotada de CodeQL.
- **No se modificó `main`, no se fusionó ninguna PR y no se habilitaron sesiones reales.**
- Los pasos que requieren secretos, infraestructura, servicios instalados, datos de prueba controlados o aprobación humana permanecen pendientes.

## 3. Próximos 30 pasos: plan correlativo 31–60

### Fase F — cerrar el cambio de seguridad (31–36)

31. PR #35 creada como borrador; mantenerla abierta hasta cerrar las verificaciones.
32. CI de PR #35 terminó en `success` en SHA `de075f663a18a9d290c800cda505656b887b0426`; al borrar el workflow duplicado, repetir la comprobación en el nuevo SHA.
33. Diagnóstico completado: el workflow avanzado generó SARIF pero la carga falló porque CodeQL predeterminado está habilitado; se eliminó el workflow duplicado en la rama. Verificar el análisis automático posterior.
34. Pendiente: revisar alertas de CodeQL en la interfaz de GitHub; no se ha confirmado cantidad ni severidad.
35. SAST de PR #35 pasó en SHA `aa0c81fcad8bbbdb77487717138578a9efcb60c6` ([run 38307610813](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38307610813)). Semgrep: 0 resultados, sin errores, 151 reglas en 25 archivos. La autoprueba detectó 1 hallazgo sintético bloqueante, como se esperaba. Trivy: 20 comprobaciones de configuración de Dockerfile exitosas y 0 fallidas; el JSON no contiene resultados de vulnerabilidades/secretos y no se interpreta como prueba universal de ausencia de riesgos.
36. Pendiente: revisar PR #28 y Dependabot #3/#4, resolver solapamientos y no fusionar solo por CI verde.

### Fase G — reproducibilidad y cadena de suministro (37–42)

37. Elegir una estrategia de dependencias bloqueadas compatible con Python y generar lockfile con hashes.
38. Instalar desde cero en un entorno limpio usando solo el lockfile; registrar versiones y resultado.
39. Fijar acciones externas por SHA completo revisado y documentar el proceso de actualización.
40. PARCIAL: CI ya construye la imagen y genera SBOM CycloneDX (118 componentes); Trivy de imagen encontró 44 hallazgos HIGH agrupados en 8 CVE únicos sin versión corregida indicada, por lo que el gate falla. Falta remediar/verificar las CVE, fijar digest y conservar SBOM de imagen.
41. Definir actualización de dependencias con PR automáticas, CI obligatoria y revisión humana.
42. Probar que el pipeline falla ante vulnerabilidades de severidad bloqueante y conserva informes aun cuando el job falle.

### Fase H — privacidad y defensa de red (43–48)

43. Modelar amenazas y fronteras de confianza entre interfaz local, API, núcleo, proveedor de búsqueda, modelo local y almacenamiento.
44. Crear una matriz adversarial SSRF: IPv4/IPv6, loopback, redes privadas, link-local, metadatos, puertos y URL con credenciales.
45. Probar DNS rebinding y volver a validar cada destino después de redirecciones; bloquear por defecto si no puede verificarse.
46. Integrar el control de privacidad en el cliente local antes de cualquier envío; demostrar con pruebas de red que los casos bloqueados no transmiten el texto.
47. Probar límites de cuerpo, tiempo, concurrencia, respuesta y memoria; verificar que errores y logs no revelan texto sensible ni secretos.
48. Definir y probar consentimiento, minimización, retención, exportación y borrado, con registros de auditoría que no almacenen transcripciones.

### Fase I — autonomía útil, medible y controlada (49–54)

49. Configurar SearXNG en entorno aislado y ejecutar una consulta pública de prueba sin datos sensibles.
50. Instalar un modelo local con licencia revisada y probar el adaptador Ollama sin fallback remoto.
51. Conectar búsqueda e inferencia mediante contratos tipados, límites y políticas fuera del proveedor; el modelo no puede elevar permisos.
52. Construir un corpus sintético en español que incluya ambigüedad, fuentes contradictorias, datos ficticios y evidencia insuficiente.
53. Medir precisión de citas, afirmaciones sin soporte, abstención, contradicciones, latencia, memoria y coste; publicar resultados reproducibles.
54. Completar la investigación con separación visual de hechos, fuentes, inferencias, hipótesis e incertidumbre; cada afirmación factual debe enlazar evidencia o abstenerse.

### Fase J — operación, evaluación CFE y preproducción (55–60)

55. Probar OIDC/JWT y RBAC reales con identidades autorizadas y denegadas, expiración, emisor, audiencia, firma y revocación.
56. Configurar secretos fuera del repositorio, rotación y permisos mínimos; probar que nunca aparecen en logs o artefactos.
57. Desplegar un entorno privado de preproducción con TLS, PostgreSQL, migraciones, límites, métricas y alertas sin contenido sensible.
58. Ejecutar pruebas de backup/restauración, carga, caída de proveedores, degradación, cancelación, rollback y recuperación.
59. Validar con revisión humana el flujo CFE usando datos sintéticos: no diagnosticar, preservar el control del facilitador y respetar el Modo Espera Fenomenológica.
60. Ejecutar la Puerta de Producción y decidir GO/NO-GO con evidencia; mantener el bloqueo si queda un P0, una incertidumbre crítica o una aprobación externa pendiente.

## 4. Criterio de expansión

Prioridad recomendada: **seguridad reproducible → privacidad previa al envío → servicios reales de prueba → evaluación de calidad → preproducción privada → aprobación humana**.

No abrir 30 frentes de código simultáneos. Avanzar por bloques pequeños, con una PR por cambio coherente, CI en el SHA exacto y evidencia verificable. No habilitar sesiones reales ni enviar transcripciones a proveedores remotos mientras la Puerta de Producción permanezca cerrada.


## 5. Registro incremental de ejecución del plan 31–60

### Hechos verificados en esta continuación

- [x] Paso 31: PR #35 abierta como borrador.
- [x] Paso 32: CI de PR #35 pasó en SHA `bc74f72df24653b23bfe41f9fb654ba28a2ce6fa`: 118 tests aprobados, 1 advertencia; `pip-audit` informó que no encontró vulnerabilidades conocidas. Tras los cambios posteriores de endurecimiento, CI debe volver a ejecutarse en el nuevo SHA.
- [x] Paso 33 (diagnóstico): logs de CodeQL mostraron un error de configuración, no un fallo de extracción: “CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled”.
- [x] Decisión de arquitectura: usar la configuración predeterminada de CodeQL de GitHub como fuente única y retirar el workflow avanzado duplicado en la rama.
- [x] Paso 35 (parcial): SAST alternativo pasó en SHA `bc74f72`; Semgrep reportó 0 resultados/0 errores y Trivy informó 20 comprobaciones de configuración de Dockerfile exitosas/0 fallidas. Falta detección controlada y ampliar evidencia de escaneo de dependencias/secretos.
- [ ] Paso 34: revisión manual de alertas CodeQL; la consulta del endpoint de alertas no está disponible mediante el conector actual, por lo que requiere revisión en la interfaz de GitHub.
- [x] Paso 35 (parcial): JSON de Semgrep y Trivy inspeccionados; la autoprueba de Semgrep detectó el hallazgo sintético esperado. La cobertura de Trivy para vulnerabilidades/secretos sigue siendo una limitación.
- [ ] Pasos 37–42: no afirmar lockfile, SBOM de imagen ni enforcement nuevo hasta generar y probar esos artefactos.
- [x] Paso 43 (parcial): se agregó `docs/THREAT_MODEL_INITIAL_2026-10-12.md`, con activos, fronteras de confianza, amenazas y evidencia de cierre.
- [x] Paso 44 (parcial): se agregaron casos unitarios para URLs SearXNG inseguras/malformadas y redirecciones de origen distinto; se amplió la matriz para IP privadas en HTTPS, loopback IPv6, IP no especificada, loopback alternativo, credenciales vacías y dominios especiales. CI/SAST pasaron en SHA `aa0c81fcad8bbbdb77487717138578a9efcb60c6` (126 tests aprobados, 1 advertencia).
- [x] Endurecimiento adicional: los handlers de redirección ahora rechazan URLs con usuario/contraseña embebidos; añadido test para rechazar cambios de origen y permitir redirección del mismo origen sin credenciales.
- [ ] Pasos 45–48: DNS rebinding, control de salida real, prueba de ausencia de transmisión y ciclo de vida de datos siguen pendientes; los tests unitarios no sustituyen pruebas de red.
- [ ] Pasos 49–60: requieren servicios, secretos, infraestructura y/o aprobación humana; continúan bloqueados hasta configurar y validar el entorno.

La eliminación del workflow avanzado está en la rama de la PR, no en `main`. No se han habilitado sesiones reales ni se ha aprobado la Puerta de Producción.

### Cambios técnicos añadidos en esta continuación

- `tests/test_research_security.py`: pruebas parametrizadas para bloquear IPs de metadatos, redes privadas, loopback IPv6, URL con credenciales, query/fragment no permitidos, esquemas no admitidos y puertos inválidos antes de abrir conexión.
- `core/research.py`: los handlers de redirección Brave/SearXNG rechazan URL con usuario o contraseña embebidos; el handler SearXNG mantiene restricción de mismo origen.
- `docs/THREAT_MODEL_INITIAL_2026-10-12.md`: modelo de amenazas inicial y evidencias necesarias para cerrar cada riesgo.
- La prueba automatizada todavía no se ha declarado aprobada: esperar CI en el SHA final de la PR. No se realizaron pruebas reales de DNS ni de salida de red.


## 6. Actualización posterior — ejecución máxima posible

**Corte de evidencia:** 2026-10-12. Esta sección prevalece sobre cualquier estado anterior que indique que los runs del SHA `bc74f72` seguían pendientes.

- CI del SHA `bc74f72df24653b23bfe41f9fb654ba28a2ce6fa`: `success`; logs: 118 tests aprobados, 1 advertencia; `pip-audit` indicó “No known vulnerabilities found”.
- SAST alternativo del mismo SHA: `success`. Semgrep 1.180.0 inspeccionó 25 archivos Python y ejecutó 151 reglas: 0 resultados y 0 errores.
- Artefacto Trivy inspeccionado: contiene un resultado de configuración para `Dockerfile`, con 20 comprobaciones exitosas y 0 fallidas. No contiene resultados de análisis de vulnerabilidades ni secretos; este límite queda abierto y no debe traducirse como “cero vulnerabilidades”.
- CodeQL predeterminado en el mismo SHA: `success` para Python, JavaScript/TypeScript y GitHub Actions. La lista/severidad de alertas no pudo recuperarse mediante el endpoint disponible en esta conexión; la revisión manual en GitHub sigue pendiente.
- Advertencias de CI a tratar: deprecación de Starlette relacionada con `httpx`, advertencias de `url.parse()` y de acciones que usan Node.js 20.
- En respuesta al análisis de amenazas, `core/research.py` ahora rechaza IP literales no públicas como destino base de SearXNG, incluidos destinos privados en HTTPS, y nombres de uso especial en HTTPS; mantiene solo la excepción explícita HTTP `127.0.0.1` para desarrollo local. Se añadieron casos de regresión a `tests/test_research_security.py`. **Estos últimos cambios todavía deben pasar CI en el SHA nuevo.**
- Estado de PRs abiertas comprobado: #35 borrador; #28 abierta; Dependabot #3 y #4 abiertas. No se fusionó ninguna PR ni se modificó `main`.

### Estado actualizado por bloque

- 31–33: HECHO en el SHA anterior; repetir validación final tras el endurecimiento recién añadido.
- 34: PENDIENTE — revisar alertas CodeQL manualmente.
- 35: PARCIAL — informes inspeccionados; detección controlada pendiente; Trivy no aporta evidencia de hallazgos de vulnerabilidad/secretos en el JSON recibido.
- 36: PARCIAL — PRs identificadas; comparación de diffs y plan de integración aún pendiente.
- 37–42: PARCIAL — SBOM CycloneDX de imagen generado y escaneo real implementado; el gate detectó 44 hallazgos HIGH (8 CVE únicos, sin versión corregida indicada) y falla correctamente. Lockfile con hashes, pinning completo y remediación siguen pendientes.
- 43–44: PARCIAL — threat model y matriz unitaria ampliada; falta validación adversarial de red.
- 45–48: PENDIENTE — DNS rebinding, egress real, no-transmisión y ciclo de vida de datos.
- 49–54: PENDIENTE DE ENTORNO — servicios reales, inferencia, corpus y métricas.
- 55–60: PENDIENTE DE CONFIGURACIÓN/APROBACIÓN — identidad real, secretos, preproducción, recuperación y Puerta de Producción.

**Decisión:** NO-GO para sesiones reales hasta que la evidencia faltante sea resuelta y la aprobación humana quede registrada.


## 7. Cierre de validación del cambio de seguridad

- SHA final validado en esta iteración: `aa0c81fcad8bbbdb77487717138578a9efcb60c6`.
- [CI push](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38307610818): `success`; 126 tests aprobados, 1 advertencia; Ruff y Bandit aprobados; `pip-audit` indicó que no encontró vulnerabilidades conocidas; el SBOM Python se generó y el gate de dependencias pasó.
- [SAST push](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38307610813): `success`. Semgrep 1.180.0: 0 hallazgos en el código escaneado, 0 errores, 151 reglas y 25 archivos; autoprueba sintética: 1 hallazgo detectado y validación aprobada.
- Trivy 0.74.0: el artefacto reporta 20 comprobaciones de configuración del Dockerfile exitosas y 0 fallidas. No hay entradas de vulnerabilidades/secretos en el JSON recibido; el escaneo de archivos no sustituye una auditoría completa de imagen y dependencias.
- La advertencia de CI permanece identificada; no se considera un fallo de pruebas, pero debe revisarse en mantenimiento.
- El cambio en SearXNG ahora rechaza IP literales no públicas como destino base y ciertos nombres de uso especial por HTTPS; los tests de regresión quedaron cubiertos por CI.
- La ejecución de SAST de `push` pasó. Un run separado por `pull_request` seguía en curso en el momento del corte; la PR permanece en borrador y no se fusionó.

**No completado por falta de evidencia/entorno:** revisión manual de alertas CodeQL, comparación completa de cambios solapados con PR #28 y Dependabot, DNS rebinding y egress real, lockfile reproducible con hashes, SBOM de imagen, servicios de inferencia/búsqueda reales, identidad y secretos de preproducción, restauración de backups, prueba de carga/failover y aprobación de producción.

**Decisión vigente: NO-GO para sesiones reales.**


## 8. Resultado de escaneo de imagen — hallazgo bloqueante

En el SHA `407a2df60c8e862040d8d57dc0f5d3b888b8a6a7`, el nuevo job construyó la imagen local y generó el SBOM CycloneDX. El escaneo de imagen de Trivy terminó en fallo por hallazgos HIGH, como exige el gate:

- SBOM CycloneDX: 118 componentes; generado correctamente.
- Imagen escaneada: `xilac-ci:407a2df60c8e862040d8d57dc0f5d3b888b8a6a7`, base Debian 13.7.
- Trivy: 44 hallazgos HIGH de paquetes del sistema, correspondientes a 8 CVE únicos; el informe no indica versión corregida para esos registros. No se observaron hallazgos CRITICAL, de configuración ni de secretos en las entradas examinadas.
- Informe y SBOM quedaron empaquetados en el artefacto `xilac-container-sbom-and-trivy` del run [38307834425](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38307834425).

**Interpretación:** no es un falso positivo demostrado ni corresponde suprimirlo automáticamente. Se debe comprobar la disponibilidad de parches upstream, actualizar/reconstruir la imagen base y repetir el escaneo. Si no hay corrección disponible, documentar cada excepción con exposición, mitigación y aceptación explícita de riesgo. La imagen no debe considerarse aprobada mientras el gate permanezca rojo.

El job de imagen está funcionando como control efectivo y reveló un riesgo que el escaneo de archivos no mostró. La Puerta de Producción sigue en NO-GO.
