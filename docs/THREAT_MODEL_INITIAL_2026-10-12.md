# XIL-AC — modelo de amenazas inicial (plan 31–60)

**Estado:** borrador técnico para revisión; no es una certificación de seguridad.  
**Alcance:** API, cliente local, núcleo CFE, proveedores de búsqueda/modelos, almacenamiento, registros y flujos de GitHub Actions.

## Activos a proteger

- Transcripciones, informes y cualquier dato que pueda identificar a consultantes.
- Tokens, claves de proveedores, secretos de despliegue y credenciales de base de datos.
- Integridad de los resultados, referencias de evidencia y trazas `execution_id`.
- Disponibilidad, presupuesto de inferencia/búsqueda y control humano sobre acciones.
- Integridad de las compilaciones, dependencias, artefactos y despliegues.

## Fronteras de confianza

1. Interfaz/dispositivo del facilitador → API.
2. API autenticada → núcleo y controles de privacidad.
3. Núcleo → motor de búsqueda configurado.
4. Núcleo → inferencia local o proveedor remoto.
5. Aplicación → PostgreSQL y sistema de auditoría.
6. Pull requests y dependencias → runners/artefactos de CI.
7. Resultado del modelo o páginas web → lógica de decisión y salida para el facilitador.

## Amenazas y controles requeridos

| Amenaza | Control requerido | Evidencia para cerrar |
|---|---|---|
| SSRF hacia loopback, redes privadas, link-local o metadatos | Lista permitida de orígenes, bloqueo por defecto, control de IP/DNS y redirecciones | Pruebas automatizadas más pruebas de red en entorno aislado |
| DNS rebinding / cambio de destino | Resolver y validar cada conexión/redirección; egress restringido en red | Prueba con servidor DNS controlado; el test unitario no alcanza |
| Envío accidental de datos sensibles | Preflight local antes de cualquier transmisión; consentimiento explícito | Test de integración que compruebe ausencia de petición saliente |
| Filtración por logs, errores o artefactos | Redacción de secretos, no persistir transcripciones, retención limitada | Tests con canarios ficticios y revisión de artefactos |
| Inyección de instrucciones desde páginas/modelos | Tratar fuentes como datos no confiables; separar contenido y políticas; no elevar permisos | Corpus adversarial con decisiones denegadas |
| Abuso de tokens / acceso horizontal | Verificación de emisor, audiencia, expiración, firma y RBAC por recurso | Pruebas positivas y negativas con identidades de prueba |
| Compromiso de acciones/dependencias | SHA completos revisados, lockfile, SBOM, escáneres y actualización controlada | Instalación limpia y CI con resultados archivados |
| Corrupción/pérdida de sesiones | Minimización, cifrado, backup/restauración y control de acceso | Restauración comprobada en entorno aislado |
| Fallo o coste excesivo de proveedor | Timeout, límite de respuesta, cuota, circuit breaker y modo degradado | Pruebas de caída, límite y presupuesto |
| Interpretación excesiva del motor CFE | Hipótesis etiquetadas, evidencia/uncertidumbre visible, aprobación humana | Evaluación con corpus sintético y revisión del facilitador |

## Límites actuales

- La validación de URL configurada reduce configuraciones peligrosas, pero no demuestra protección contra DNS rebinding.
- Las pruebas unitarias no sustituyen aislamiento de red, egress filtering, escaneo dinámico ni revisión de infraestructura.
- El filtro heurístico de privacidad no garantiza detectar todo dato sensible.
- CodeQL, Semgrep, Trivy y CI verdes no demuestran ausencia total de vulnerabilidades.
- Ningún resultado de este documento autoriza procesar sesiones reales.

## Condiciones mínimas de producción

Mantener NO-GO hasta demostrar: control de privacidad antes de la transmisión, autorización real, aislamiento de red, revisión de alertas, dependencias reproducibles, restauración, observabilidad sin contenido sensible, evaluación CFE con datos sintéticos y aprobación humana documentada.
