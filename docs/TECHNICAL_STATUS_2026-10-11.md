# Informe técnico consolidado XIL-AC — 2026-10-11

## Alcance y criterio
Este informe distingue entre cambios fusionados, verificaciones observadas y capacidades aún no implementadas. Una ejecución de CI solo valida el SHA indicado; no certifica el producto completo ni producción.

## Integraciones y evidencia verificable

### PR #16 — auditoría maestra
- Estado: fusionada en `main`.
- Commit: `4fa0ec320b96c06407b96a21914a6e207f00839f`.
- CI en ese SHA: satisfactorio: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38112692175

### PR #12 — puerta de preparación para producción
- Estado: fusionada en `main`.
- Commit de integración: `577536e8c0dc1c8342f0d0b1b8a1b273635ad07e`.
- Aporta auditoría de preparación, barrera de arranque que impide activar el procesamiento de sesiones en staging/producción mientras el motor CFE no esté implementado, utilidad local de preinspección y pruebas de regresión.
- CI posterior a esta integración debe confirmarse por su ejecución específica: https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38113158685
- CodeQL figura omitido por la configuración para el repositorio privado; no equivale a análisis aprobado.

## Solicitudes todavía abiertas
- PR #11 — puerta local de privacidad para Windows. La ejecución histórica de pytest tuvo 27 pruebas aprobadas y una falla por una expectativa textual obsoleta en `tests/test_api.py`; la corrección de esa expectativa se integró en #16. Sin embargo, #11 presenta conflicto con el `main` actualizado y debe rebasarse/resolverse y volver a probarse antes de integrar.
- PR #13 — interfaz de investigación y búsqueda web protegida. Pruebas principales históricas aprobadas; CodeQL histórico falló/está condicionado por el entorno privado. Presenta conflicto con el `main` actualizado y necesita actualización, revisión y CI nuevo.
- PR #14 — evaluación tecnológica y pruebas de navegador. Sus pruebas de navegador históricas fueron satisfactorias. Está apilada sobre #13; no es integración independiente hasta estabilizar #13.
- PR #15 — límites compartidos de solicitudes y backlog de producción. Las pruebas históricas de CI y navegador fueron satisfactorias. Está apilada sobre #14; requiere validar migraciones, comportamiento concurrente, fallo cerrado y CI tras integrar toda la cadena.

## Estado de capacidad

| Área | Estado real | Evidencia / brecha |
|---|---|---|
| CI base | Parcialmente verificada | #16 aprobada; validar el commit tras #12 y cada integración posterior |
| Privacidad local | Prototipos separados | CLI y propuesta de escritorio; aún no hay una puerta obligatoria común a todos los clientes |
| Procesamiento de sesiones CFE | Deshabilitado | Motor real no conectado; no habilitar |
| Investigación web | Parcial / propuesta en PR | Adaptador inicial de búsqueda no equivale a un motor de investigación autónomo |
| Investigación trazable | Pendiente | Falta registro de evidencias por afirmación, contraste, contradicciones, incertidumbre y evaluación de calidad |
| Autonomía de ejecución | Pendiente | Falta orquestación integral con permisos, límites, checkpoints, recuperación y verificación independiente |
| Seguridad de producción | No aprobada | OIDC real, secretos administrados, observabilidad, pruebas de seguridad/carga y recuperación no verificados integralmente |
| Despliegue y piloto | No ejecutados/verificados | No existe evidencia de un despliegue productivo aprobado ni de piloto con protocolo de aceptación |

## Bloqueos para cerrar el proceso
1. Confirmar CI en el commit de `main` posterior a #12.
2. Resolver conflictos y actualizar #11 y #13 contra `main`; ejecutar CI nuevo en los SHA resultantes.
3. Integrar #14 y #15 después de #13, con pruebas después de cada integración.
4. Configurar una clave de búsqueda como secreto fuera del repositorio y ejecutar una prueba de extremo a extremo; no inventar credenciales ni guardarlas en Git.
5. Construir y evaluar el motor de investigación con corpus de referencia, citas por afirmación, contraste y abstención ante evidencia insuficiente.
6. Implementar y probar la orquestación de tareas con límites de permisos, gasto, tiempo, checkpoints, registro y verificación independiente.
7. Completar identidad, secretos, observabilidad, migraciones, pruebas de seguridad/carga, backups y restauración en una preproducción privada.
8. Ejecutar piloto solo con datos sintéticos inicialmente, criterios de salida, supervisión humana y aprobación expresa.

## Decisión
**XIL-AC no está listo para producción ni para procesar sesiones reales de consultantes.** Mantener `POST /v1/process` bloqueado. Este informe no declara completados el motor de investigación, la autonomía total ni el piloto; establece la situación técnica y las evidencias necesarias para continuar.
