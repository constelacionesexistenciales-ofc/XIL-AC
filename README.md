# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.2.0; todavía no es candidata a producción real**.

## Incluye
- API mínima con autenticación por token en el endpoint de procesamiento.
- Identificador de ejecución y control de riesgo que bloquea niveles desconocidos.
- Comprobación real de conectividad PostgreSQL en la ruta de disponibilidad.
- Ejecutor de migraciones numeradas e idempotentes.
- Pruebas automatizadas, análisis estático, integración continua y análisis CodeQL.
- Propuestas automáticas de actualización de dependencias.
- Contenedor con usuario sin privilegios y entorno local de PostgreSQL.

## Inicio local con Docker
1. Copiar `.env.example` a `.env`.
2. Reemplazar los valores de ejemplo de `XILAC_API_TOKEN` y `POSTGRES_PASSWORD` por secretos aleatorios largos. Estos valores son solo para desarrollo local.
3. Ejecutar `docker compose up --build`.
4. Consultar `http://127.0.0.1:8000/health/live` y `/health/ready`.
5. Para detener los servicios: `docker compose down`. Los datos de PostgreSQL quedan en el volumen local; para borrarlos explícitamente usar `docker compose down -v`.

El puerto se publica únicamente en `127.0.0.1`, no en todas las interfaces de red.

## Inicio local con Python
1. Instalar Python 3.11 o superior.
2. Instalar dependencias: `pip install -e ".[test]"`.
3. Configurar `DATABASE_URL` y `XILAC_API_TOKEN` en el entorno.
4. Aplicar migraciones: `python scripts/migrate.py`.
5. Ejecutar `uvicorn core.api:app --reload`.

No subir `.env`, credenciales ni transcripciones reales al repositorio.

## Estado funcional importante
`POST /v1/process` responde HTTP 501 porque el motor CFE todavía no está conectado. Esto es intencional: no se simula un procesamiento inexistente. La base no tiene todavía RBAC completo, gestor de secretos, auditoría conectada al flujo, limitación de solicitudes ni despliegue cloud. No debe exponerse a usuarios reales hasta superar la [Puerta de producción](docs/PRODUCTION_GATE.md).

El entorno Docker Compose es para desarrollo local, no una receta de despliegue productivo.

## Documentación
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)
