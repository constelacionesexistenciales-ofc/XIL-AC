# Puerta de producción — XIL-AC 0.3.1

## Estado actual
**NO APTO PARA PRODUCCIÓN REAL.** Esta versión añade controles de identidad, auditoría y tamaño de solicitud, pero no conecta el motor CFE ni despliega el servicio.

## Controles construidos
- [x] CI con análisis estático y pruebas automatizadas.
- [x] Pruebas de migración repetida contra PostgreSQL.
- [x] Validación de configuración de Docker Compose.
- [x] Token compartido restringido a desarrollo/pruebas.
- [x] Validación OIDC/JWT preparada para staging/producción.
- [x] Autorización por roles para el endpoint de procesamiento.
- [x] Persistencia de eventos de auditoría sin transcripciones.
- [x] Bloqueo de solicitudes si falla la persistencia de auditoría.
- [x] Límite del cuerpo HTTP de 256 KiB.
- [x] Contenedor no-root y puerto local enlazado a localhost.

## Bloqueos antes de exponer a usuarios
- [ ] Configurar proveedor OIDC real, emisor, audiencia, JWKS y claims de roles; probar tokens reales.
- [ ] Elegir y configurar gestor de secretos administrado.
- [ ] Conectar el motor CFE, proveedores de modelos y sus credenciales con límites, tiempos máximos y manejo seguro de errores.
- [ ] Implementar límites de solicitudes compartidos/distribuidos y controles contra abuso.
- [ ] Añadir métricas, alertas y observabilidad operativa sin datos personales.
- [ ] Probar copias de seguridad, restauración, rollback y migraciones en entorno de prueba.
- [ ] Definir retención, borrado, consentimiento y controles de acceso para datos de consultantes.
- [ ] Ejecutar pruebas de seguridad, fuga entre consultantes, inyección de instrucciones y carga.
- [ ] Configurar protección de rama, revisión obligatoria y permisos mínimos en GitHub.
- [ ] Desplegar en infraestructura real y verificar TLS, red privada, base administrada y recuperación.
- [ ] Obtener aprobación humana explícita antes de habilitar el uso real.

## Limitaciones conocidas
- `POST /v1/process` responde HTTP 501: el motor CFE no está conectado.
- La configuración OIDC está implementada, pero todavía no está probada contra un proveedor real.
- El control de roles usa el claim configurable indicado; la estructura real del token depende del proveedor.
- El esquema y la escritura de auditoría están conectados, pero faltan políticas de retención y una vista administrativa protegida.
- No hay gestor de secretos, limitación distribuida ni despliegue cloud.

## Criterio de aprobación
No declarar producción habilitada hasta que cada bloqueo aplicable tenga evidencia verificable, revisión y aprobación de la persona responsable.
