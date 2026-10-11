# Puerta de producción — XIL-AC 0.4.1

## Decisión actual

**NO APTO PARA PRODUCCIÓN REAL NI PARA SESIONES REALES EN LA API REMOTA.** La base tiene controles útiles y una ruta de investigación web integrada, pero faltan validaciones de entorno real y controles operativos. No se declara despliegue cloud ni motor CFE funcional.

## Controles integrados (pendientes de validación en el entorno objetivo)

- [x] Compuerta de procesamiento de sesiones cerrada por defecto.
- [x] Detector heurístico de posibles datos sensibles, sin repetir valores coincidentes.
- [x] Validación OIDC/JWT preparada y autorización por roles.
- [x] Auditoría técnica sin transcripciones y límite del cuerpo HTTP.
- [x] Contenedor no-root y puerto local enlazado a localhost en Compose.
- [x] Búsqueda web protegida con auditoría previa, límite compartido PostgreSQL y respuestas de fallo cerrado.
- [x] Registro de procedencia de fuentes y abstención explícita cuando no existe síntesis.
- [x] Pruebas de navegador añadidas al flujo dedicado.

## Bloqueos pendientes antes de exponer a usuarios

- [ ] Ejecutar y revisar CI en el commit candidato, incluyendo PostgreSQL, Ruff, Bandit y pruebas de navegador.
- [ ] Ejecutar prueba de extremo a extremo con clave válida del proveedor configurada como secreto; no usar claves de prueba para afirmar funcionamiento real.
- [ ] Resolver CodeQL: el último intento consultado falló al publicar resultados porque el análisis de código no está habilitado en este repositorio. Confirmar disponibilidad/plan y configuración; no marcar la seguridad como aprobada mientras siga sin resultado.
- [ ] Integrar la inspección local previa al envío en el cliente. La utilidad CLI existente no bloquea automáticamente a todos los clientes.
- [ ] Evaluar falsos positivos y falsos negativos con un corpus sintético representativo.
- [ ] Configurar y verificar OIDC real y el principio de mínimo privilegio.
- [ ] Elegir y configurar un gestor de secretos administrado en el entorno de ejecución.
- [ ] Completar evaluación de contenido de fuentes, contraste semántico y síntesis con citas verificables antes de llamar al sistema motor autónomo.
- [ ] Establecer límites de gasto, presupuesto y alertas del proveedor.
- [ ] Verificar límite compartido PostgreSQL, concurrencia, respuestas 429/503 y ejecución programada de limpieza.
- [ ] Implementar observabilidad, política de retención y borrado.
- [ ] Probar copias de seguridad, restauración, permisos, aislamiento, seguridad y carga.
- [ ] Desplegar en infraestructura real y verificar TLS, base de datos, recuperación y exposición de red.
- [ ] Obtener aprobación humana explícita antes de habilitar el uso real.

## Limitaciones conocidas

- El detector de privacidad es heurístico; no garantiza detectar todos los datos sensibles ni determina que un contenido sea seguro.
- La detección de privacidad en la API ocurre después de que el texto llegó al servidor; no evita la transmisión inicial.
- Los resultados de búsqueda no son una verificación independiente de las afirmaciones.
- `POST /v1/process` sigue bloqueado mientras el procesamiento CFE no esté conectado y aprobado.
- No hay evidencia verificada de despliegue cloud productivo.
- Una configuración de despliegue o una prueba unitaria no demuestra que el sistema esté publicado, protegido o recuperable en producción.

## Criterio de aprobación

No declarar producción habilitada hasta que cada bloqueo aplicable tenga evidencia reproducible, revisión y aprobación de la persona responsable. Mantener datos reales de consultantes fuera de la API remota mientras la puerta permanezca cerrada.
