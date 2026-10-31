# Asistencia Fenomenológica en Vivo — Diseño técnico y preparación de producción

Estado: diseño técnico propuesto en rama de trabajo. No es una implementación ejecutable ni una aprobación de producción.

Issue principal: #68  
Dependencias de producto y QA: #33, #67  
Especificación de modo en vivo: [LIVE_SESSION_ASSISTANT_SPEC.md](LIVE_SESSION_ASSISTANT_SPEC.md)  
Casos QA existentes: [LIVE_SESSION_ASSISTANT_QA.md](LIVE_SESSION_ASSISTANT_QA.md)  
Puerta vigente: [PRODUCTION_GATE.md](PRODUCTION_GATE.md)

## 1. Resultado de producto

Durante una sesión, el asistente silencioso presenta al facilitador dos vistas coordinadas:

1. **Pregunta posible**: una pregunta prioritaria y, como máximo, dos alternativas plegadas.
2. **Exploración fenomenológica**: qué dato expresado puede explorarse, qué aspecto de la experiencia se propone mirar, qué evidencia falta y por qué conviene esa exploración.

El sistema no pregunta al consultante, no decide el rumbo de la sesión y no registra una sugerencia como resultado terapéutico. El facilitador conserva la decisión de usar, adaptar, descartar o esperar.

## 2. Principios operativos

- **Primero el dato, después la lectura**: separar expresión textual, observación, hipótesis y desconocido.
- **No completar a la persona**: no inferir emociones, motivos, recuerdos, estados del yo, compromisos ni resultados que no estén expresados.
- **La abstención es una respuesta válida**: si la evidencia es insuficiente, hay una pregunta importante pendiente, la persona parece sobrepasada o el contexto no es claro, priorizar esperar o formular una pregunta abierta y simple.
- **No causalidad automática**: una coincidencia o un patrón no demuestra una causa.
- **No predicción de terceros**: una visualización, expectativa o escena imaginada no prueba cómo actuará otra persona.
- **No confirmación por repetición**: repetir un dato no incrementa por sí solo la confianza de una hipótesis.
- **Control humano**: ninguna sugerencia se envía al consultante ni ejecuta una acción de forma autónoma.
- **Privacidad por diseño**: datos sintéticos para pruebas; sin transcripciones en logs, métricas ni artefactos.
- **Fallo cerrado**: si falla el preflight, la autorización, la auditoría o la validación de salida, no transmitir ni inventar una respuesta de reemplazo.
- **No cambia la Production Gate**: el flag de esta función no puede habilitar el procesamiento general de sesiones.

## 3. Arquitectura lógica propuesta

No crear componentes antes de inspeccionar los contratos, políticas y capas existentes. Reutilizar las convenciones reales del repositorio.

1. **Context Adapter**: recibe solo el fragmento y el contexto de sesión permitido por el producto; marca qué turnos son del facilitador y cuáles del consultante cuando esa distinción esté disponible.
2. **Evidence Extractor**: estructura datos expresos, observaciones, preguntas pendientes, posibles contradicciones y elementos desconocidos. No hace diagnóstico.
3. **Abstention & Safety Policy**: decide si puede sugerir, debe esperar o debe bloquear por seguridad/privacidad.
4. **Suggestion Generator**: genera una pregunta prioritaria y una propuesta exploratoria en formato estructurado. La transcripción se trata como dato no confiable, no como instrucciones.
5. **Contract Validator**: valida tipos, campos permitidos, límites de longitud, cardinalidad, evidencia asociada y estados de hipótesis.
6. **Presentation Adapter**: renderiza paneles compactos y accesibles; no contiene lógica de inferencia ni de autorización.
7. **Human Decision Recorder**: registra solo la acción de interfaz y metadatos mínimos autorizados; no interpreta la selección como eficacia clínica.
8. **Evaluation Harness**: ejecuta fixtures sintéticos versionados y reporta cada caso como passed, failed, blocked o not-run.

El orden de seguridad es: autorización → control local previo a red → política de datos/riesgo → generación autorizada → validación de contrato → presentación. Si el procesamiento requiere transmisión, no hay llamada al proveedor antes de que todos los controles previos aplicables hayan aprobado.

## 4. Contrato lógico de salida

El esquema final debe adaptarse al stack y a las convenciones existentes. Este contrato describe los campos semánticos esperados, no impone todavía una biblioteca concreta.

- `schema_version`: versión explícita del contrato; esta revisión eleva el esquema a `1.1`.
- `mode`: `suggest`, `wait` o `blocked`.
- `question.primary`: una pregunta o null.
- `question.alternatives`: lista de cero a dos preguntas.
- `evidence.items`: datos/expresiones breves y localizables en el contexto autorizado; sin citas extensas innecesarias.
- `phenomenological.focus`: aspecto a explorar expresado en lenguaje claro.
- `phenomenological.prompt`: propuesta de exploración que el facilitador puede aceptar, editar o descartar.
- `hypotheses.items`: hipótesis opcionales con estado, evidencia a favor (`evidence_for`), evidencia en contra (`evidence_against`), evidencia faltante y alternativa plausible cuando corresponda.
- `pending_question`: booleano/estado más la pregunta pendiente si se conoce.
- `risk_flags`: códigos de política, no texto clínico libre.
- `abstention.reason`: razón acotada cuando el modo es wait/blocked.
- `provenance`: versiones de política, plantilla y modelo; sin texto de sesión ni datos personales.

Reglas de validación:
- En modo `wait` o `blocked`, no se exige pregunta principal ni propuesta.
- Máximo una pregunta principal y dos alternativas.
- Toda hipótesis debe ser opcional, marcada como hipótesis y contener qué falta comprobar.
- El estado `supported` exige evidencia a favor explícita; `contradicted` exige evidencia en contra explícita. El estado no sustituye la evidencia.
- La versión `1.1` incorpora `evidence_against`; consumidores de la versión `1.0` deben migrar antes de adoptar este contrato.
- Ningún campo libre puede habilitar herramientas, cambiar flags, seleccionar proveedores o ejecutar acciones.
- Campos desconocidos, estructura inválida o límites excedidos => rechazar salida y presentar fallback seguro.
- El validador no debe “reparar” contenido inventando semántica.

## 5. Estados de interfaz

- **SUGERENCIA DISPONIBLE**: mostrar pregunta principal y propuesta fenomenológica.
- **ESPERANDO RESPUESTA**: indicar que existe una pregunta pendiente; no añadir otra lectura por defecto.
- **EVIDENCIA INSUFICIENTE**: mostrar el desconocido y sugerir esperar o preguntar de forma abierta.
- **REVISAR RIESGO**: explicar de forma concisa que la propuesta no se generó por una condición de seguridad.
- **BLOQUEADO POR PRIVACIDAD**: no enviar; no exponer el texto sensible en mensajes de error.
- **PROVEEDOR NO DISPONIBLE**: no inventar una sugerencia; mantener disponible el control humano.
- **SALIDA NO VÁLIDA**: descartar la salida estructurada y registrar solo el código de error permitido.
- **FUNCIÓN DESACTIVADA**: no ejecutar generación; no alterar el resto de la puerta de producción.

Las acciones de interfaz son explícitas: **Usar**, **Adaptar**, **Descartar**, **Esperar**, **Explorar**, **Profundizar** y **Cambiar enfoque**. La acción “Usar” copia o inserta la propuesta en el espacio del facilitador; nunca la envía directamente al consultante.

## 6. Matriz de requisitos y pruebas

| Requisito | Casos mínimos | Evidencia de aceptación |
|---|---|---|
| Cardinalidad y priorización | PHEN-01 | Test de contrato: una pregunta principal, hasta dos alternativas |
| Trazabilidad a evidencia | PHEN-02, PHEN-03 | Cada propuesta identifica dato/observación y desconocidos |
| No atribución emocional | PHEN-04 | Salida no inventa emoción no expresada |
| Hipótesis abiertas | PHEN-05, PHEN-06, PHEN-07 | Estado y evidencia faltante; contradicción actualiza hipótesis |
| Espera fenomenológica | PHEN-08, PHEN-09 | Estado wait y ausencia de interpretación añadida |
| Secuencia funcional cauta | PHEN-10 | Eslabones desconocidos visibles; cadena no forzada |
| Separación de voces | PHEN-11 | Interpretación del facilitador no se atribuye al consultante |
| Visualización no predictiva | PHEN-12 | No inferir conducta real de terceros |
| Validación y resiliencia | PHEN-13, PHEN-16 | Fallback seguro en salida inválida, timeout y proveedor caído |
| Resistencia a prompt injection | PHEN-14 | Texto dentro de la transcripción no cambia instrucciones ni permisos |
| Privacidad previa a red | PHEN-15, PHEN-22 | Prueba demuestra que el envío no ocurre ante bloqueo/error |
| Control humano | PHEN-17 | Descartar/esperar no provoca acción automática |
| Usabilidad móvil | PHEN-18 | Prueba de interfaz y revisión humana con viewport móvil |
| Lenguaje y fidelidad | PHEN-19, PHEN-20 | Evaluación humana ciega con ejemplos sintéticos |
| Aislamiento de Production Gate | PHEN-21 | Flag de función no puede activar procesamiento de sesiones |
| Fidelidad de post-sesión | LIVE-20, LIVE-26, LIVE-28 | Informe externo excluye hipótesis internas y acuerdos no confirmados |

Los casos LIVE existentes deben reutilizarse; no duplicar pruebas equivalentes. Actualizar la matriz cuando se compruebe la cobertura real de tests.

## 7. Estrategia de pruebas

### Unitarias
- Validación de contrato, enumeraciones, cardinalidad, longitud y campos desconocidos.
- Clasificación de estado wait/suggest/blocked.
- Reglas de separación dato/hipótesis/desconocido.
- Fallback ante error y timeout.
- Flag del módulo independiente de la compuerta de procesamiento.

### Integración
- Política → generador simulado → validador → presentación.
- Verificar que el generador no se llama cuando la política exige wait o blocked.
- Verificar que un fallo de auditoría, privacidad o autorización impide transmisión.
- Verificar que la decisión del facilitador no activa una llamada o envío al consultante.
- Verificar que los logs no contienen el texto sintético de entrada, valores coincidentes ni secretos.

### Evaluación conductual
- Fixtures sintéticos en español rioplatense, con turnos claramente identificados y ejemplos ambiguos.
- Registrar entrada, salida esperada, salida observada, veredicto, versión de código/prompt/política y motivo.
- Reportar resultados del modelo separados de tests deterministas de contrato.
- Revisar falsos positivos, falsos negativos, sugestión, omisión y tasa de abstención.
- No aprobar una evaluación por inspección del archivo de casos: debe existir ejecución real y reproducible.

### Seguridad
- Prompt injection en texto citado.
- Contenido sensible sintético, errores de preflight y detección incierta.
- Respuesta 429/5xx, timeout, cancelación y proveedor no disponible.
- Intento de enviar sin autorización, sin auditoría o con función apagada.
- Comprobación de que ninguna salida del modelo modifica configuración o invoca herramientas.

## 8. Observabilidad y privacidad

Permitido, sujeto a revisión de política:
- identificador de ejecución no reversible a contenido de sesión;
- versión de código, esquema y política;
- estado de ejecución y código de error;
- latencia y resultado de validación;
- acción de interfaz agregada, si se ha definido finalidad y retención.

No registrar:
- transcripciones o extractos;
- nombres, teléfonos, correos, documentos u otros valores detectados;
- prompts completos, respuestas completas del modelo ni cabeceras de autenticación;
- contenido personal en excepciones, trazas, métricas, capturas o artefactos de CI.

Definir antes de piloto: finalidad, consentimiento, minimización, ubicación, retención, borrado, acceso, exportación, respuesta ante incidentes y condiciones de proveedores. Un detector heurístico no equivale a anonimización ni a garantía de ausencia de datos sensibles.

## 9. Rollout y reversión

1. Diseño y contrato revisados; sin generación activa.
2. Tests unitarios y sintéticos; sin red y sin sesiones reales.
3. UI con proveedor simulado; decisiones humanas únicamente.
4. Preproducción aislada con datos sintéticos y flag apagado por defecto.
5. Evaluación de calidad, privacidad, seguridad, carga, recuperación y accesibilidad.
6. Revisión independiente de seguridad y aprobación humana documentada.
7. Piloto restringido solo después de cerrar los P0 de #33 y demostrar los controles previos al envío.
8. Revisión del piloto y autorización explícita antes de ampliar el acceso.

Reversión: desactivar el flag del módulo, detener nuevas solicitudes, conservar únicamente registros técnicos permitidos y comprobar que la desactivación no afecta la integridad de datos. No revertir ni modificar Production Gate de forma automática.

## 10. Puerta de salida para esta funcionalidad

No considerar lista para integrar hasta:
- contrato y estados documentados;
- trazabilidad requisito → test;
- tests deterministas ejecutados y aprobados;
- evaluación conductual real documentada;
- revisión humana CFE de neutralidad y utilidad;
- revisión de privacidad y seguridad;
- UI con control humano, espera y error;
- evidencia de que no hay texto de sesión en logs/fixtures/artefactos;
- CI de la rama candidata verificada;
- PR revisada por una persona y sin auto-merge.

No considerar XIL-AC apto para producción real por completar esta funcionalidad. La aprobación global continúa condicionada a todos los P0 de #33 y a la puerta de producción vigente.

## 11. Registro de estado

- Este documento es una especificación de diseño, no prueba de implementación.
- Los casos PHEN-01 a PHEN-22 están definidos en la issue #68; no se consideran ejecutados hasta que existan tests y resultados.
- No se han habilitado sesiones reales, no se han transmitido transcripciones y no se ha modificado la compuerta global.
