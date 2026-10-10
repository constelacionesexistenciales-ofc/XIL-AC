# Seguridad y datos

- No guardar claves, tokens, cadenas de conexión ni transcripciones en el repositorio.
- Usar secretos del entorno o un gestor administrado y rotar cualquier credencial expuesta.
- El endpoint de proceso requiere `Authorization: Bearer ...`; sin token configurado falla cerrado.
- No usar transcripciones reales en pruebas ni incluirlas en registros, errores o incidencias.
- Limitar acceso por rol, conservar solo lo necesario y establecer eliminación y recuperación verificables.
- Reportar vulnerabilidades en privado al mantenedor; no publicar datos personales ni secretos en incidencias.
