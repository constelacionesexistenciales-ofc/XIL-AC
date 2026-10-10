# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.2.0; todavía no es candidata a producción real**.

## Incluye
- API mínima con autenticación por token en el endpoint de procesamiento.
- Identificador de ejecución y control de riesgo que bloquea niveles desconocidos.
- Comprobación real de conectividad PostgreSQL en la ruta de disponibilidad.
- Ejecutor de migraciones numeradas e idempotentes.
- Pruebas automatizadas, análisis estático e integración continua.
- Imagen de contenedor con usuario sin privilegios.

## Inicio local
1. Instalar Python 3.11 o superior.
2. Instalar dependencias: `pip install -e ".[test]"`.
3. Configurar `DATABASE_URL` para una instancia PostgreSQL y `XILAC_API_TOKEN` para la API.
4. Aplicar las migraciones: `python scripts/migrate.py`.
5. Ejecutar `uvicorn core.api:app --reload`.
6. Consultar `http://127.0.0.1:8000/health/live` y `/health/ready`.

No subir `.env`, credenciales ni transcripciones reales al repositorio.

## Estado funcional importante
`POST /v1/process` responde HTTP 501 porque el motor CFE todavía no está conectado. Esto es intencional: no se simula un procesamiento inexistente. La base no tiene todavía RBAC completo, gestor de secretos, auditoría conectada al flujo, limitación de solicitudes ni despliegue cloud. No debe exponerse a usuarios reales hasta superar la [Puerta de producción](docs/PRODUCTION_GATE.md).

## Documentación
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)
