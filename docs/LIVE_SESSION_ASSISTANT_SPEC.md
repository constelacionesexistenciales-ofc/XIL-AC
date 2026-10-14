# Interfaz de asistencia en sesión en tiempo real

Estado: especificación propuesta para revisión; no habilita procesamiento remoto de sesiones ni modifica la puerta de producción.

## Objetivo

Cuando el contexto indique claramente que el facilitador está conduciendo una sesión y comparte fragmentos de diálogo, XIL-AC debe responder como copiloto en vivo. La salida empieza por **Anticipación silenciosa** y mantiene los apartados 1–1.6 de análisis del facilitador, actualizados con cada fragmento. Debe ser visual, escaneable y suficientemente breve para leer mientras la conversación continúa.

Esta especificación aplica a cualquier caso o disciplina configurada; CFE es el dominio inicial. No implica que el sistema pueda detectar audio/transcripciones de forma autónoma si la interfaz no le entrega esos datos.

## Detección de modo

### Señales fuertes para activar

- El usuario declara «asistencia sesión», «estoy en sesión», «asistí en vivo» o equivalente y luego aporta diálogo.
- El mensaje contiene un flujo de turnos de facilitador/consultante, preguntas sucesivas y respuestas en primera persona que parecen continuar una conversación en curso.
- El usuario dice explícitamente «seguí asistiendo en vivo» o «te voy pasando lo que responde».

### Señales débiles

- Mención de una sesión pasada, solicitud de informe, resumen, auditoría o análisis retrospectivo sin indicios de continuidad en vivo.
- Preguntas generales sobre coaching, terapia, CFE o XIL-AC.

Las señales débiles no activan por sí solas el modo en vivo. Si la intención es ambigua, hacer una sola pregunta breve de aclaración o responder en modo normal.

### Salida del modo

Cambiar a modo post-sesión cuando el usuario pida explícitamente informe final, informe para consultante, auditoría completa, evaluación de proceso o cierre. No tratar automáticamente cada nueva mención de un consultante como una sesión activa.

## Diseño de salida en vivo

Orden obligatorio en cada respuesta de asistencia en vivo:

### Anticipación silenciosa
- Una lectura breve de qué podría estar emergiendo y qué conviene observar a continuación.
- No formular la hipótesis como hecho ni comunicar al consultante interpretaciones internas no validadas.
- Señalar un riesgo de sugestión si el facilitador parece haber adelantado una explicación.

### 1. Síntesis del fragmento
Dos a cuatro frases con lo nuevo aportado en este turno y cómo conecta con lo anterior. Evitar repetir la transcripción completa.

### 1.1. Fotografía fenomenológica
Lista breve de hechos expresados, emociones nombradas, conductas observadas en el relato y contexto relevante. No inferir estados internos que el consultante no expresó.

### 1.2. Secuencia funcional provisional
Cuando exista evidencia suficiente, mostrar:
contexto/antecedente → experiencia o impulso expresado → conducta → consecuencia inmediata o posterior → punto de elección.
Marcar explícitamente los eslabones desconocidos. No forzar una cadena si el fragmento no la sostiene.

### 1.3. Hipótesis y validación
Usar estados controlados:
- **Dato textual**
- **Patrón provisional**
- **Hipótesis abierta**
- **Evidencia que falta / alternativa**
- **Contradicha o descartada**
Nunca elevar una hipótesis por repetición, por inferencia del facilitador ni por aceptación ambigua. Incluir explicaciones alternativas cuando sean plausibles.

### 1.4. Análisis AT: transacciones y estados del yo
Solo describir indicadores observables y como posibilidades de trabajo, no como rasgos o diagnóstico. Distinguir comunicación/transacción del facilitador y del consultante cuando la transcripción lo permita. Si no hay evidencia, declarar «insuficiente información en este fragmento».

### 1.5. Anticipación de la próxima intervención
Una recomendación principal y hasta cinco preguntas posibles, ordenadas por prioridad. En tiempo real mostrar primero **la próxima pregunta sugerida**; las demás pueden quedar como alternativas. Preferir preguntas abiertas, neutrales y no sugestivas. No sugerir al facilitador respuestas o motivos que el consultante no haya expresado.

### 1.6. Dirección de trabajo y cuidado
- Indicar el movimiento exploratorio más útil para el siguiente turno.
- Si surge un acuerdo real, registrarlo como acuerdo; no inventar tareas ni compromisos.
- Señalar límites de seguridad cuando corresponda, sin convertir la sesión en diagnóstico médico o psicológico.
- Evitar informes al consultante, auditoría técnica y conclusiones finales mientras la sesión siga activa, salvo petición explícita.

## Contrato de brevedad y actualización

- La salida completa conserva los apartados 1–1.6, pero cada apartado usa solo la información necesaria del fragmento actual.
- Encabezado y próxima pregunta deben ser visibles sin desplazarse demasiado en móvil.
- Máximo cinco preguntas; una recomendación principal.
- Actualizar hipótesis solo ante evidencia nueva, contradictoria o relevante.
- Mantener continuidad entre fragmentos dentro del contexto autorizado; no inventar memoria de sesiones anteriores.
- No almacenar transcripciones reales en logs técnicos, artefactos de CI o fixtures. Pruebas con datos sintéticos únicamente.
- El facilitador mantiene el control: las sugerencias son opcionales y no ejecutan acciones sobre el consultante.

## Privacidad y seguridad

- No transmitir transcripciones sensibles a una API remota mientras la puerta de producción siga cerrada.
- La inspección local debe ocurrir antes de cualquier envío de red y bloquear ante contenido sensible o resultado no verificable.
- No registrar el texto de la sesión en trazas técnicas; registrar solo identificadores, eventos mínimos, estados y errores permitidos por la política de retención.
- Una alerta de salud se expresa de forma prudente y no causal. Ante síntomas graves o de alarma, priorizar valoración profesional urgente.
- Esta especificación documental no activa `CFE_SESSION_PROCESSING_ENABLED` ni cambia el estado de producción.

## Criterios de aceptación

1. Con señal fuerte de sesión activa, la respuesta empieza por «Anticipación silenciosa».
2. Los apartados 1, 1.1, 1.2, 1.3, 1.4, 1.5 y 1.6 aparecen en ese orden.
3. La síntesis y la secuencia incluyen solo datos sustentados por la transcripción.
4. Cada hipótesis tiene estado y evidencia faltante; no se transforma en hecho sin validación.
5. La próxima intervención sugerida es abierta y no sugestiva.
6. No se generan informes post-sesión si el usuario sigue compartiendo diálogo en vivo.
7. Una petición explícita de informe final cambia al modo post-sesión.
8. Las señales débiles no activan el modo automáticamente.
9. Las pruebas no contienen datos reales de consultantes.
10. No se habilita procesamiento remoto ni se abre la puerta de producción como consecuencia de esta función.

## Fidelidad al lenguaje y generación de textos personales

- En discursos, cartas u otros textos en nombre del consultante, separar hechos y expresiones aportados por la persona de las propuestas creativas del asistente.
- No inventar anécdotas, recuerdos compartidos, cualidades personales ni detalles biográficos para hacer que un texto parezca auténtico.
- Cuando los datos personales sean insuficientes, ofrecer una base genérica explícitamente identificada como borrador y señalar dónde incorporar recuerdos reales.
- El humor es opcional: no forzar chistes solo porque se haya pedido un tono ligero. Si el consultante reacciona de forma ambigua a una frase, explorar primero qué le sucede con esa expresión.
- Si el facilitador acaba de formular una pregunta y la respuesta aún no está disponible, no atribuir una emoción ni completar el significado por la persona. Priorizar una pregunta abierta y esperar evidencia nueva.
- No se habilita procesamiento remoto de sesiones como consecuencia de esta especificación; requiere controles técnicos y aprobación independientes.

11. Los textos personales no incluyen anécdotas ni detalles biográficos inventados.
12. Una reacción ambigua ante humor genera exploración, no una interpretación ni otro chiste automático.
13. Una pregunta pendiente no se trata como si el consultante ya la hubiera respondido.
14. Los resultados de pruebas se etiquetan como observados, fallidos, bloqueados o no ejecutados; no se simulan.
