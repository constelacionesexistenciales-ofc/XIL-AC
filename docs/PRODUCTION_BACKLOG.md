# Pendientes para producción — XIL-AC

**Estado global: NO APTO PARA PRODUCCIÓN REAL.** Esta lista separa controles implementados, trabajo de ingeniería pendiente y validaciones que requieren configuración o autorización humana. Un archivo de configuración o una ejecución de CI no demuestran por sí solos que un servicio remoto esté seguro.

## P0 — Bloqueos antes de cualquier uso real

| Estado | Pendiente | Evidencia de cierre requerida |
|---|---|---|
| En curso | CI, Ruff, pruebas y CodeQL de las ramas activas | Ejecución verde vinculada al commit exacto; revisar alertas, no solo el estado general |
| Pendiente | Identidad OIDC real | Pruebas contra proveedor configurado: token válido, inválido, expirado, audiencia/emisor incorrectos, roles ausentes y rol no autorizado |
| En validación | Límite inicial compartido por PostgreSQL | CI, prueba de integración contra PostgreSQL y prueba concurrente; verificar 429/Retry-After y cambio de ventana |
| Pendiente | Límites de gasto y cuotas del proveedor | Cuota/alerta del proveedor y límite de aplicación verificados; comportamiento cerrado ante exceso |
| Pendiente | Protección web para el despliegue elegido | CORS restrictivo, CSRF si hay cookies, CSP, cabeceras de seguridad y TLS verificados desde el cliente real |
| Pendiente | Secretos en entorno real | Gestor de secretos configurado, acceso mínimo, rotación documentada; nunca secretos en Git, frontend, artefactos ni logs |
| Pendiente | Observabilidad segura | Métricas de disponibilidad, errores, latencia y gasto sin consultas, tokens ni contenido de sesiones |
| Pendiente | Recuperación de base de datos | Copia cifrada, retención definida y restauración ensayada con evidencia |
| Pendiente | Despliegue y rollback | Entorno identificado, migración probada, health checks, rollback y verificación postdespliegue |
| Bloqueado por diseño | Procesamiento real de sesiones CFE | No habilitar: el motor no está conectado. Requiere evaluación de privacidad, consentimiento, minimización, proveedores y aprobación explícita |

## P1 — Necesarios para una beta controlada de investigación

- [ ] Prueba de extremo a extremo con clave de proveedor válida en entorno privado; no usar datos personales.
- [ ] Evaluar falsos positivos y falsos negativos del detector de privacidad con datos sintéticos; no tratarlo como garantía.
- [ ] Probar navegador real, interacción y tamaños de pantalla; confirmar el flujo de CI de Chromium.
- [ ] Registrar estado, proveedor, latencia y conteos sin guardar consultas ni fragmentos sensibles.
- [ ] Límites por usuario, por IP cuando corresponda y por gasto; protección contra reintentos abusivos.
- [x] Script de limpieza por lotes para la tabla `rate_limit_buckets`.
- [ ] Programar la limpieza periódica en el entorno de despliegue y verificar su ejecución/alertas.
- [ ] Validar la retención efectiva y el rendimiento de la limpieza con una base de datos representativa.
- [ ] Manejo de caídas, timeouts, límites del proveedor y respuestas malformadas.
- [ ] Revisar CORS/CSP/CSRF y cookies según la autenticación y el origen final de la interfaz.
- [ ] Verificar dependencias, imágenes de contenedor, permisos y política de actualización.
- [ ] Pruebas de carga moderada, aislamiento y solicitudes concurrentes.
- [ ] Definir retención, eliminación y exportación de los metadatos técnicos.

## P2 — Completar el motor de investigación

- [ ] Contrato común de proveedor para desacoplar la API de Brave.
- [ ] Adaptador científico OpenAlex y evaluación aislada de SearXNG; revisar licencia y condiciones upstream.
- [ ] Recuperación segura de documentos permitidos, con límites anti-SSRF y control de contenido.
- [ ] Extracción de afirmaciones con fragmentos y localizadores de fuente.
- [ ] Contraste de fuentes independientes, evidencia contraria y contradicciones.
- [ ] Síntesis con citas por afirmación, incertidumbre y abstención ante evidencia insuficiente.
- [ ] Corpus curado e índice propio incremental; evaluar Common Crawl solo tras estimar coste.
- [ ] Benchmark reproducible de relevancia, fidelidad de citas, cobertura, latencia y coste.
- [ ] Evaluación de modelos abiertos/locales antes de seleccionar o desplegar uno.

## Criterios de aceptación de producción

La puerta no se considera aprobada hasta que:
1. Todos los P0 aplicables tengan evidencia reproducible y revisión.
2. CI, pruebas de seguridad, análisis estático y dependencias estén sin bloqueos abiertos.
3. La autenticación y autorización hayan sido verificadas contra el proveedor real.
4. La limitación de uso funcione entre instancias, tenga retención/limpieza definida y falle de forma segura si la base de control no está disponible.
5. La tarea de limpieza periódica esté programada y monitorizada.
6. Copias de seguridad y rollback hayan sido probados, no solo configurados.
7. No se almacenen consultas, transcripciones, claves ni tokens en registros.
8. La persona responsable otorgue aprobación humana explícita para el alcance exacto del despliegue.

## Alcance que sigue deshabilitado

`POST /v1/process` y el procesamiento de sesiones reales permanecen cerrados por defecto. No incluir transcripciones de consultantes en pruebas de nube ni en proveedores de búsqueda/modelos. Una beta de investigación general no autoriza el procesamiento CFE.

## Registro de implementación

- [x] Documentar el inventario priorizado y la evidencia de cierre.
- [x] Implementación inicial de límite compartido por PostgreSQL; pruebas unitarias añadidas.
- [x] Añadir script de limpieza por lotes y pruebas unitarias.
- [ ] Confirmar CI, integración real y concurrencia; implementar límites de gasto/cuota del proveedor.
- [ ] Resolver el resto de bloqueos P0 uno por uno; no declarar producción por anticipado.
