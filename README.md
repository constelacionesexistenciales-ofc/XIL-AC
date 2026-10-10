# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.3.1; todavía no es candidata a producción real**.

## Incluye
- API mínima con roles, validación OIDC/JWT en modo estricto y token local solo para desarrollo.
- Validación estricta de configuración y uso obligatorio de HTTPS para el proveedor de identidad.
- Límite de 256 KiB para el cuerpo HTTP antes de analizar la solicitud.
- Identificador de ejecución y control de riesgo que bloquea niveles desconocidos.
- Comprobación real de PostgreSQL, migraciones numeradas e idempotentes y auditoría técnica sin transcripciones.
- Pruebas automatizadas, integración continua con PostgreSQL, análisis estático, CodeQL y Dependabot.
- Docker Compose local con puerto publicado solo en localhost y contenedor no-root.

## Inicio local con Docker
1. Copiar `.env.example` a `.env`.
2. Reemplazar `XILAC_API_TOKEN` y `POSTGRES_PASSWORD` por valores aleatorios largos. Son solo secretos de desarrollo local.
3. Ejecutar `docker compose up --build`.
4. Consultar `http://127.0.0.1:8000/health/live` y `/health/ready`.

## Identidad y roles
En desarrollo, el token compartido local asigna roles de prueba y solo sirve para trabajar en el equipo local. En modo estricto se deshabilita esa vía y se exige un proveedor OIDC con:
- `OIDC_ISSUER`: emisor exacto del token.
- `OIDC_AUDIENCE`: audiencia de la API.
- `OIDC_JWKS_URL`: URL HTTPS de claves públicas.
- `OIDC_ROLES_CLAIM`: claim que contiene una lista de roles; por defecto `roles`.

Los roles `facilitator` o `admin` permiten solicitar procesamiento; el rol `auditor` no lo permite. La integración debe validarse contra el proveedor real antes de habilitar usuarios.

## Modos de trabajo y privacidad
La investigación y el desarrollo metodológico pueden continuar mediante la interfaz actual de ChatGPT. El motor autónomo de búsqueda dentro de XIL-AC aún requiere integración. Durante esta etapa, el trabajo de sesiones se realiza por la interfaz de ChatGPT; no enviar información de consultantes a la API remota.

`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. `POST /v1/process` devuelve HTTP 423 con un aviso de bloqueo mientras el procesamiento esté deshabilitado. El cuerpo de una solicitud puede llegar al servidor antes del rechazo, así que no enviar contenido sensible al servicio remoto. El motor CFE sigue sin estar conectado; cuando se habilite la compuerta, la respuesta será HTTP 501 hasta que el motor exista. No están conectados un gestor de secretos, limitación distribuida ni despliegue cloud. Consultar [Política operativa CFE](docs/CFE_OPERATING_POLICY.md), [plan del motor de investigación](docs/RESEARCH_ENGINE_PLAN.md) y [Puerta de producción](docs/PRODUCTION_GATE.md).

Docker Compose es solo para desarrollo local, no una receta de despliegue productivo.

## Documentación
- [Preproducción privada](docs/PREPRODUCCION_PRIVADA.md)
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)
