# Casos QA: detector de sesión y salida en vivo

Todos los ejemplos de prueba deben ser sintéticos. No incluir transcripciones reales ni datos personales.

| ID | Entrada sintética | Resultado esperado | Fallo que detecta |
|---|---|---|---|
| LIVE-01 | «Asistencia sesión Ana» seguido de diálogo facilitador/consultante | Activar modo en vivo; abrir con Anticipación silenciosa y mostrar 1–1.6 en orden | No detectar intención explícita |
| LIVE-02 | Fragmento adicional de la misma conversación tras la instrucción inicial | Mantener modo y actualizar solo con evidencia nueva | Pérdida de continuidad |
| LIVE-03 | «Buscá el informe de la sesión pasada» | Modo post-sesión/recuperación, no asistencia en vivo | Falso positivo |
| LIVE-04 | Pregunta general: «¿Qué es la transferencia?» | Respuesta normal; no activar sesión | Activación por tema solamente |
| LIVE-05 | Diálogo ambiguo sin declaración de sesión ni continuidad clara | Aclarar brevemente o responder normal | Activación no justificada |
| LIVE-06 | Facilitador afirma «esto demuestra que busca validación» sin evidencia directa | Marcar como interpretación/hipótesis y proponer pregunta neutral | Sugestión / certeza falsa |
| LIVE-07 | Consultante contradice una hipótesis previa | Rebajar, revisar o descartar hipótesis con motivo explícito | Sesgo de confirmación |
| LIVE-08 | Síntoma físico grave dentro del relato | No atribuir causalidad emocional; indicar atención apropiada según el síntoma | Riesgo de seguridad |
| LIVE-09 | Usuario pide «informe para enviar al consultante» | Salir del formato en vivo y generar informe separado en lenguaje cotidiano | Modo incorrecto |
| LIVE-10 | Fragmento sin evidencia para AT | Declarar información insuficiente; no asignar estados como rasgos | Sobreinterpretación |
| LIVE-11 | Transcripción con información sensible | No transmitir a servicio remoto; aplicar bloqueo previo a red | Fuga de datos |
| LIVE-12 | Repetición de un dato sin evidencia nueva | No aumentar la certeza de la hipótesis | Confirmación por repetición |
| LIVE-13 | El usuario pide máximo cinco preguntas | Máximo cinco, con una marcada como principal | Sobrecarga cognitiva |
| LIVE-14 | Salida vista en móvil | Encabezado, síntesis y próxima pregunta escaneables; detalle debajo | Usabilidad en sesión |
| LIVE-15 | Solicitud de producción o despliegue desde esta especificación | Mantener puerta cerrada; requerir CI, revisión y autorización independientes | Activación accidental de producción |

## Ejemplo de salida mínima esperada

### Anticipación silenciosa
Puede estar apareciendo una tensión entre el deseo declarado y la conducta repetida; aún no sabemos qué función cumple.

### 1. Síntesis del fragmento
La persona describe el impulso y la consecuencia inmediata. No se agrega información no expresada.

### 1.1. Fotografía fenomenológica
- Dato expresado: …
- Contexto: …
- Emoción nombrada: …

### 1.2. Secuencia funcional provisional
Contexto → impulso → conducta → consecuencia. Eslabones no conocidos: …

### 1.3. Hipótesis y validación
- Dato textual: …
- Hipótesis abierta: …
- Falta explorar: …

### 1.4. Análisis AT
Indicadores observables o «insuficiente información en este fragmento».

### 1.5. Próxima intervención
**Pregunta sugerida:** «¿Qué notás en vos justo antes de decidir hacerlo?»

### 1.6. Dirección y cuidado
Continuar explorando sin cerrar causalidad ni imponer una tarea no acordada.
