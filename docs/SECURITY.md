# Seguridad y datos

- No guardar claves, tokens, cadenas de conexión ni transcripciones en el repositorio.
- En producción, usar un gestor de secretos administrado y rotar credenciales expuestas.
- El token compartido solo está habilitado en desarrollo/pruebas; staging y producción exigen OIDC/JWT y validación de emisor, audiencia, firma, expiración y roles.
- El acceso a procesamiento requiere el rol `facilitator` o `admin`; el rol `auditor` no puede procesar.
- Los eventos técnicos guardan identificador de ejecución, tipo, actor y resultado; nunca guardan el texto de la sesión.
- La solicitud se bloquea si no se puede persistir el evento de auditoría.
- No usar transcripciones reales en pruebas ni incluirlas en registros, errores o incidencias.
- La integración OIDC debe probarse con el proveedor real antes de habilitar usuarios.
- CI ejecuta pruebas unitarias e integración PostgreSQL; CodeQL analiza el código y Dependabot propone actualizaciones.
- Reportar vulnerabilidades en privado al mantenedor; no publicar datos personales ni secretos en incidencias.
