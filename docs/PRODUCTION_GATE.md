# Puerta de producción — XIL-AC 0.4.1

## Decisión actual
**NO APTO PARA PRODUCCIÓN REAL NI PARA SESIONES REALES EN LA API REMOTA.** La versión 0.4.1 endurece la configuración para que el procesamiento de sesiones no pueda habilitarse en staging/producción mientras el motor CFE y la puerta de producción sigan incompletos. No declara un despliegue real.

## Controles incorporados
- [x] Aviso preventivo estándar y compuerta de sesiones cerrada por defecto.
- [x] Detector heurístico de posibles datos sensibles que devuelve categorías sin repetir los valores detectados.
- [x] Pruebas de reglas y del comportamiento de bloqueo de la API.
- [x] Validación OIDC/JWT preparada para staging/producción.
- [x] Autorización por roles, auditoría sin transcripciones y límite del cuerpo HTTP.
- [x] Contenedor no-root y puerto local enlazado a localhost.
- [x] Validación de arranque que impide activar el procesamiento de sesiones en staging/producción antes de conectar y aprobar el motor CFE.
- [x] Digest inmutable de imagen base, escaneo de imagen, generación de SBOM CycloneDX y prueba de salud en CI (PR #62).

## Bloqueos antes de exponer a usuarios
- [ ] Integrar la inspección local previa al envío en el cliente/interfaz. Existe una utilidad CLI inicial (`python -m scripts.privacy_preflight`), pero no está integrada automáticamente con una interfaz ni bloquea a otros clientes.
- [ ] Medir falsos positivos y falsos negativos con un conjunto sintético representativo.
- [ ] Configurar y verificar un proveedor OIDC real y limitar el acceso operativo a la identidad autorizada.
- [ ] Configurar protección efectiva de `main`: exigir PR, checks de CI/SAST/CodeQL, resolver conversaciones y bloquear force-push y borrado. La lectura del repositorio devolvió cero rulesets; la API de protección de rama no fue accesible con la integración actual. No se afirma que la protección esté configurada.
- [ ] Elegir y configurar un gestor de secretos administrado.
- [ ] Conectar y probar el motor CFE y los proveedores de modelos con límites de datos documentados.
- [ ] Validar la ruta de investigación web en una rama candidata: autenticación, detección de datos personales, auditoría previa, fallos del proveedor, límites de solicitudes y pruebas E2E con una clave gestionada como secreto.
- [ ] Verificar límite compartido en PostgreSQL, concurrencia, respuestas 429/503 y ejecución programada de limpieza.
- [ ] Implementar observabilidad, retención y borrado.
- [ ] Probar copias de seguridad, restauración, permisos, aislamiento, seguridad y carga.
- [ ] Verificar controles de red y SSRF/DNS rebinding, incluidos destinos privados y redirecciones.
- [ ] Desplegar en infraestructura real y verificar TLS, base de datos y recuperación.
- [ ] Obtener aprobación humana explícita antes de habilitar el uso real.

## Limitaciones conocidas
- El detector es heurístico; no garantiza detectar todo dato sensible ni determina que el contenido sea seguro.
- La detección dentro de la API ocurre después de que el texto llegó al servidor; no evita la transmisión inicial.
- La CLI de privacidad siempre devuelve bloqueo; no es una autorización ni un mecanismo de anonimización.
- `POST /v1/process` responde HTTP 423 mientras la compuerta está cerrada. El motor no conectado no debe considerarse funcional.
- No hay gestor de secretos ni despliegue cloud verificado.
- Un archivo de configuración de despliegue no prueba que el servicio esté publicado, privado ni protegido correctamente.

## Criterio de aprobación
No declarar producción habilitada hasta que cada bloqueo aplicable tenga evidencia reproducible, revisión y aprobación de la persona responsable. Mantener los datos reales de consultantes fuera de la API remota mientras la puerta permanezca cerrada.


## Indicador de movimiento de sesión (añadido en rama de trabajo)
El indicador usa una habilitación independiente, SESSION_MOVEMENT_ENABLED=false por defecto. Su API persiste solo objetivo contextual, fase, fuente y puntuaciones, sin transcripciones ni texto libre; requiere migración 0003 y rol de facilitador/admin. La interfaz está disponible en /session-movement/ cuando el código se despliega, pero no implica que esté desplegada ni que la Puerta de Producción esté aprobada. Antes de habilitarlo en un entorno compartido: revisar retención/borrado de puntuaciones, ejecutar pruebas y revisión de acceso, verificar OIDC real y aprobar explícitamente el uso de datos. No habilitar el motor CFE ni enviar transcripciones a la API remota por esta funcionalidad.
