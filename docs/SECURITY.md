# Seguridad y datos

- No guardar claves, tokens, cadenas de conexión ni transcripciones en el repositorio.
- Usar secretos de un gestor administrado en producción y rotar cualquier credencial expuesta.
- El token compartido actual es un control transitorio de desarrollo, no sustituye identidad real, permisos por rol, revocación ni rotación.
- El endpoint de proceso falla cerrado si no hay token configurado.
- No usar transcripciones reales en pruebas ni incluirlas en registros, errores o incidencias.
- Limitar acceso por rol, conservar solo lo necesario y establecer eliminación y recuperación verificables.
- La API no debe considerarse lista para procesar datos sensibles mientras el motor CFE, el registro de auditoría y los controles de acceso no estén conectados y probados.
- La integración continua ejecuta análisis estático y pruebas; CodeQL analiza el código y Dependabot propone actualizaciones de dependencias.
- Reportar vulnerabilidades en privado al mantenedor; no publicar datos personales ni secretos en incidencias.
