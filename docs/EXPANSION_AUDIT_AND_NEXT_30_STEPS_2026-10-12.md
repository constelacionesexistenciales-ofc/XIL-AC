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
35. SAST de PR #35 terminó en éxito ([run 38306227108](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38306227108)); revisar informes/artefactos y demostrar detección controlada aún pendiente.
36. Pendiente: revisar PR #28 y Dependabot #3/#4, resolver solapamientos y no fusionar solo por CI verde.

### Fase G — reproducibilidad y cadena de suministro (37–42)

37. Elegir una estrategia de dependencias bloqueadas compatible con Python y generar lockfile con hashes.
38. Instalar desde cero en un entorno limpio usando solo el lockfile; registrar versiones y resultado.
39. Fijar acciones externas por SHA completo revisado y documentar el proceso de actualización.
40. Fijar imágenes de contenedor por versión/digest; generar y guardar SBOM de la imagen.
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
- [x] Paso 32 (primera ejecución): CI de PR #35 pasó en SHA `de075f663a18a9d290c800cda505656b887b0426`; debe repetirse tras el último commit.
- [x] Paso 33 (diagnóstico): logs de CodeQL mostraron un error de configuración, no un fallo de extracción: “CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled”.
- [x] Decisión de arquitectura: usar la configuración predeterminada de CodeQL de GitHub como fuente única y retirar el workflow avanzado duplicado en la rama.
- [x] Paso 35 (primera ejecución): SAST alternativo pasó en PR #35; el contenido de sus informes todavía no fue inspeccionado.
- [ ] Paso 34: revisión manual de alertas CodeQL.
- [ ] Paso 35: prueba de detección controlada y lectura de informes JSON.
- [ ] Pasos 37–42: no afirmar lockfile, SBOM de imagen ni enforcement nuevo hasta generar y probar esos artefactos.
- [ ] Pasos 43–48: matriz de amenazas y pruebas de configuración SSRF en desarrollo; no sustituyen pruebas de DNS/red reales.
- [ ] Pasos 49–60: requieren servicios, secretos, infraestructura y/o aprobación humana; continúan bloqueados hasta configurar y validar el entorno.

La eliminación del workflow avanzado está en la rama de la PR, no en `main`. No se han habilitado sesiones reales ni se ha aprobado la Puerta de Producción.
