# Preproducción privada de XIL-AC

**Objetivo:** preparar un entorno de uso exclusivamente personal, con presupuesto operativo objetivo de USD 0, sin confundir preproducción con producción pública.

## Decisión de arquitectura provisional

- **Repositorio y control de cambios:** GitHub privado. Nunca almacenar secretos, exportaciones de base de datos, audios, transcripciones ni informes de consultantes en GitHub.
- **Identidad:** Auth0 Free mediante OIDC/JWT. Solo la identidad de Alexis debe tener acceso a la operación. La configuración final debe comprobar emisor, audiencia, JWKS, expiración, firma y un claim de roles explícito. No asumir que crear la aplicación de identidad asigna roles automáticamente.
- **API:** servicio Python/FastAPI en Render Free, con `APP_ENV=production` para activar la validación estricta y deshabilitar la documentación interactiva. Render Free es públicamente alcanzable por URL; por eso el endpoint de procesamiento debe permanecer protegido por autenticación y autorización, y los controles se deben probar desde fuera.
- **PostgreSQL:** Supabase Free puede usarse provisionalmente solo para metadatos técnicos mínimos y auditoría, nunca como archivo maestro de transcripciones. El plan gratuito puede pausar proyectos inactivos y no ofrece copias descargables administradas. La base gratuita de Render expira a los 30 días y no ofrece copias de seguridad; no usarla como base duradera.
- **Contenido de sesiones:** no persistir transcripciones ni audio en la base técnica. El motor CFE todavía no está conectado, así que no existe procesamiento real de sesiones desde esta API. No enviar sesiones reales a esta preproducción hasta que el motor, los proveedores de modelos, la política de datos y la puerta de seguridad estén implementados y verificados.

## Límite de seguridad sobre sesiones reales

La intención de trabajar con sesiones reales queda registrada, pero **no se habilita el envío de contenido real todavía**. En la versión actual, `POST /v1/process` responde HTTP 501. Desplegarla no la convierte en un asistente funcional. Además, los planes gratuitos no garantizan disponibilidad ni recuperación de datos.

Antes de aceptar contenido real deben cumplirse como mínimo:

1. Integrar el motor CFE y declarar explícitamente qué datos se envían a cada proveedor de modelos.
2. Confirmar consentimiento y finalidad; minimizar identificadores y no usar nombres reales si no son imprescindibles.
3. Definir retención y eliminación, y una ruta segura para exportar los informes autorizados.
4. Probar autenticación desde un cliente externo: identidad única autorizada, token inválido/expirado rechazado y cualquier otra identidad bloqueada.
5. Confirmar que ningún registro, error, seguimiento o auditoría captura el cuerpo de la sesión.
6. Disponer de una copia de seguridad cifrada fuera del proveedor y probar la restauración. No asumir que un plan gratuito incluye recuperación.
7. Ejecutar pruebas de seguridad, aislamiento, tamaño de solicitud, límites de uso y recuperación; obtener aprobación humana documentada.

Si no podemos satisfacer cualquiera de estos puntos sin costo, la decisión segura es mantener el contenido de las sesiones fuera de la nube y continuar con pruebas ficticias o anonimizadas hasta disponer de una alternativa adecuada.

## Configuración del servicio

El archivo `render.yaml` es una plantilla versionada, no un despliegue. Render, Auth0 y Supabase requieren crear las cuentas y servicios desde sus paneles, vincular GitHub y completar variables secretas. No guardar los valores secretos en el repositorio ni enviarlos por chat.

Variables requeridas para la API en modo estricto:

- `APP_ENV=production`
- `RISK_GATE_ENABLED=true`
- `OIDC_ISSUER`: emisor HTTPS exacto de Auth0.
- `OIDC_AUDIENCE`: audiencia de la API configurada en Auth0.
- `OIDC_JWKS_URL`: URL HTTPS del conjunto de claves públicas.
- `OIDC_ROLES_CLAIM`: claim que contenga roles; debe coincidir con el token real.
- `DATABASE_URL`: cadena de conexión PostgreSQL con TLS y privilegios mínimos.

No cargar `XILAC_API_TOKEN` en la nube: el token compartido está reservado al desarrollo local.

## Riesgos aceptados temporalmente

- Servicio gratuito puede suspenderse, reiniciarse o tardar en arrancar.
- Sin contrato de disponibilidad ni soporte prioritario.
- La URL del servicio puede descubrirse; la privacidad depende de la autenticación y autorización, no de ocultar la URL.
- Las cuotas y las condiciones de los planes gratuitos pueden cambiar.
- La auditoría técnica mínima no sustituye un sistema de copias de seguridad, retención ni cumplimiento legal.

## Criterio de salida de preproducción

No declarar esta preproducción desplegada hasta verificar la ejecución en el proveedor. No declarar habilitado el uso real de sesiones hasta que todos los controles anteriores tengan evidencia reproducible y la API procese realmente el contenido previsto.
