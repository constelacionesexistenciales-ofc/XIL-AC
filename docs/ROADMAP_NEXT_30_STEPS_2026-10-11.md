# Próximos 30 pasos de XIL-AC — 2026-10-11

**Tipo de documento:** hoja de ruta, no evidencia de implementación.
**Regla de avance:** cada cambio debe superar CI y revisión antes de integrarse; si falla, se corrige antes de continuar.
**Estado actualizado 2026-10-11:** PR #19, #20, #22, #23 y #24 están integradas. Las CI de rama de #19–#24 fueron aprobadas; las CI posteriores de main están confirmadas para #19–#23, y la de #24 estaba en curso en la última consulta. El procesamiento de sesiones CFE permanece bloqueado.

## A. Cerrar las integraciones (16–20)

16. **[COMPLETADO] Cerrar PR #20:** integrada como recuperación inicial de fuentes y registro de evidencias.
   - Evidencia: [CI de PR #20](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38144825234); [CI de main posterior](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38144929140).
17. **[COMPLETADO EN CI] Verificar el endpoint de investigación:** autenticación, roles, privacidad, auditoría previa, proveedor y fallos están cubiertos por pruebas HTTP; `/v1/process` sigue bloqueado.
   - Evidencia: [CI de main posterior a #20](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38144929140). La búsqueda con clave real sigue pendiente.
18. **[COMPLETADO] Integrar #14 mediante PR #22:** evaluación tecnológica y pruebas de navegador Chromium incorporadas.
   - Evidencia: [CI](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145095662) · [Chromium](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145095578).
19. **[COMPLETADO] Integrar #15 mediante PR #23:** límite compartido en PostgreSQL, migración, respuestas 429/503 y limpiador por lotes.
   - Evidencia: [CI de integración](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145508597) · [CI de main posterior](https://github.com/constelacionesexistenciales-ofc/XIL-AC/actions/runs/38145583477).
20. **[COMPLETADO EN CI] Validar el límite en PostgreSQL de prueba:** persistencia, ventanas, concurrencia y fallo cerrado están cubiertos por las pruebas automatizadas.
   - Pendiente operacional: comprobarlo entre instancias desplegadas y programar/monitorizar la limpieza en el entorno real.

## B. Convertir la búsqueda en investigación trazable (21–28)

21. **Configurar el secreto del proveedor en el entorno autorizado.**
   - Aceptación: prueba sin imprimir ni registrar la clave; no guardar secretos en el repositorio.
22. **Ejecutar una prueba real de proveedor con consulta pública no sensible.**
   - Aceptación: timeout, error 429, clave ausente, respuesta inválida y caída del proveedor cubiertos; registrar solo metadatos técnicos.
23. **Normalizar fuentes:** URL HTTPS, título, dominio/editor, fecha disponible, fecha de recuperación y deduplicación.
   - Aceptación: descartar URL inseguras, registros malformados y duplicados.
24. **Conectar cada resultado al registro de evidencias.**
   - Aceptación: cada fuente tiene ID estable dentro de la ejecución y la respuesta incluye limitaciones.
25. **Implementar extracción de afirmaciones como módulo separado.**
   - Aceptación: cada afirmación debe enlazar evidencia o convertirse en abstención explícita; no inventar citas.
26. **Agregar contraste entre fuentes independientes.**
   - Aceptación: registrar coincidencias, contradicciones y fuentes que discrepan; no asumir que dos páginas equivalen a dos fuentes independientes.
27. **Definir evaluación de calidad y confianza calibrada.**
   - Aceptación: puntuaciones justificadas y validadas contra un corpus; no presentar una cifra heurística como probabilidad comprobada.
28. **Completar el informe de investigación en la interfaz.**
   - Aceptación: mostrar fuentes, fechas, citas por afirmación, contradicciones, incertidumbre y qué no se pudo concluir.

## C. Autonomía controlada y seguridad (29–36)

29. **Construir un corpus sintético de evaluación.**
   - Aceptación: consultas de varias disciplinas, datos personales ficticios, consultas ambiguas, fuentes contradictorias y evidencia insuficiente.
30. **Definir métricas reproducibles.**
   - Aceptación: precisión de citas, afirmaciones sin soporte, abstención adecuada, detección de contradicciones, latencia y coste.
31. **Defenderse de instrucciones maliciosas en fuentes externas.**
   - Aceptación: el contenido recuperado se trata como dato no confiable, nunca como instrucción para cambiar permisos o revelar secretos.
32. **Endurecer validación de entradas y límites de recursos.**
   - Aceptación: límites de tamaño, cantidad de resultados, tiempo, redirecciones y salida estructurada; pruebas de casos límite.
33. **Completar TRACE y eventos de resultado.**
   - Aceptación: `execution_id` conecta solicitud, proveedor, evidencias y decisión sin almacenar consulta sensible ni secretos en logs.
34. **Crear el planificador de tareas con estados explícitos.**
   - Aceptación: plan, ejecución, checkpoint, cancelación, error, recuperación y finalización; nada se ejecuta fuera de la lista autorizada.
35. **Integrar permisos mínimos y Human Gate.**
   - Aceptación: acciones externas, gasto por encima del umbral y cambios de estado sensibles requieren autorización; cancelación efectiva.
36. **Añadir presupuestos, cuotas y recuperación segura.**
   - Aceptación: límites por usuario/tarea, reintentos acotados, circuit breaker, idempotencia y ausencia de reintentos infinitos.

## D. Preparar y verificar preproducción (37–41)

37. **Configurar identidad real OIDC/JWT en un entorno de prueba aislado.**
   - Aceptación: emisor, audiencia, firma, expiración, roles y revocación comprobados con el proveedor elegido.
38. **Conectar un gestor de secretos y rotación.**
   - Aceptación: claves fuera del repositorio, permisos mínimos y procedimiento de rotación probado.
39. **Completar infraestructura de base de datos y migraciones.**
   - Aceptación: PostgreSQL administrado o equivalente, migraciones repetibles, permisos mínimos, backups y restauración demostrada.
40. **Agregar observabilidad operativa.**
   - Aceptación: métricas, trazas, alertas, estado de proveedores y costes; logs sin datos de consultantes ni tokens.
41. **Ejecutar pruebas de seguridad, carga y recuperación.**
   - Aceptación: resultados registrados, fallos críticos resueltos, límites bajo concurrencia y restauración ensayada.

## E. Puerta de aceptación y piloto (42–45)

42. **Desplegar en preproducción privada.**
   - Aceptación: TLS, autenticación, red, base, secretos y reversión verificados; no basta con que exista un archivo de despliegue.
43. **Ejecutar pruebas de extremo a extremo con datos sintéticos.**
   - Aceptación: camino exitoso y fallos de proveedor, base, permisos, auditoría y cancelación comprobados.
44. **Aprobar protocolo de piloto supervisado.**
   - Aceptación: objetivos, responsables, límites, criterios de interrupción, datos permitidos, consentimiento y tratamiento de incidentes documentados.
45. **Ejecutar piloto limitado y decidir continuar o detener.**
   - Aceptación: autorización humana expresa, supervisión activa, criterios cuantitativos cumplidos y revisión posterior. Cualquier uso con sesiones reales requiere una autorización separada y una puerta de privacidad específica.

## Bloqueos que no se pueden resolver solo con código

- Credenciales y autorización del proveedor de búsqueda.
- Configuración del proveedor OIDC y del gestor de secretos.
- Cuenta y recursos de infraestructura de producción.
- Aprobación del responsable para cualquier piloto externo o uso de datos reales.

## Regla de publicación de estado

Informar por separado: **propuesto**, **implementado en rama**, **CI aprobada**, **integrado en main**, **validado en entorno**, y **aprobado para uso**. Ningún estado implica automáticamente el siguiente.
