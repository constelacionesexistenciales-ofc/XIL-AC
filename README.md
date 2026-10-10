# XIL-AC

**Núcleo seguro y auditable para el procesamiento y acompañamiento CFE.**

Estado: **base de ingeniería 0.2.0; todavía no es candidata a producción real**.

## Incluye
- API mínima con protección por token para el endpoint de procesamiento.
- Identificador de ejecución y controles de riesgo con bloqueo por defecto ante niveles desconocidos.
- Conexión PostgreSQL opcional y migración SQL inicial para eventos de auditoría.
- Pruebas automatizadas, análisis estático y flujo de integración continua.
- Imagen de contenedor con usuario sin privilegios y documentación de seguridad.

## Inicio local
1. Instalar Python 3.11 o superior.
2. Instalar dependencias: `pip install -e ".[test]"`.
3. Copiar `.env.example` a `.env` y configurar `XILAC_API_TOKEN` con un valor secreto fuerte.
4. Ejecutar `uvicorn core.api:app --reload`.
5. Consultar `http://127.0.0.1:8000/health/live`.

No subir `.env` ni transcripciones reales al repositorio.

## Estado funcional importante
`POST /v1/process` aún no ejecuta el motor CFE: devuelve `not_implemented` deliberadamente. La base no tiene todavía RBAC completo, gestor de secretos, auditoría conectada, readiness real de PostgreSQL ni despliegue cloud. No debe exponerse a usuarios reales hasta superar la [Puerta de producción](docs/PRODUCTION_GATE.md).

## Documentación
- [Puerta de producción](docs/PRODUCTION_GATE.md)
- [Seguridad y datos](docs/SECURITY.md)
