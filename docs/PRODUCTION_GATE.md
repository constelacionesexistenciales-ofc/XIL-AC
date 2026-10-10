# Puerta de producción — XIL-AC 0.4.0

## Estado actual
**NO APTO PARA PRODUCCIÓN REAL NI PARA SESIONES REALES EN LA API REMOTA.** La versión 0.4.0 incorpora detección heurística de posibles datos sensibles como defensa adicional. No conecta el motor CFE ni despliega el servicio.

## Controles incorporados
- [x] Aviso preventivo estándar y compuerta de sesiones cerrada por defecto.
- [x] Detector heurístico de datos sensibles que devuelve categorías sin repetir los valores detectados.
- [x] Pruebas de reglas y del comportamiento de bloqueo de la API.
- [x] Validación OIDC/JWT preparada para staging/producción.
- [x] Autorización por roles, auditoría sin transcripciones y límite del cuerpo HTTP.
- [x] Contenedor no-root y puerto local enlazado a localhost.

## Bloqueos antes de exponer a usuarios
- [ ] Crear una interfaz local que ejecute el detector antes de transmitir contenido.
- [ ] Medir falsos positivos y falsos negativos con un conjunto de pruebas sintético representativo.
- [ ] Configurar y verificar un proveedor OIDC real y limitar el acceso a Alexis.
- [ ] Elegir y configurar gestor de secretos administrado.
- [ ] Conectar y probar el motor CFE y los proveedores de modelos.
- [ ] Implementar límites de solicitudes, observabilidad, retención y borrado.
- [ ] Probar copias de seguridad, restauración, permisos, aislamiento, seguridad y carga.
- [ ] Desplegar en infraestructura real y verificar TLS, base de datos y recuperación.
- [ ] Obtener aprobación humana explícita antes de habilitar el uso real.

## Limitaciones conocidas
- El detector es heurístico; no garantiza detectar todo dato sensible ni determina que el contenido sea seguro.
- La detección que corre dentro de la API ocurre después de que el texto llegó al servidor; no evita la transmisión inicial.
- `POST /v1/process` responde HTTP 423 mientras la compuerta está cerrada. Si se abre manualmente, el motor aún no conectado produce HTTP 501.
- No hay gestor de secretos ni despliegue cloud verificado.

## Criterio de aprobación
No declarar producción habilitada hasta que cada bloqueo aplicable tenga evidencia verificable, revisión y aprobación de la persona responsable.
