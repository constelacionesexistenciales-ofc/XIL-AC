# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.3.0; todavía no es candidata a producción real**.

## Incluye
- API mínima con roles, validación OIDC/JWT en staging/producción y token local solo para desarrollo.
- Validación estricta de configuración y uso obligatorio de HTTPS para el proveedor de identidad.
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
En desarrollo, el token compartido local asigna roles de prueba y solo sirve para trabajar en el equipo local. En staging/producción se deshabilita esa vía y se exige un proveedor OIDC con:
- `OIDC_ISSUER`: emisor exacto del token.
- `OIDC_AUDIENCE`: audiencia de la API.
- `OIDC_JWKS_URL`: URL HTTPS de claves públicas.
- `OIDC_ROLES_CLAIM`: claim que contiene una lista de roles; por defecto `roles`.

Los roles `facilitator` o `admin` permiten solicitar procesamiento; el rol `auditor` no lo permite. La integración debe validarse contra el proveedor real antes de producción.

## Estado funcional importante
`POST /v1/process` responde HTTP 501 porque el motor CFE todavía no está conectado. La API registra un evento técnico mínimo sin almacenar el texto recibido y bloquea la solicitud si la auditoría no puede guardarse. No están conectados el motor CFE, un gestor de secretos, limitación distribuida de solicitudes ni despliegue cloud. No procesar transcripciones reales hasta superar la [Puerta de producción](docs/PRODUCTION_GATE.md).

Docker Compose es solo para desarrollo local, no una receta de despliegue productivo.

## Documentación
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)
