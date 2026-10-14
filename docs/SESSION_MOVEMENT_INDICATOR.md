# Indicador de disponibilidad, energía y movimiento — XIL-AC

## Objetivo
Evaluar el encuentro según su propósito contextual y el movimiento observable entre llegada, proceso y cierre; no medir la sesión por la finalización obligatoria de una secuencia. La estabilización, la pausa, la disponibilidad o una apertura parcial pueden ser resultados pertinentes. No se exige una decisión ni una acción externa en todas las sesiones.

## Dimensiones
- **Disponibilidad:** posibilidades internas para acercarse a la experiencia, observarla o considerarla.
- **Capacidad de acción:** posibilidades percibidas de afrontar, expresar, elegir, hacer o dejar de hacer.
- **Capacidad integradora:** posibilidad de relacionar experiencia, reconocimiento y opciones sin exigir resolución completa.
- **Movimiento fenomenológico:** cambio en la manera de vivir, expresar u observar la situación.
- **Vitalidad percibida:** energía/vitalidad que la persona reconoce.
- **Disponibilidad para afrontar:** energía funcional disponible para abordar la situación presente. Se distingue de la vitalidad.

Cada dimensión usa 0–4 y admite **NE** (no evaluable). 0 es una puntuación evaluada; NE significa que no hay base suficiente para puntuar. Registrar la fuente de cada toma: autorreporte del consultante, observación del facilitador o revisión conjunta. No presentar estas escalas como instrumentos clínicos validados.

## Uso durante el encuentro
1. Crear un registro con un objetivo de sesión predefinido, sin escribir nombre, tema identificable ni transcripción.
2. Registrar **llegada** antes o al inicio.
3. Registrar **durante** solo cuando aporte valor; puede repetirse y no constituye una obligación.
4. Registrar **cierre** cuando corresponda. La sesión se cierra en el indicador y ya no admite nuevas tomas.
5. La interfaz muestra comparación de llegada/cierre, variaciones y dimensiones NE. Las variaciones se calculan únicamente cuando ambos valores son evaluables.

## Informes posteriores
El informe interno puede incorporar un bloque “Movimiento durante el encuentro” con objetivo, llegada, variaciones, estado al cierre, fuente de cada puntuación y limitaciones. No convertir las puntuaciones en diagnóstico ni usarlas para clasificar al consultante. En el informe que se envía al consultante, incluir únicamente una descripción humana y validada por el facilitador, nunca una calificación numérica no conversada.

## Privacidad y control
- No se guardan nombres, transcripciones, notas libres ni detalles del motivo de consulta.
- Los registros se vinculan al usuario autenticado del facilitador y solo este usuario puede consultarlos.
- No almacenar tokens en el navegador ni registrar puntuaciones en trazas de aplicación.
- La API utiliza SESSION_MOVEMENT_ENABLED=false por defecto. Habilitarlo solo tras aplicar la migración 0003, revisar control de acceso/retención, ejecutar CI, validar en un entorno de prueba y obtener aprobación humana explícita.
- Esta funcionalidad no habilita el motor CFE ni abre CFE_SESSION_PROCESSING_ENABLED. La Puerta de Producción general permanece independiente y puede seguir en NO-GO.

## Interpretación responsable
Un cambio positivo en una puntuación no prueba por sí solo que la intervención lo haya causado. Menor activación o energía al cierre no implica automáticamente peor resultado; revisar objetivo, contexto, fuente, relato del consultante y criterio del facilitador. Los datos NE no equivalen a capacidad ausente.
