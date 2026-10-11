# XIL-AC

**Núcleo seguro y auditable para investigación general y para el futuro procesamiento CFE.**

Estado: **base de ingeniería 0.4.1; no aprobada para producción real**.

## Capacidades integradas en `main`

- API con autenticación, autorización por roles y validación estricta de configuración.
- Límite de 256 KiB para el cuerpo HTTP.
- Identificadores de ejecución, control de riesgo y auditoría técnica sin transcripciones.
- PostgreSQL, migraciones y limitación compartida de solicitudes para investigación.
- Primera ruta de búsqueda web protegida mediante Brave Search API.
- Registro estructurado de fuentes y abstención explícita cuando todavía no hay síntesis.
- Interfaz universal de investigación en `/research-ui/`.
- Pruebas automatizadas, integración continua, Ruff, Bandit y pruebas de navegador en flujos separados.
- Contenedor no-root y puerto local enlazado a localhost para desarrollo.

## Investigación web: alcance actual

La ruta `POST /v1/research` requiere autenticación y rol autorizado, aplica límites compartidos, evalúa señales heurísticas de privacidad y registra el evento de auditoría antes de enviar la consulta al proveedor. Requiere `BRAVE_SEARCH_API_KEY` configurada fuera del repositorio.

La recuperación devuelve resultados del proveedor y metadatos de procedencia. **Todavía no descarga y evalúa sistemáticamente el contenido de los artículos, no contrasta semánticamente afirmaciones ni produce una síntesis autónoma verificada.** No se debe presentar como motor de investigación completo.

La respuesta incorpora una evaluación explícita de metadatos (`source_assessment`): cantidad de fuentes, dominios únicos, diversidad de dominios, duplicados y campos faltantes. No asigna una puntuación de fiabilidad ni afirma que el contenido esté verificado. El registro de evidencia exige URL HTTPS públicas y rechaza hosts locales/privados, credenciales embebidas y puertos no estándar.

Los resultados se filtran a enlaces HTTPS públicos de formato permitido. Ese filtro reduce riesgos en los enlaces mostrados, pero no demuestra que una fuente sea fiable ni que su contenido sea verdadero.

## Privacidad y procesamiento CFE

`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. `POST /v1/process` sigue bloqueado mientras la función no esté implementada y aprobada. No enviar información de consultantes, transcripciones ni datos confidenciales a la API remota.

El detector de privacidad es heurístico: puede producir falsos positivos y falsos negativos. La detección dentro de la API ocurre después de que el cuerpo llegó al servidor; no sustituye la inspección local previa al envío. Existe una utilidad local inicial:

```bash
python -m scripts.privacy_preflight < texto.txt
```

Un resultado sin señales detectadas no garantiza que el texto esté libre de información sensible.

## Inicio local para desarrollo

1. Copiar `.env.example` a `.env`.
2. Sustituir los valores de desarrollo por secretos aleatorios propios.
3. Configurar `BRAVE_SEARCH_API_KEY` solo si se habilita la búsqueda real. Nunca guardar una clave real en Git.
4. Ejecutar `docker compose up --build`.
5. Comprobar `http://127.0.0.1:8000/health/live` y `/health/ready`.

Docker Compose es una configuración de desarrollo local, no una receta de despliegue productivo.

## Seguridad y estado de producción

La revisión de CodeQL del flujo anterior falló al intentar publicar resultados porque GitHub indicó que el análisis de código no estaba habilitado para el repositorio. Esto es un problema de configuración/entitlement del análisis; no prueba que el código esté libre de vulnerabilidades ni que se haya encontrado una vulnerabilidad concreta. CI también ejecuta Bandit como control estático adicional. Se agregó un flujo independiente de auditoría de dependencias con `pip-audit`; su resultado debe revisarse en cada ejecución y no reemplaza CodeQL.

Antes de producción todavía hacen falta, como mínimo: prueba de extremo a extremo con credenciales reales gestionadas como secretos; resolver la disponibilidad del análisis de código; verificar OIDC real y gestión de secretos; completar observabilidad, retención/borrado, límites de gasto, pruebas de carga y recuperación; y aprobar formalmente la puerta de producción.

Consultar [Puerta de producción](docs/PRODUCTION_GATE.md), [plan del motor de investigación](docs/RESEARCH_ENGINE_PLAN.md), [seguridad y datos](docs/SECURITY.md), [política operativa CFE](docs/CFE_OPERATING_POLICY.md) y [último informe de ejecución](docs/EXECUTION_REPORT_2026-10-11.md).
