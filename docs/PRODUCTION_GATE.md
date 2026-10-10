# Puerta de producción — XIL-AC 0.2.0

## Estado actual
**NO APTO PARA PRODUCCIÓN REAL.** Este cambio agrega una base de ingeniería; no equivale a un despliegue, a una auditoría externa ni a un motor CFE terminado.

## Bloqueos antes de exponer a usuarios
- [ ] Ejecutar CI en GitHub y corregir todos los fallos.
- [ ] Configurar secretos en un gestor administrado; nunca guardarlos en Git.
- [ ] Sustituir el token compartido por identidad real, RBAC, rotación y revocación.
- [ ] Conectar readiness con PostgreSQL real y aplicar migraciones con credenciales de mínimo privilegio.
- [ ] Probar copias de seguridad, restauración y rollback.
- [ ] Definir cifrado en tránsito/reposo, retención y eliminación de transcripciones con consentimiento y minimización.
- [ ] Añadir auditoría de accesos, métricas y alertas sin datos personales.
- [ ] Integrar el motor CFE y proveedores con límites, tiempos máximos y manejo seguro de errores.
- [ ] Probar inyección de instrucciones, fuga entre consultantes, abuso, límites y rate limiting.
- [ ] Ejecutar pruebas de carga, seguridad, recuperación y dependencias.
- [ ] Configurar protección de rama, revisión obligatoria y permisos mínimos.
- [ ] Desplegar primero en pruebas y exigir aprobación humana explícita.

## Controles incluidos
- Endpoint de proceso protegido; falla cerrado si falta token.
- Comparación de token en tiempo constante y errores sin detalles internos.
- Identificador único de ejecución; el texto recibido no se registra.
- Nivel de riesgo desconocido bloqueado por defecto.
- CI para análisis estático y pruebas automatizadas.
- Contenedor con usuario sin privilegios.
- Esquema inicial de auditoría PostgreSQL.

## Limitaciones conocidas
- `/health/ready` todavía no verifica PostgreSQL; devuelve `not_checked`.
- `/v1/process` devuelve `not_implemented`: no simula que el motor CFE exista.
- La tabla de auditoría aún no está conectada al flujo de peticiones.
- No hay RBAC completo, gestor de secretos, limitación de solicitudes ni despliegue cloud.
- La migración requiere un procedimiento controlado; no hay ejecutor automático todavía.

## Criterio de aprobación
No declarar producción habilitada hasta contar con evidencia verificable para cada bloqueo aplicable, revisión y aprobación de la persona responsable.
