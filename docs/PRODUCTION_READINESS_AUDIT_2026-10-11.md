# Auditoría de preparación para producción — XIL-AC

**Fecha de corte:** 2026-10-11  
**Resultado:** NO APTO PARA PRODUCCIÓN REAL. Mantener cerrada la compuerta de sesiones CFE.

## Resumen ejecutivo

La rama principal documenta una base de ingeniería 0.4.1. La CI existente incluye pruebas unitarias e integración con PostgreSQL, Ruff, Bandit, generación de SBOM y auditoría de dependencias. En las ramas de trabajo hay avances de búsqueda autoalojada, estrategia de modelos abiertos y análisis SAST alternativo. Nada de esto demuestra que la aplicación esté desplegada o que el motor CFE esté integrado.

## Evidencia actual

- CI de PR #31 en el SHA 2827ab4b68892685a7721a702425143dd51a1840: éxito.
- SAST de PR #32 en el SHA 1c0729db6e7e044953ea142655ca148ed11f33bf: éxito; Semgrep ejecutó 151 reglas sobre 24 archivos y reportó 0 hallazgos. Trivy no activó el umbral HIGH/CRITICAL. Artefactos JSON publicados.
- CodeQL sigue terminando skipped en el repositorio privado; no cuenta como análisis ejecutado.
- README y docs/PRODUCTION_GATE.md declaran que el sistema no es candidato de producción y que el motor CFE no está conectado.
- POST /v1/process no debe considerarse funcional; los documentos indican HTTP 501 o bloqueo de sesiones según la versión/cambio en evaluación. Verificar el SHA de integración antes de cualquier exposición.
- La utilidad scripts.privacy_preflight existe como CLI local, pero no está integrada automáticamente con una interfaz que impida transmitir datos.
- PR #27, #29, #31 y #32 están abiertas; ninguna se fusionó durante esta auditoría.
- Se fijaron las acciones principales de CI (checkout, setup-python, upload-artifact) por SHA en la rama feat/technology-independence-v1, commit c154dad105f6ec4994fe5a306ae75a06e7303e25. La nueva CI de este commit debe pasar antes de considerar validado el cambio.

## Bloqueos de producción priorizados

### P0 — bloqueos absolutos

1. **Motor funcional:** integrar y probar el motor de procesamiento previsto; un endpoint, contrato o enrutador no equivale a inferencia real.
2. **Privacidad antes del envío:** integrar un filtro local obligatorio en la interfaz; probar que no se transmite texto sensible cuando hay detección, error o resultado incierto. No confiar únicamente en un filtro ejecutado en el servidor.
3. **Identidad real:** configurar OIDC/JWT con un proveedor real, comprobar issuer, audience, firma, expiración y roles con pruebas desde cliente externo; verificar que solo la identidad autorizada obtiene permisos operativos.
4. **Política de datos:** documentar finalidad, consentimiento, minimización, destinos externos, retención, exportación, borrado y respuesta ante incidentes. No enviar sesiones reales a proveedores no aprobados.
5. **Seguridad de red:** pruebas adversariales de SSRF, IPv4/IPv6, DNS rebinding, redirecciones, host/puerto y límites de recursos en adaptadores.
6. **Pruebas end-to-end:** verificar el flujo completo con datos sintéticos, fallos de proveedor, límites, bloqueo, auditoría y ausencia de fugas en registros.
7. **Puerta humana:** revisión independiente y aprobación explícita antes de abrir sesiones reales.

### P1 — operación confiable

8. **Secretos:** integrar gestor de secretos, mínimos privilegios, rotación y procedimiento de revocación.
9. **Datos y recuperación:** PostgreSQL administrado o autoalojado con TLS, migraciones, roles mínimos, copias cifradas y prueba real de restauración.
10. **Observabilidad:** métricas, alertas y trazas con execution_id, sin transcripciones, tokens, prompts privados ni datos identificables.
11. **Disponibilidad y límites:** concurrencia, cuotas por identidad, timeouts, 429/503, backpressure y degradación segura.
12. **Cadena de suministro:** lockfile con hashes, acciones fijadas, imágenes por digest, SBOM de imágenes y política de actualización revisada.
13. **Pruebas de carga y recuperación:** carga, saturación, reinicios, pérdida de base, proveedor caído, recuperación y rollback.
14. **Despliegue reproducible:** infraestructura, TLS, configuración, migraciones, secretos y verificación desde fuera del entorno.

### P2 — autonomía y calidad

15. **Búsqueda autoalojada:** ejecutar SearXNG real y comprobar motores, límites, errores y resultados. SearXNG no es un índice propio y puede depender de motores externos.
16. **Inferencia local:** ejecutar Ollama con modelo/licencia revisados; medir calidad en español, latencia, memoria, límites y fallos.
17. **Evaluación de investigación:** dataset sintético/versionado, fuentes por afirmación, fechas, contradicciones, incertidumbre y revisión humana.
18. **Evaluación CFE:** comprobar que el asistente no diagnostica, no sustituye al facilitador, diferencia datos/patrones/hipótesis y respeta el Modo Espera Fenomenológica.

## Estrategia recomendada: una ruta crítica, no 50 frentes paralelos

**Etapa A — cerrar la ingeniería base (1–2 ciclos):**
- Esperar CI del commit c154dad; corregir cualquier fallo.
- Revisar informes y probar deliberadamente el bloqueo de Semgrep/Trivy con fixtures sintéticos.
- Resolver dependencias y acciones reproducibles, sin fusionar PRs hasta tener CI verde y revisión humana.
- Mantener CodeQL como limitación explícita mientras siga omitido; no hacer público el repositorio para desbloquearlo.

**Etapa B — construir un vertical slice seguro:**
- Una sola ruta de extremo a extremo con autenticación real, validación de entrada, política de privacidad, execution_id, motor, adaptador de inferencia, límites y auditoría.
- Datos totalmente sintéticos; ningún dato de consultante.
- Sin proveedores externos por defecto. Habilitar cada proveedor solo tras prueba y política documentada.

**Etapa C — preproducción privada:**
- Entorno aislado, gestor de secretos, base con TLS, migraciones, observabilidad, copias y restauración.
- Probar autorización desde fuera, fugas, SSRF, caídas, carga y recuperación.
- No confundir despliegue exitoso con aprobación de procesamiento de sesiones.

**Etapa D — autonomía medible:**
- Ejecutar SearXNG y Ollama reales, medir resultados y comparar opciones en un benchmark reproducible.
- Adoptar el camino de menor coste total que satisfaga los umbrales de calidad, privacidad y latencia; no entrenar un modelo propio antes de demostrar que hace falta.
- Mantener el enrutamiento remoto bloqueado para contenido sensible si no existe una autorización explícita y verificable.

**Etapa E — lanzamiento limitado:**
- Revisión de seguridad independiente, checklist completa, rollback probado y aprobación explícita.
- Piloto interno con datos sintéticos; después, solo si se aprueba legal, operativa y técnicamente, un piloto restringido.
- Activar CFE_SESSION_PROCESSING_ENABLED únicamente mediante cambio controlado y evidencia firmada de la puerta aprobada.

## Criterio de salida

La producción solo puede aprobarse cuando cada bloqueo P0 tenga evidencia reproducible, todos los P1 aplicables estén operativos y revisados, y una persona responsable apruebe explícitamente la puerta. Hasta entonces: **NO USAR SESIONES REALES EN LA API REMOTA**.
