# XIL-AC — próximos 30 pasos ejecutables
**Fecha de corte:** 2026-10-11  
**Objetivo:** avanzar desde la base de ingeniería hacia autonomía verificable, sin abrir procesamiento CFE real antes de superar controles.  
**Regla:** propuesta no equivale a integración; archivo no equivale a prueba; prueba verde no equivale a seguridad total.

## Fase A — evidencia y CI
1. Capturar estado de PR #31 y #32 y sus ejecuciones actuales.
2. Verificar que el CI de PR #31 pasa en el SHA vigente.
3. Verificar el CI de PR #32 después de cada cambio.
4. Validar sintaxis y ejecución de Semgrep.
5. Validar ejecución de Trivy y revisar su informe, no solo el código de salida.
6. Mantener CodeQL como pendiente mientras el repositorio privado lo omita.
7. Documentar el bloqueo CodeQL y las alternativas sin hacer público el repositorio.
8. Revisar permisos mínimos y retención de artefactos de CI.

## Fase B — cadena de suministro y privacidad
9. Fijar acciones de terceros por SHA completo revisado antes de producción.
10. Establecer actualizaciones automáticas con revisión humana y pruebas.
11. Mantener SBOM y auditoría de dependencias por compilación.
12. Generar inventario separado de imágenes de contenedor y sus digests.
13. Reproducir instalación desde lockfile con hashes.
14. Añadir pruebas de seguridad para SSRF/DNS rebinding en inferencia local.
15. Verificar límites de tamaño, tiempo, redirecciones y respuestas.
16. Documentar datos que nunca deben enviarse a proveedores externos.

## Fase C — autonomía tecnológica
17. Revisar PR #27 (enrutador) y #29 (búsqueda) antes de integrarlas.
18. Ejecutar búsqueda contra una instancia SearXNG real aislada cuando exista entorno.
19. Conectar contratos de proveedor al núcleo sin saltarse las políticas.
20. Probar inferencia local con un servidor Ollama explícitamente configurado.
21. Comparar modelos locales y remotos en un conjunto versionado, sin datos de consultantes.
22. Medir calidad, latencia, memoria y coste por tarea.
23. Asegurar que la caída de proveedor termina en modo seguro, sin cambiar silenciosamente de política.

## Fase D — investigación y experiencia
24. Crear conjunto de evaluación en español con afirmaciones, fuentes, fechas y revisión humana.
25. Exigir trazabilidad de cada afirmación factual a su evidencia.
26. Distinguir resultado recuperado, inferencia, hipótesis y dato no verificado.
27. Crear interfaz universal de investigación con estados de progreso, fuentes y contradicciones.
28. Implementar filtro local previo al envío y pruebas de privacidad antes de cualquier uso CFE.

## Fase E — producción controlada
29. Añadir observabilidad sin registrar transcripciones ni secretos, además de copias y prueba de recuperación.
30. Ejecutar pruebas adversariales, carga, autorización, recuperación y la Puerta de Producción; mantener deshabilitado el procesamiento CFE hasta que todas las condiciones obligatorias estén aprobadas.

## Puerta de producción — criterios mínimos
- CI y análisis de seguridad finalizados y revisados; hallazgos críticos/altos resueltos o formalmente aceptados.
- Dependencias y acciones de terceros fijadas y revisables.
- Autenticación, autorización, gestión de secretos y migraciones probadas en el entorno de destino.
- Pruebas de privacidad preenvío, límites, SSRF, fallos y recuperación aprobadas.
- Evidencia de despliegue y restauración real.
- Evaluación CFE validada por responsables humanos; consentimiento, control humano y desactivación de emergencia.
- Aprobación explícita del responsable del proyecto.

## Ejecución inicial registrada
- Se consultaron las PR #31 y #32 y se confirmó que ambas siguen abiertas y en borrador.
- PR #31: CI reportada exitosa en la ejecución consultada; no fusionada.
- PR #32: Trivy actualizado a `aquasecurity/trivy-action@v0.36.0` y escáner `v0.74.0`; se verificaron ejecuciones Push y Pull Request exitosas en el SHA `f3bf98ce0f00485079910d6f724b05f1590bbe13`. Semgrep ejecutó 151 reglas sobre 24 archivos con 0 hallazgos; Trivy terminó sin disparar el umbral de fallo configurado HIGH/CRITICAL. Informes JSON disponibles como artefactos de CI.
- Luego se fijaron las cuatro acciones principales del flujo SAST por SHA verificado; el nuevo SHA `f37fad78325339d6545e81fbcdcebe7efc94b4d0` tiene ejecuciones nuevas en cola/en curso al cierre de este informe.
- CodeQL sigue sin producir un análisis útil: el workflow tiene una condición que lo omite para repositorio privado; la ejecución más reciente debe revisarse, y la alternativa SAST no se presenta como equivalente a CodeQL.
- No se han fusionado PR ni habilitado procesamiento de sesiones reales.
