# XIL-AC

**Núcleo seguro y auditable para investigación y acompañamiento CFE.**

Estado: **integración inicial de búsqueda web en revisión; todavía no es candidata a producción real**.

## Incluye

- API con autenticación, roles y validación OIDC/JWT estricta en staging/producción.
- Límite de 256 KiB para el cuerpo HTTP.
- Identificador de ejecución, control de riesgo y auditoría técnica sin consultas ni transcripciones.
- Detector heurístico de posibles datos sensibles.
- Endpoint protegido **POST /v1/research** con adaptador de búsqueda web, límite de resultados, tiempo de espera y validación de URL HTTPS.
- Interfaz visual en **/research-ui/** que muestra fuentes reales devueltas por el proveedor configurado.
- Pruebas automatizadas, integración continua con PostgreSQL, análisis estático, CodeQL y Dependabot.
- Docker Compose local y contenedor no-root.

## Investigación web

La búsqueda usa Brave Search API cuando se configura **BRAVE_SEARCH_API_KEY** como secreto del entorno. No guardes una clave real en GitHub ni en archivos versionados. La consulta se envía al proveedor externo, por lo que la interfaz avisa que no deben introducirse datos personales, información confidencial ni sesiones de consultantes.

Para utilizarla en local:
1. Copiar **.env.example** a **.env**.
2. Reemplazar los secretos de desarrollo por valores aleatorios y configurar **BRAVE_SEARCH_API_KEY** en el entorno local.
3. Iniciar la API y abrir **http://127.0.0.1:8000/research-ui/**.
4. Introducir un token autorizado.

Si falta la clave del proveedor, la búsqueda falla de forma explícita. Esta fase recupera enlaces y descripciones; **no** genera todavía una síntesis automática, no evalúa completamente la calidad de las fuentes y no debe considerarse un motor de investigación completo.

## Privacidad y modos de trabajo

**CFE_SESSION_PROCESSING_ENABLED=false** por defecto. **POST /v1/process** permanece bloqueado y el motor CFE no está conectado. No enviar transcripciones ni datos identificables de consultantes a la API remota. El detector es heurístico y no garantiza detectar todo contenido sensible.

La búsqueda requiere completar la configuración de secretos, OIDC real, límites de solicitudes compartidos, observabilidad, pruebas de seguridad y la puerta de producción antes de exponerse a usuarios.

## Inicio local con Docker

1. Copiar **.env.example** a **.env**.
2. Reemplazar **XILAC_API_TOKEN** y **POSTGRES_PASSWORD** por valores aleatorios largos.
3. Configurar **BRAVE_SEARCH_API_KEY** fuera del repositorio.
4. Ejecutar **docker compose up --build**.
5. Consultar **http://127.0.0.1:8000/health/live**, **/health/ready** y abrir **/research-ui/**.

Docker Compose es solo para desarrollo local, no una receta de despliegue productivo.

## Documentación

- [Plan del motor de investigación](docs/RESEARCH_ENGINE_PLAN.md)
- [Seguridad y datos](docs/SECURITY.md)
- [Puerta de producción](docs/PRODUCTION_GATE.md)\n- [Listado priorizado de pendientes de producción](docs/PRODUCTION_BACKLOG.md)
- [Preproducción privada](docs/PREPRODUCCION_PRIVADA.md)
