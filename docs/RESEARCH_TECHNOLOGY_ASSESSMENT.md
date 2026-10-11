# Evaluación tecnológica: motor de investigación propio de XIL-AC

**Fecha de evaluación:** 2026-10-10  
**Estado:** análisis documental inicial; no equivale a una auditoría legal, prueba de carga ni validación en producción.  
**Decisión propuesta:** construir un núcleo de investigación propio, modular y medible; no integrar aún un proveedor nuevo ni habilitar producción.

## Resumen ejecutivo

XIL-AC puede reducir la dependencia de un proveedor único construyendo sus propios componentes de planificación de consultas, normalización, deduplicación, evaluación de fuentes, contraste de afirmaciones, trazabilidad y síntesis. No puede prometer independencia total de Internet: el acceso a páginas, índices, corpus, modelos y alojamiento sigue sujeto a disponibilidad, licencias, condiciones de uso y costes.

La búsqueda web actual en `core/research.py` está acoplada a Brave Search. El cambio de mayor valor es definir un contrato interno de proveedor y añadir fuentes especializadas de manera gradual. La interfaz no debe depender del proveedor ni presentar resultados recuperados como evidencia ya verificada.

## Tecnologías evaluadas

| Tecnología | Función útil | Ventajas | Límites y riesgos | Decisión |
|---|---|---|---|---|
| [SearXNG](https://docs.searxng.org/) | Metabúsqueda autohospedada que agrega motores de búsqueda | Código abierto; puede alojarse bajo control propio; evita acoplar la aplicación a una sola API | No es un índice web autónomo: muchos resultados siguen viniendo de motores externos, que pueden bloquear o limitar peticiones. Licencia AGPL-3.0: revisar compatibilidad y obligaciones antes de incorporarlo o modificarlo en un servicio de red | **Evaluar como adaptador desplegable aparte**, sin copiar código ni añadirlo al núcleo hasta revisión de licencia y pruebas |
| [OpenAlex API](https://help.openalex.org/api/) | Literatura académica: trabajos, autores, revistas, instituciones y temas | API documentada; uso básico gratuito; permite consultas académicas especializadas y ampliar límites con clave | Cobertura académica no equivale a toda la web; límites de uso, disponibilidad y condiciones siguen aplicando | **Prioridad alta** para un adaptador científico separado |
| [Common Crawl](https://commoncrawl.org/get-started) | Corpus e índices de páginas web rastreadas | Datos abiertos accesibles sin una API key para descarga HTTP; posibilidad de construir índices propios | Corpus masivo, no necesariamente actualizado al momento; construir y mantener índice propio exige almacenamiento, cómputo, filtrado, respeto de restricciones y operación | **Fase posterior de I+D**, no requisito inicial |
| Índice propio de XIL-AC | Recuperación de documentos ya obtenidos de fuentes permitidas | Control de esquema, ranking, deduplicación, caché, trazabilidad y evaluación | No crea acceso universal a la web; exige políticas de rastreo, actualización, almacenamiento, eliminación y control de costes | **Construir de forma incremental** empezando por corpus curados y fuentes abiertas |
| Modelos locales/abiertos | Clasificar, extraer afirmaciones y sintetizar documentos | Menor dependencia de una API de modelo; posibilidad de procesar datos en infraestructura propia | Hardware, calidad variable, seguridad de cadena de suministro, licencias y mantenimiento; un modelo local no garantiza veracidad | **Benchmark antes de seleccionar**; mantener interfaz de proveedor intercambiable |

## Arquitectura objetivo

1. **Orquestador de investigación:** transforma la pregunta en objetivo, alcance, fecha de corte y subpreguntas; aplica límites de tiempo y presupuesto.
2. **Registro de proveedores:** adaptadores con contrato común (`search(query, limit, filters)`) y capacidades declaradas. Un proveedor fallido no debe simular resultados.
3. **Fuentes especializadas:** web general, OpenAlex y repositorios abiertos; cada adaptador identifica su procedencia y condiciones.
4. **Normalización y deduplicación:** URL canónica, título, editor/autor, fechas, tipo de documento, fragmento y fecha de recuperación.
5. **Recuperación documental segura:** descarga limitada y con tiempo máximo; validación de esquema, tipo de contenido, tamaño, redirecciones y destinos para reducir SSRF. Respetar términos, robots y derechos aplicables.
6. **Motor de evidencia:** divide texto en afirmaciones verificables; enlaza cada afirmación con fragmentos de fuente y conserva evidencia contraria. No confundir ranking de búsqueda con fiabilidad.
7. **Síntesis fundamentada:** genera conclusiones con citas cercanas a cada afirmación; marca incertidumbre, vacíos y desacuerdos. No inventa citas.
8. **TRACE y gobierno:** execution_id, proveedor, tiempos, estado, conteos y decisiones; no registrar consultas sensibles ni secretos en logs. Human Gate para acciones de riesgo.
9. **Evaluación reproducible:** conjunto de consultas de referencia, fuentes esperadas, relevancia, fidelidad de citas, cobertura, latencia, coste y pruebas de privacidad.
10. **Interfaz universal:** muestra búsqueda, síntesis y evidencia como estados distintos. La interfaz no asigna por sí sola una etiqueta de “verificado”.

## Reglas de seguridad y privacidad

- Nunca enviar transcripciones, datos identificables o contenido sensible de sesiones CFE a proveedores externos.
- Los detectores heurísticos son una defensa parcial, no una garantía; mantener minimización de datos y advertencias explícitas.
- Secretos solo en un gestor de secretos o entorno seguro, nunca en Git, frontend ni registros.
- Aplicar timeout, límites de respuesta, límites de solicitudes y gasto, backoff, circuit breaker y respuesta cerrada ante fallos de auditoría.
- Tratar páginas recuperadas como datos no confiables: no ejecutar instrucciones contenidas en ellas.
- No habilitar procesamiento de sesiones reales como efecto colateral del módulo de investigación.

## Plan de implementación y puertas de calidad

### Fase 0 — verificación de base
- [x] Identificar acoplamiento actual a Brave en `core/research.py`.
- [x] Documentar estado de la interfaz: recupera resultados, pero no realiza síntesis ni evaluación automática.
- [ ] Ejecutar suite completa de CI y revisión de seguridad sobre la rama propuesta.
- [ ] Completar prueba de extremo a extremo con un secreto válido en un entorno controlado.

### Fase 1 — desacoplamiento
- [ ] Definir esquema tipado de consulta, fuente y resultado.
- [ ] Extraer protocolo de proveedor y conservar Brave como adaptador existente.
- [ ] Añadir pruebas contractuales compartidas para todos los adaptadores.
- [ ] Implementar límites de solicitudes/coste y métricas sin contenido de consultas.

### Fase 2 — fuentes alternativas
- [ ] Crear adaptador OpenAlex con límites, backoff, normalización y atribución.
- [ ] Evaluar SearXNG en despliegue aislado; revisar AGPL-3.0 y condiciones de motores upstream.
- [ ] Probar fallos, límites y degradación sin bloquear el resto del sistema.

### Fase 3 — evidencia y síntesis
- [ ] Recuperación segura de páginas/documentos permitidos.
- [ ] Extracción de afirmaciones y fragmentos de evidencia con ubicación de fuente.
- [ ] Contraste de fuentes independientes, contradicciones y evidencia contraria.
- [ ] Síntesis con citas por afirmación y abstención cuando no exista respaldo suficiente.

### Fase 4 — autonomía incremental
- [ ] Corpus curado propio, política de actualización y eliminación.
- [ ] Benchmark de índice local y modelos locales/abiertos frente a referencias.
- [ ] Estimar costes reales de infraestructura, operación y mantenimiento antes de expandir el rastreo web.

## Métricas de aceptación

No declarar superioridad sin medición. Comparar las mismas consultas y registrar:
- relevancia de los primeros 5/10 resultados;
- diversidad de fuentes y cobertura de fuentes primarias;
- porcentaje de afirmaciones factuales respaldadas por una cita correcta;
- citas que no respaldan la afirmación y citas inexistentes (objetivo: cero inventadas);
- tasa de contradicciones omitidas y abstenciones correctas;
- latencia p50/p95, fallos, coste por investigación y gasto mensual;
- falsos positivos/negativos de privacidad y ausencia de consultas sensibles en logs;
- reproducibilidad del informe con las mismas fuentes y fecha de corte.

## Criterio de decisión

La arquitectura debe priorizar el núcleo propio y los adaptadores intercambiables, no un nuevo acoplamiento. No añadir SearXNG al repositorio ni activar nuevos servicios hasta completar revisión de licencia, despliegue, seguridad y pruebas. No declarar independencia total ni producción activa mientras estas puertas estén pendientes.

## Fuentes consultadas

- SearXNG: documentación oficial y descripción del proyecto, https://docs.searxng.org/ y https://github.com/searxng/searxng (licencia indicada en el repositorio como AGPL-3.0).
- OpenAlex: autenticación, uso básico, API keys y límites, https://help.openalex.org/api/authentication/ y https://help.openalex.org/api/.
- Common Crawl: acceso al corpus e índices, https://commoncrawl.org/get-started y https://commoncrawl.org/overview.

Las afirmaciones sobre capacidades se basan en la documentación de los proyectos; la recomendación arquitectónica es una propuesta de diseño de XIL-AC, no un resultado de benchmark.
