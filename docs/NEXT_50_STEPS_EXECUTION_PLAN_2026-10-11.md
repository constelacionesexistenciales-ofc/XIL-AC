# XIL-AC — próximos 50 pasos técnicos y de validación

**Corte:** 2026-10-11  
**Objetivo:** avanzar hacia autonomía tecnológica verificable sin declarar producción antes de disponer de evidencia real.  
**Regla de ejecución:** cada paso se marca como HECHO solo con evidencia reproducible. Documentación, código en una PR y CI verde no sustituyen pruebas contra servicios desplegados.

## Estado ejecutivo

- **Verificado:** CI de PR #31 exitosa en el SHA 7477aef; CI de PR #32 exitosa en el SHA actualizado 1c0729db6e7e044953ea142655ca148ed11f33bf; Semgrep y Trivy finalizaron correctamente y sus informes se publicaron como artefactos con 30 días de retención.
- **Cambio realizado ahora:** workflow SAST actualizado en PR #32 a commit 1c0729db6e7e044953ea142655ca148ed11f33bf; se fijaron las llamadas restantes a checkout/upload-artifact por SHA y Semgrep a versión exacta 1.180.0. La ejecución SAST 38177719130 confirmó éxito en ambos trabajos y publicó informes nuevos; el CI general asociado seguía en curso al último chequeo.
- **Pendiente crítico:** CodeQL continúa omitido en el repositorio privado; PR #32 continúa en borrador; GitHub volvió a calcularla como mergeable=true, pero no se fusionó y requiere revisión humana.
- **No ejecutable desde el conector por sí solo:** despliegue real, instalación/descarga de modelos, ejecución real de SearXNG/Ollama, pentest, carga, RBAC/OIDC real, restauración de backups y aprobación de producción.
- **Seguridad:** PR #31/#32/#27/#29 siguen sin fusionar según la consulta; CFE permanece deshabilitado para sesiones reales.

## Fase 1 — estado, pruebas y evidencia (1–10)

1. **HECHO** — Consultar metadatos actuales de PR #31 y #32.
2. **HECHO** — Verificar CI de PR #31 en el SHA 7477aefcbde1cd789ac6ecfc34837a940e4d784c.
3. **HECHO** — Verificar CI anterior de PR #32 en f37fad78325339d6545e81fbcdcebe7efc94b4d0 y SAST actualizado en 1c0729db6e7e044953ea142655ca148ed11f33bf.
4. **HECHO** — Confirmar que Semgrep se ejecuta y finaliza sin activar el bloqueo en la ejecución actual 38177719130.
5. **HECHO** — Confirmar que Trivy se ejecuta y finaliza sin activar el umbral HIGH/CRITICAL en la ejecución actual 38177719130.
6. **HECHO** — Confirmar que existen artefactos JSON de Semgrep y Trivy, con caducidad de 30 días.
7. **HECHO** — Confirmar que CodeQL termina como skipped, no como análisis aprobado.
8. **HECHO** — Revisar los pasos del trabajo CI: SBOM, auditoría de dependencias, Bandit, Ruff y pruebas.
9. **HECHO** — Confirmar estado de PR #27 y #29: CI exitosa en los SHA consultados, PR abiertas.
10. **HECHO** — Registrar resultados y límites; nueva ejecución SAST revisada. El CI general del SHA 0a7e0cca625c77c6994cd58bc1748a0e56d69413 estaba en curso al último chequeo; volver a verificar antes de integrar.

## Fase 2 — cadena de suministro y CI (11–20)

11. **HECHO EN PR #32; REVALIDAR** — Fijar checkout, setup-python, upload-artifact y Trivy por SHA en el workflow SAST.
12. **HECHO EN PR #32; REVALIDAR** — Fijar Semgrep a 1.180.0 en vez de un rango flotante.
13. **PENDIENTE** — Revisar acciones transitivas y dependencias descargadas por cada acción fijada.
14. **PENDIENTE** — Añadir actualización automatizada controlada de acciones y dependencias con revisión humana.
15. **PARCIAL** — Generar SBOM Python en CI; generar SBOM para cada imagen de contenedor.
16. **PENDIENTE** — Fijar imágenes de contenedor por versión/digest; evitar latest en despliegues reproducibles.
17. **PENDIENTE** — Generar lockfile con hashes para las dependencias de Python.
18. **PENDIENTE** — Probar que la instalación desde lockfile funciona en entorno limpio.
19. **PENDIENTE** — Validar que Semgrep y Trivy fallan deliberadamente ante hallazgos de prueba controlados.
20. **PENDIENTE** — Revisar artefactos completos y documentar hallazgos, falsos positivos y excepciones con vencimiento.

## Fase 3 — privacidad, red y seguridad de entradas (21–30)

21. **PENDIENTE** — Modelar amenazas y límites de confianza entre API, núcleo, adaptadores, proveedores y datos de sesión.
22. **PENDIENTE** — Añadir pruebas SSRF con IPv4/IPv6, loopback, redes privadas, link-local y direcciones de metadatos.
23. **PENDIENTE** — Añadir pruebas de DNS rebinding y cambios entre resolución y conexión.
24. **PENDIENTE** — Revalidar destino después de cada redirección, incluidos esquemas, host y puerto.
25. **PENDIENTE** — Probar URLs con credenciales embebidas, puertos inválidos, IPv6 entre corchetes y nombres ambiguos.
26. **PENDIENTE** — Aplicar límites de cuerpo, tiempo, concurrencia, respuesta y memoria en cada adaptador.
27. **PENDIENTE** — Comprobar que las excepciones no exponen secretos, prompts, tokens ni contenido de consultantes.
28. **PENDIENTE** — Implementar filtro local de datos antes de cualquier llamada externa, con pruebas de no fuga.
29. **PENDIENTE** — Definir política de retención, exportación, eliminación y consentimiento para los datos operativos.
30. **PENDIENTE** — Ejecutar revisión independiente de privacidad y amenazas antes de cualquier piloto CFE.

## Fase 4 — autonomía de búsqueda e inferencia (31–40)

31. **PARCIAL** — Revisar PR #29: adaptador SearXNG propuesto; CI verde, pero falta instancia real.
32. **PENDIENTE** — Fijar imagen SearXNG a versión/digest y revisar configuración de motores.
33. **PENDIENTE** — Levantar SearXNG en una red aislada y confirmar consultas reales sin clave comercial.
34. **PENDIENTE** — Probar límites, errores, redirecciones, resultados malformados y caída de SearXNG.
35. **PENDIENTE** — Documentar que SearXNG puede consultar motores externos; no confundirlo con índice web propio.
36. **PARCIAL** — Revisar PR #27: el enrutador es determinista y falla de forma segura en pruebas; no ejecuta inferencia.
37. **PENDIENTE** — Instalar Ollama en un entorno de prueba controlado y obtener un modelo con licencia revisada.
38. **PENDIENTE** — Probar generación local real, timeout, límites de contexto, memoria y apagado del servicio.
39. **PENDIENTE** — Ejecutar benchmark versionado en español con entradas sintéticas y criterios humanos.
40. **PENDIENTE** — Medir calidad, latencia, consumo de memoria, coste y comportamiento bajo fallo; no declarar superioridad sin datos.

## Fase 5 — núcleo, investigación y operación (41–50)

41. **PENDIENTE** — Integrar contratos tipados de búsqueda e inferencia al núcleo solo después de aprobar adaptadores.
42. **PENDIENTE** — Mantener políticas, autorización y riesgo fuera del adaptador del modelo; impedir que el modelo eleve permisos.
43. **PENDIENTE** — Exigir execution_id y trazabilidad de decisiones sin guardar transcripciones en logs.
44. **PENDIENTE** — Construir conjunto de evaluación de investigación en español con fuentes, fecha, contradicciones y revisión humana.
45. **PENDIENTE** — Separar visualmente hechos, fuentes, inferencias, hipótesis y afirmaciones no verificadas.
46. **PENDIENTE** — Probar identidad real OIDC/JWT y matriz RBAC con casos permitidos y denegados.
47. **PENDIENTE** — Probar migraciones PostgreSQL, copias de seguridad y restauración completa en entorno aislado.
48. **PENDIENTE** — Ejecutar pruebas de carga, degradación, recuperación, alertas y procedimiento de reversión.
49. **PENDIENTE** — Validar en revisión humana que el flujo CFE no diagnostica, no reemplaza al facilitador y respeta el Modo Espera Fenomenológica.
50. **BLOQUEADO HASTA EVIDENCIA** — Ejecutar Puerta de Producción, resolver todas las condiciones críticas y obtener aprobación explícita antes de activar sesiones reales.

## Puerta de producción

La puerta permanece **CERRADA** hasta contar con CI y análisis de seguridad revisados en el SHA exacto, dependencias reproducibles, servicios reales probados, identidad/autorización, protección de datos, restauración, pruebas de carga y fallos, evaluación CFE humana y aprobación explícita. No se considera que los 50 pasos estén completados por el mero hecho de que estén enumerados.
