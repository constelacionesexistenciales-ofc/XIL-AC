# Seguridad y datos

- No guardar claves, tokens, cadenas de conexión ni transcripciones en el repositorio.
- En producción y preproducción remota, usar variables secretas del proveedor y rotar credenciales expuestas.
- El token compartido solo está habilitado en desarrollo/pruebas locales; el modo estricto exige OIDC/JWT y validación de emisor, audiencia, firma, expiración y roles.
- El acceso a procesamiento requiere el rol `facilitator` o `admin`; el rol `auditor` no puede procesar. En la etapa privada, solo Alexis debe recibir el rol operativo.
- El cuerpo HTTP tiene un límite de 256 KiB para reducir el riesgo de agotamiento de memoria.
- Los eventos técnicos guardan identificador de ejecución, tipo, actor y resultado; nunca deben guardar el texto de la sesión.
- La solicitud se bloquea si no se puede persistir el evento de auditoría.
- La URL de una API alojada en un plan gratuito puede ser pública. No confiar en que una dirección difícil de adivinar constituya un control de acceso.
- No enviar sesiones reales a la API de preproducción mientras el motor CFE, la integración real con modelos, las políticas de datos, la recuperación y las pruebas de seguridad sigan pendientes. La API actual responde HTTP 501 en `POST /v1/process`.
- No usar transcripciones identificables en pruebas ni incluirlas en registros, errores o incidencias.
- Antes de habilitar contenido real, verificar consentimiento, minimización, retención y borrado; documentar qué proveedores reciben datos y por cuánto tiempo.
- No usar planes gratuitos sin copias de seguridad como archivo maestro de sesiones. Mantener cualquier copia autorizada cifrada y comprobar restauración.
- La integración OIDC debe probarse con el proveedor real; confirmar el claim de roles en un token real sin copiar ni publicar el token.
- CI ejecuta pruebas unitarias e integración PostgreSQL; CodeQL analiza el código y Dependabot propone actualizaciones.
- Reportar vulnerabilidades en privado al mantenedor; no publicar datos personales ni secretos en incidencias.
