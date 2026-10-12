# Puerta de producción — XIL-AC

## Estado actual
**NO APTO PARA PRODUCCIÓN REAL NI PARA SESIONES REALES EN LA API REMOTA.** La rama de trabajo incorpora un endpoint inicial de búsqueda web protegida y una interfaz conectada. La búsqueda requiere un secreto externo configurado y aún no ofrece síntesis automática ni evaluación completa de fuentes. No hay despliegue productivo verificado.

## Controles incorporados
- [x] Compuerta de procesamiento CFE cerrada por defecto.
- [x] Detector heurístico de posibles datos sensibles.
- [x] Autenticación y autorización por roles en la API.
- [x] Auditoría sin texto de consultas ni transcripciones.
- [x] Límite del cuerpo HTTP, contenedor no-root y publicación local de Docker Compose.
- [x] Adaptador inicial de búsqueda web con timeout, límite de resultados, normalización, deduplicación y URL HTTPS.
- [x] Interfaz de investigación que muestra resultados del proveedor sin inventar resultados cuando falta configuración.
- [x] Pruebas nuevas para autorización, bloqueo por privacidad, auditoría y normalización del proveedor (pendiente de confirmación CI).

## Bloqueos antes de exponer a usuarios
- [ ] Ejecutar y revisar CI completa, análisis estático y CodeQL sobre esta rama.
- [ ] Configurar y probar la clave del proveedor en un gestor de secretos; verificar el flujo de extremo a extremo.
- [ ] Configurar y verificar un proveedor OIDC real y limitar roles al mínimo necesario.
- [x] Límite inicial compartido por PostgreSQL implementado en rama de desarrollo; CI, integración y concurrencia pendientes.
- [ ] Implementar límites de gasto/cuotas del proveedor.
- [ ] Añadir protección CSRF/CORS y política de seguridad de contenido según el modelo de despliegue.
- [x] Añadir una comprobación local de patrones obvios de datos personales en la interfaz, antes de enviar la consulta.
- [ ] Medir falsos positivos y falsos negativos del detector local y del servidor con datos sintéticos representativos.
- [ ] Conectar evaluación de calidad, recuperación autorizada de fuentes y síntesis con citas.
- [ ] Implementar observabilidad sin registrar consultas sensibles ni secretos.
- [ ] Probar copias de seguridad, restauración, aislamiento, seguridad y carga.
- [ ] Desplegar en infraestructura real y verificar TLS, base de datos y recuperación.
- [ ] Obtener aprobación humana explícita antes de habilitar el uso real.

## Limitaciones conocidas
- El detector es heurístico; no garantiza detectar todo dato sensible.
- La consulta se transmite al proveedor web externo después de los controles del servidor. No introducir información personal, sesiones ni contenido confidencial.
- La búsqueda devuelve resultados, pero no verifica la veracidad de sus páginas ni crea una síntesis argumentada.
- Si no existe BRAVE_SEARCH_API_KEY, la búsqueda falla de forma explícita.
- POST /v1/process permanece bloqueado por defecto; el motor CFE no está conectado.
- No hay gestor de secretos ni despliegue cloud verificado.

## Criterio de aprobación
No declarar producción habilitada hasta que cada bloqueo aplicable tenga evidencia verificable, revisión y aprobación de la persona responsable.
