# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.4.1; todavía no es candidata a producción real**.

## Incluye
- API mínima con roles, validación OIDC/JWT en modo estricto y token local solo para desarrollo.
- Validación estricta de configuración y uso obligatorio de HTTPS para el proveedor de identidad.
- Límite de 256 KiB para el cuerpo HTTP antes de analizar la solicitud.
- Identificador de ejecución y control de riesgo que bloquea niveles desconocidos.
- Comprobación de PostgreSQL, migraciones y auditoría técnica sin transcripciones.
- Detector heurístico de posibles datos sensibles, con categorías de riesgo y sin devolver los valores coincidentes.
- Pruebas automatizadas, integración continua con PostgreSQL, análisis estático, CodeQL y Dependabot.
- Docker Compose local con puerto publicado solo en localhost y contenedor no-root.

## Privacidad y modos de trabajo
La investigación general ya tiene una primera ruta de búsqueda web en la rama de integración: requiere token autorizado y clave externa configurada. Devuelve resultados recuperados, pero todavía no sintetiza ni contrasta afirmaciones; no debe describirse como motor autónomo completo. Durante esta etapa, el trabajo de sesiones se realiza por la interfaz de ChatGPT; no enviar información de consultantes a la API remota.

El detector identifica señales explícitas como correos, teléfonos, documentos etiquetados, nombres etiquetados y referencias a salud, violencia, abuso o autolesión. Es heurístico: puede equivocarse y no garantiza detectar todo contenido sensible.

**Importante:** el detector integrado en la API se ejecuta después de que el cuerpo de la solicitud llegó al servidor. Es una barrera adicional, no un filtro previo al envío. Hace falta una interfaz local que inspeccione el contenido antes de transmitirlo; hasta entonces, no envíes contenido de consultantes a la API remota.

`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. `POST /v1/process` devuelve HTTP 423 cuando detecta señales sensibles o mientras el procesamiento esté deshabilitado. El motor CFE sigue sin estar conectado y no hay despliegue cloud verificado. Consultar [Política operativa CFE](docs/CFE_OPERATING_POLICY.md), [plan del motor de investigación](docs/RESEARCH_ENGINE_PLAN.md) y [Puerta de producción](docs/PRODUCTION_GATE.md).

## Inspección local preventiva de privacidad

Hay una utilidad CLI de inspección local que no realiza conexiones de red y no imprime el texto recibido:

```bash
python -m scripts.privacy_preflight < texto.txt
```

La utilidad **siempre bloquea la transmisión** y devuelve código de salida `2`, tanto si detecta señales como si no las detecta. Devuelve categorías y nivel de riesgo; un resultado sin señales explícitas no demuestra que el texto esté libre de datos sensibles. Un error del detector también bloquea. No interpretar nunca el resultado como autorización para enviar. Esta utilidad no está integrada automáticamente con una interfaz ni sustituye la compuerta remota.

## Inicio local con Docker
1. Copiar `.env.example` a `.env`.
2. Reemplazar `XILAC_API_TOKEN` y `POSTGRES_PASSWORD` por valores aleatorios largos. Son solo secretos de desarrollo local.
3. Ejecutar `docker compose up --build`.
4. Consultar `http://127.0.0.1:8000/health/live` y `/health/ready`.

Docker Compose es solo para desarrollo local, no una receta de despliegue productivo.

## Documentación
- [Preproducción privada](docs/PREPRODUCCION_PRIVADA.md)
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)

## Prototipo de investigación web

La ruta propuesta `POST /v1/research` exige autenticación y rol autorizado, bloquea consultas con señales de datos personales, registra el evento antes de contactar al proveedor y falla de forma cerrada si la auditoría o la configuración no están disponibles. La interfaz se sirve en `/research-ui/`. Para habilitar búsquedas hay que configurar `BRAVE_SEARCH_API_KEY` como secreto fuera del repositorio. La consulta se transmite al proveedor externo; no usar consultas identificables ni información de consultantes. Esta rama requiere CI y revisión antes de integrarse en `main`.

## Asistencia en sesión en tiempo real

La especificación de interfaz conversacional y los casos QA sintéticos están documentados en:
- [Especificación del asistente en vivo](docs/LIVE_SESSION_ASSISTANT_SPEC.md)
- [Casos QA del modo en vivo](docs/LIVE_SESSION_ASSISTANT_QA.md)

Estos documentos definen el comportamiento esperado, pero no constituyen una interfaz ejecutable ni habilitan el procesamiento remoto de sesiones. La puerta de producción y `CFE_SESSION_PROCESSING_ENABLED=false` permanecen sin cambios.
