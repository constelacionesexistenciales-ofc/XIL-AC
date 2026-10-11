# XIL-AC — lista de control de Puerta de Producción
**Estado inicial:** NO APROBADA. No usar esta lista como certificación; cada casilla exige evidencia enlazada.

## Ingeniería y cadena de suministro
- [ ] CI verde en el SHA exacto que se pretende desplegar.
- [ ] Semgrep ejecutado; informe revisado; falsos positivos documentados.
- [ ] Trivy ejecutado; informe revisado; no solo estado del trabajo.
- [ ] CodeQL o alternativa documentada, ejecutada y revisada.
- [ ] SBOM de aplicación e imágenes de contenedor archivados.
- [ ] Dependencias bloqueadas con hashes; acciones de GitHub fijadas por SHA.
- [ ] Vulnerabilidades críticas/altas resueltas o aceptadas formalmente con vencimiento.

## Identidad, autorización y secretos
- [ ] OIDC/JWT probado contra proveedor real del entorno.
- [ ] Matriz RBAC probada para permitir y denegar cada rol.
- [ ] Secretos fuera del código, logs, artefactos y variables públicas.
- [ ] Rotación y revocación de credenciales probadas.
- [ ] Migraciones y permisos de base de datos probados.

## Privacidad y red
- [ ] Filtro local previo al envío activo y probado.
- [ ] SSRF, DNS rebinding, redirecciones, resolución y rangos privados probados.
- [ ] Límites de cuerpo, respuesta, concurrencia y tiempo probados.
- [ ] Transcripciones y datos identificables ausentes de logs.
- [ ] Retención, borrado, consentimiento y exportación documentados.

## Resiliencia y operación
- [ ] Copia de seguridad restaurada en prueba.
- [ ] Observabilidad y alertas probadas sin datos sensibles.
- [ ] Pruebas de carga y límites documentadas.
- [ ] Fallos de proveedor/base de datos llevan a modo seguro.
- [ ] Procedimiento de incidente y reversión ensayado.

## CFE y control humano
- [ ] Procesamiento sigue deshabilitado por defecto.
- [ ] Casos de evaluación en español revisados por personas competentes.
- [ ] El sistema separa hechos, hipótesis, contradicciones e incertidumbre.
- [ ] No diagnostica ni sustituye el criterio del facilitador.
- [ ] Human Gate, anulación y apagado de emergencia probados.
- [ ] Aprobación explícita del responsable antes de activar producción.

**Regla de decisión:** cualquier casilla crítica sin evidencia mantiene la puerta cerrada.
