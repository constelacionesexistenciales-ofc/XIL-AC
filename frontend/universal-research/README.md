# Experiencia universal de investigación — prototipo

Interfaz estática, adaptable y sin dependencias de compilación para explorar la experiencia visual transversal de investigación de XIL-AC/SILAC.

## Ejecutar localmente

Abrí `index.html` en un navegador moderno. No requiere instalar paquetes ni ejecutar un servidor.

## Contenido

- `index.html`: estructura semántica de la interfaz en español.
- `styles.css`: sistema visual adaptable, diseño móvil y soporte para movimiento reducido.
- `app.js`: interacciones de demostración y cambio de esquema conceptual según la disciplina.

## Estado y límites

**Esto es un prototipo visual interactivo, no un motor de investigación conectado.** No consulta fuentes, no usa modelos de lenguaje, no guarda investigaciones y no debe presentar el contenido de ejemplo como hallazgos verificados. La interfaz muestra explícitamente ese límite.

La integración real necesita conectarse al contrato de resultados de investigación de XIL-AC, usar metadatos de fuentes verificadas y conservar las etiquetas de evidencia y la trazabilidad del motor. No habilita ni modifica el procesamiento de sesiones CFE.

## Validación manual sugerida

1. Abrir la página y comprobar la carga sin errores.
2. Cambiar de disciplina y enviar una pregunta: cambia el esquema ilustrativo y el aviso indica que no se ejecutó una investigación.
3. Expandir y contraer cada ruta de profundización.
4. Probar «Nueva investigación» y «Copiar pregunta».
5. Verificar la lectura en móvil a 320, 375 y 650 px.
6. Navegar con teclado y comprobar el foco visible.
7. Confirmar que no se muestran citas ficticias ni resultados simulados como hechos reales.
