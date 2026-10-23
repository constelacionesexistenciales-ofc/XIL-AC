# AVC — Archivo Vivo de Conversaciones

## Objetivo
Conservar, importar, recuperar y contrastar conversaciones originales de XIL-AC y de fuentes externas autorizadas. AVC es un archivo de evidencia fuente, no una memoria resumida ni un sistema que infiere contenido ausente.

## Contrato de fidelidad
- Preservar el contenido de cada mensaje como texto UTF-8 exacto, sin recortar espacios ni normalizar saltos de línea.
- Preservar el orden mediante `sequence_no`, el rol, identificadores de origen disponibles y fechas originales disponibles.
- No inventar timestamps, roles, mensajes eliminados, regeneraciones ni metadatos que la fuente no entregue.
- Una edición/regeneración se conserva como versión o mensaje separado si la exportación de origen lo representa; nunca reemplaza silenciosamente el original.
- Calcular SHA-256 por mensaje y verificarlo al recuperar.
- Importación idempotente: el mismo lote no duplica registros; una colisión con contenido distinto aborta y requiere revisión.
- Estados de cobertura: `VERIFIED`, `PARTIAL`, `MISSING`, `IMPORT_FAILED`. No declarar integridad completa sin recuento de origen comprobable.

## Alcance y límites de ChatGPT
La aplicación no obtiene por defecto acceso general al historial de la cuenta de ChatGPT. Las conversaciones históricas se incorporan mediante una exportación/importación explícita y autorizada, o un adaptador oficial con permisos verificados. La captura futura automática cubre solo los mensajes que atraviesan la interfaz propia de XIL-AC o una fuente conectada y autorizada. Nunca afirmar “100% del historial” si no existe manifiesto que lo demuestre.

## Modelo de datos
- `avc_conversations`: origen, IDs de origen, título, recuentos esperados/importados, estado de cobertura y metadatos.
- `avc_messages`: ID, conversación, secuencia, rol, contenido exacto, metadatos de origen y hash.
- La tabla de mensajes es append-only por contrato. La protección de producción debe incluir permisos de DB que nieguen UPDATE/DELETE a la cuenta de aplicación, política de retención/borrado aprobada y auditoría de acceso. La eliminación legal/autorizada debe ser una operación separada, registrada y verificable.

## Seguridad
- No usar datos reales de consultantes en repositorios públicos, issues, fixtures, logs o artefactos de CI.
- Mantener el procesamiento CFE de sesiones reales deshabilitado hasta cerrar la Puerta de Producción.
- Cifrado en tránsito y en reposo, autenticación fuerte, RBAC por conversación, auditoría de acceso, backup y restauración probada son requisitos de producción.
- No enviar contenido de sesión a proveedores LLM/web externos por defecto. Cualquier análisis externo requiere revisión de privacidad, base legítima/consentimiento y aprobación explícita.
- Exportaciones e informes públicos deben pasar por desidentificación y revisión humana; cambiar el nombre no basta.

## Puerta de producción (NO-GO hasta evidencias)
1. Migración versionada revisada y reproducible.
2. Tests automatizados para Unicode, saltos de línea, mensajes vacíos, orden, duplicados, conflicto de contenido, idempotencia y hashes alterados.
3. Prueba de importación con manifiesto de origen y detección de importación parcial.
4. RBAC: un usuario no puede recuperar conversaciones ajenas.
5. Restauración de backup en entorno aislado con recuentos y hashes comparados.
6. Fallos DB no confirman éxito ni pierden silenciosamente mensajes.
7. Política de retención, exportación y eliminación aprobada.
8. Captura transaccional desde la interfaz propia, con indicador visible de guardado o error.
9. Revisión de seguridad, dependencias, observabilidad sin texto fuente y aprobación humana.
10. Evidencia de despliegue y pruebas de aceptación antes de habilitar datos reales.

## Integración inicial
`core/avc_archive.py` ofrece funciones de persistencia/recuperación para PostgreSQL. El despliegue debe ejecutar explícitamente `initialize_schema()` como paso controlado de migración, no al arrancar cada petición. La interfaz, el importador oficial de exportaciones ChatGPT, el RBAC por conversación, la política de retención y las pruebas de integración deben completarse antes de producción.

## Reglas adicionales de integridad y conservación

- La secuencia se interpreta como índice de orden cero-basado: para declarar
  `VERIFIED`, los índices recuperados deben coincidir exactamente con
  `0..expected_message_count-1`. Contar mensajes sin comprobar los índices no
  demuestra cobertura.
- `imported_message_count` debe coincidir con el recuento real recuperado.
  Cualquier discrepancia, hueco, duplicado o hash inválido impide declarar la
  conversación completa.
- `manifest_sha256` es un hash canónico versionado de los campos de origen
  persistidos y de los hashes recalculados de los mensajes ordenados. Se
  recalcula al importar y se verifica al recuperar.
- El manifiesto canónico detecta inconsistencias accidentales; no es una firma
  ni protege por sí solo frente a una persona que pueda modificar tanto la base
  como el hash. Si el modelo de amenazas incluye esa capacidad, se necesita una
  firma o un registro de integridad independiente.
- La reimportación no debe modificar `captured_at` de la conversación ya
  existente. La última importación/verificación, si se necesita, debe tener un
  campo separado.
- Las claves foráneas no deben borrar mensajes automáticamente al eliminar una
  conversación. La eliminación debe pasar por el procedimiento autorizado,
  con auditoría y verificación.
- PostgreSQL normaliza los valores `TIMESTAMPTZ` a un instante; si una fuente
  aporta una representación textual de fecha cuya forma exacta deba conservarse,
  se debe almacenar además el valor fuente original como texto.

## Evidencia de validación

La validación de esta PR requiere que CI ejecute Ruff y todas las pruebas de
contrato. Las pruebas unitarias sin PostgreSQL no sustituyen las pruebas de
transacción, conflicto, idempotencia, recuperación y restauración. No declarar
la implementación validada hasta que esas pruebas se ejecuten y sus resultados
queden asociados al commit revisado.
