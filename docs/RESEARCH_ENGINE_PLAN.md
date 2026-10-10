# Motor de investigación de XIL-AC — especificación de implementación

## Estado

**Especificación y diseño; el motor autónomo no está conectado todavía.** La investigación puede continuar usando las herramientas disponibles en la interfaz de ChatGPT, pero no debe describirse como una función ya desplegada del servicio XIL-AC.

## Flujo previsto

1. **Definir la pregunta:** tema, alcance, fecha de corte y decisión que la investigación debe apoyar.
2. **Diseñar búsqueda:** generar términos y variantes; buscar fuentes primarias, revisiones y perspectivas críticas cuando existan.
3. **Recuperar fuentes:** usar adaptadores intercambiables; nunca acoplar la lógica central a un solo proveedor.
4. **Normalizar evidencia:** registrar título, autor/organización, URL, fecha de publicación, fecha de consulta, tipo de fuente y fragmento pertinente permitido.
5. **Evaluar calidad:** distinguir evidencia empírica, revisión, teoría, opinión, testimonio y material promocional; registrar limitaciones y posibles conflictos.
6. **Contrastar:** identificar convergencias, contradicciones, vacíos, hipótesis alternativas y cuestiones sin resolver.
7. **Síntesis CFE:** relacionar hallazgos con el marco CFE sin presentar la interpretación metodológica como hecho científico demostrado.
8. **Trazabilidad:** cada afirmación factual externa debe enlazarse a una fuente; separar citas, paráfrasis e inferencias del análisis.
9. **Revisión humana:** el usuario decide qué integrar a la metodología y qué queda como hipótesis.
10. **Registro reproducible:** guardar solo metadatos y resultados de investigación autorizados; no mezclar contenido identificable de consultantes con el corpus de investigación.

## Contrato de los adaptadores

Cada adaptador futuro deberá definir:
- consulta y filtros admitidos;
- proveedor y condiciones de uso;
- límites, tiempos máximos y errores;
- formato de resultados normalizado;
- enlaces de origen y fecha de recuperación;
- tratamiento de contenido y datos personales;
- pruebas con resultados vacíos, duplicados, errores y respuestas malformadas.

## Controles de calidad

- No inventar fuentes ni enlaces.
- No afirmar que se consultó una fuente si el adaptador no la recuperó.
- Detectar duplicados y páginas de baja calidad.
- Separar hechos de interpretaciones y recomendaciones.
- Conservar las fuentes contradictorias relevantes.
- No almacenar secretos ni transcripciones en el índice.
- Aplicar límites de solicitudes y respetar términos de uso y derechos de autor.
- Registrar fallos sin incluir consultas sensibles o datos personales.
- Incluir pruebas automatizadas y evaluación humana de una muestra de resultados.

## Fases

- **Fase 1 — diseño y catálogo de fuentes:** documentar categorías, criterios de calidad y esquema común.
- **Fase 2 — adaptadores reales:** seleccionar proveedor(es), configurar credenciales fuera del código y probar búsqueda/recuperación.
- **Fase 3 — síntesis y citas:** conectar recuperación, evaluación, contradicciones y referencias verificables.
- **Fase 4 — interfaz y auditoría:** mostrar fuentes, limitaciones y decisiones pendientes; permitir corrección humana.
- **Fase 5 — puerta de calidad:** pruebas de precisión, recuperación, atribución, errores, costo y seguridad antes de llamarlo operativo.

No declarar el motor activo hasta completar y verificar las fases necesarias en el entorno real.
