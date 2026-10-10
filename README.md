# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.4.0; todavía no es candidata a producción real**.

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
La investigación y el desarrollo metodológico pueden continuar mediante la interfaz actual de ChatGPT. El motor autónomo de búsqueda dentro de XIL-AC aún requiere integración. Durante esta etapa, el trabajo de sesiones se realiza por la interfaz de ChatGPT; no enviar información de consultantes a la API remota.

El detector identifica señales explícitas como correos, teléfonos, documentos etiquetados, nombres etiquetados y referencias a salud, violencia, abuso o autolesión. Es heurístico: puede equivocarse y no garantiza detectar todo contenido sensible.

**Importante:** el detector integrado en la API se ejecuta después de que el cuerpo de la solicitud llegó al servidor. Es una barrera adicional, no un filtro previo al envío. Hace falta una interfaz local que inspeccione el contenido antes de transmitirlo; hasta entonces, no envíes contenido de consultantes a la API remota.

`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. `POST /v1/process` devuelve HTTP 423 cuando detecta señales sensibles o mientras el procesamiento esté deshabilitado. El motor CFE sigue sin estar conectado y no hay despliegue cloud verificado. Consultar [Política operativa CFE](docs/CFE_OPERATING_POLICY.md), [plan del motor de investigación](docs/RESEARCH_ENGINE_PLAN.md) y [Puerta de producción](docs/PRODUCTION_GATE.md).

## Inicio local con Docker
1. Copiar `.env.example` a `.env`.
2. Reemplazar `XILAC_API_TOKEN` y `POSTGRES_PASSWORD` por valores aleatorios largos. Son solo secretos de desarrollo local.
3. Ejecutar `docker compose up --build`.
4. Consultar `http://127.0.0.1:8000/health/live` y `/health/ready`.

Docker Compose es solo para desarrollo local, no una receta de despliegue productivo.

## Revisión local de privacidad
Se está preparando un prototipo de revisión previa al envío en `local-privacy-review/index.html`. Es una herramienta local sin función de envío ni llamadas de red; ayuda a evaluar reglas, pero no es todavía un ejecutable instalable ni una llave obligatoria. La arquitectura futura está descrita en [Puerta Local](docs/LOCAL_GATEWAY_ARCHITECTURE.md) y el uso del prototipo en [Revisión local](docs/LOCAL_PRIVACY_REVIEW.md). No usarlo como garantía de anonimización ni habilitar el procesamiento remoto de sesiones.

## Documentación
- [Preproducción privada](docs/PREPRODUCCION_PRIVADA.md)
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)
