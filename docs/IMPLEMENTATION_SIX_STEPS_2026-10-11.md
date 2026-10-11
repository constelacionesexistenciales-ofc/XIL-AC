# Implementación de los seis pasos de independencia tecnológica

**Fecha:** 2026-10-11  
**Rama:** `feat/technology-independence-v1`  
**Estado:** implementación parcial verificable propuesta mediante PR; no fusionada ni desplegada.

## Paso 1 — Revisar los cambios pendientes
- PR #29 (SearXNG): revisión de diff y metadatos; CI reportada como exitosa. Sigue abierta y sin fusionar. Su servicio aún no se ha probado contra una instancia real.
- PR #27 (enrutador determinista de modelos): el código selecciona identificadores pero no ejecuta inferencia. Sigue abierta y sin fusionar. Requiere CI confirmado y revisión.
- No se fusionan automáticamente ni se considera que sus funciones estén disponibles en `main`.

## Paso 2 — Inventario y cadena de suministro
- Se añade una ruta de CI para generar un SBOM del entorno Python y un informe de auditoría de vulnerabilidades.
- El SBOM de CI describe el entorno que se instaló en ese trabajo; no equivale a un lockfile reproducible ni a un inventario de imágenes de contenedor.
- El primer informe real de pip-audit detectó pytest 8.4.2 vulnerable (CVE-2025-71176 / GHSA-6w46-j5rx-g56g); se elevó el mínimo a pytest 9.0.3. La corrección requiere confirmación de un nuevo informe limpio en CI.
- Sigue pendiente fijar versiones/digests de imágenes y establecer una política de actualización/revisión.

## Paso 3 — Contratos de adaptadores
- Se añade `core/provider_contracts.py` con contratos tipados para investigación e inferencia.
- Es la base para sustituir proveedores sin cambiar políticas del núcleo. La adaptación completa de todos los endpoints y proveedores existentes requiere integración posterior y pruebas de conformidad de cada adaptador.

## Paso 4 — Evaluación de investigación
- Se añade evaluación determinista offline basada en dominios juzgados por humanos: precisión@k, recall@k, URLs no HTTPS/ inválidas y resultados en dominios prohibidos.
- No mide verdad semántica ni calidad de citas por sí sola. Hace falta un conjunto versionado y revisado de casos, fechas, fuentes permitidas y criterios acordados antes de usar resultados comparativos.

## Paso 5 — Inferencia local real
- Se añade un adaptador optativo para el endpoint de chat de Ollama en hosts explícitamente locales/conocidos, con límites de tiempo y tamaño, sin redirecciones y sin fallback remoto.
- No descarga modelos, no garantiza que Ollama esté instalado y no conecta el adaptador al procesamiento CFE. La ejecución real exige instalar Ollama, descargar un modelo con licencia revisada, disponer de hardware y correr benchmarks en ese equipo.
- El adaptador local solo acepta HTTP en los nombres permitidos. No se debe exponer su puerto a Internet.

## Paso 6 — Identidad, secretos, preproducción y recuperación
- Se conserva el requisito de OIDC/HTTPS y bloqueo del procesamiento CFE.
- La documentación de arquitectura para Keycloak/OpenBao/SearXNG no prueba que estén desplegados. La integración operativa requiere servidor, secretos configurados fuera de Git, almacenamiento persistente, políticas, backups y prueba de restauración.
- No se declara staging listo hasta superar Production Gate, pruebas de carga y seguridad, restauración y revisión humana.

## Criterios de aceptación
1. CI verde en el commit exacto de la PR.
2. Ningún secreto real en el repositorio o logs.
3. Pruebas de contratos y fallos cerrados.
4. SBOM y auditoría de dependencias publicados como artefactos de CI.
5. Prueba real de inferencia local en un host designado y reporte de modelo/licencia/recursos.
6. Staging aislado, backup restaurable, observabilidad y autorización humana.
7. Procesamiento de sesiones CFE permanece deshabilitado hasta autorización explícita y validación completa.

## Limitaciones
No se afirma que la plataforma sea autónoma, que los proveedores externos hayan sido eliminados, que el modelo local sea mejor que modelos comerciales, ni que se haya ejecutado un pentest o benchmark real. Los resultados solo se actualizarán con evidencia de ejecución.
