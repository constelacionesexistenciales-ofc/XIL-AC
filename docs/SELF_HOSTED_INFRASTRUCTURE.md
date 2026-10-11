# Infraestructura propia para búsqueda, identidad y secretos

**Objetivo:** eliminar la necesidad de una cuenta o clave de un proveedor comercial para los componentes centrales de XIL-AC, manteniendo una opción externa explícita solo si el operador la habilita.

## 1. Búsqueda: adaptación inicial incorporada en esta rama

El adaptador del módulo core/research.py permite elegir:

- RESEARCH_BACKEND=brave: comportamiento actual; necesita BRAVE_SEARCH_API_KEY.
- RESEARCH_BACKEND=searxng: consulta una instancia SearXNG autoalojada; no necesita clave de Brave.

Para probar el despliegue local con Compose:
1. Copiar .env.example a .env.
2. Generar y configurar un valor aleatorio largo para SEARXNG_SECRET; no reutilizar la clave de ejemplo.
3. Configurar RESEARCH_BACKEND=searxng.
4. Ejecutar docker compose -f compose.yaml -f compose.selfhosted-search.yaml up --build.
5. Ejecutar las pruebas automatizadas y una consulta pública no sensible; revisar los registros y los límites de salida antes de cualquier exposición a una red.

La configuración de ejemplo es para desarrollo. Antes de producción, fijar una versión o digest de la imagen, revisar la configuración de motores y formatos JSON, limitar la red, establecer límites de uso y completar pruebas de seguridad. No publicar el puerto de SearXNG: debe ser accesible únicamente por la red interna de Compose.

### Límite importante

SearXNG es un metabuscador: elimina la dependencia de una API comercial única, pero puede consultar motores externos y estos ven las consultas desde la IP del servidor. No equivale a un índice web independiente. El modo realmente independiente requiere desarrollar y mantener un índice propio con fuentes autorizadas, rastreo responsable y actualizaciones periódicas. Un modo sin Internet solo puede buscar documentos previamente descargados o recopilados.

El adaptador valida el esquema, rechaza HTTP fuera de hosts locales/contenedores y bloquea redirecciones fuera del origen configurado. La normalización solo acepta URLs HTTPS como resultados. Esto reduce riesgos; no sustituye pruebas de seguridad completas.

## 2. Identidad: servidor OIDC bajo nuestro control

La API ya valida JWT/OIDC de forma estricta para los entornos de preproducción y producción. No debemos escribir criptografía propia ni aceptar tokens caseros en producción.

Arquitectura propuesta:
- Ejecutar Keycloak autoalojado como proveedor de identidad OIDC.
- Conectar la API mediante OIDC_ISSUER, OIDC_AUDIENCE, OIDC_JWKS_URL y el claim de roles.
- Definir roles mínimos, MFA para administración, política de recuperación, rotación de claves y procedimiento de baja de usuarios.
- Probar tokens reales de un entorno local aislado y verificar emisor, audiencia, firma, expiración y permisos.
- Mantener el token local solo para desarrollo. No convertirlo en una alternativa de producción.

Esto evita depender de un servicio de identidad SaaS, pero la operación segura de Keycloak, su base de datos, actualizaciones y recuperación pasa a ser responsabilidad de XIL-AC.

Documentación oficial: https://www.keycloak.org/securing-apps/oidc-layers

## 3. Secretos: gestor autoalojado

Evaluar OpenBao, un gestor de secretos y claves de código abierto, para reemplazar el gestor SaaS. La API no debe leer secretos generales ni almacenarlos en el repositorio; cada servicio recibe solo los permisos necesarios.

Controles obligatorios:
- almacenamiento persistente cifrado y copias de seguridad verificadas;
- políticas de acceso separadas por servicio;
- auditoría sin registrar valores secretos;
- procedimiento de desbloqueo/recuperación y rotación;
- TLS y credenciales de máquina;
- secretos de bootstrap fuera del repositorio y fuera de imágenes.

No usar el servidor de desarrollo en memoria de OpenBao para proteger secretos reales. El gestor de secretos tampoco elimina la necesidad de proteger el equipo, disco y claves de recuperación.

Documentación oficial: https://openbao.org/docs/what-is-openbao/

## 4. Preproducción sin proveedor de nube

Podemos desplegar una preproducción privada en un equipo o servidor bajo nuestro control usando Docker Compose, PostgreSQL, Keycloak, OpenBao, XIL-AC y copias de seguridad cifradas. Para acceso remoto se requiere una red privada/VPN o un proxy inverso correctamente configurado con TLS.

No hace falta contratar una plataforma de nube para construir y probar esta arquitectura, pero sí disponer de hardware, almacenamiento, conexión y una persona responsable de parches, monitoreo, restauración y seguridad. GitHub puede seguir alojando el código; no es necesario que aloje datos de consultantes.

## 5. Qué se puede cerrar ahora y qué necesita recursos externos

| Elemento | ¿Podemos construirlo? | Dependencia restante |
|---|---|---|
| Adaptador de búsqueda SearXNG | Sí; primera implementación en esta rama | Motores de búsqueda externos, salvo índice propio |
| Índice local de fuentes | Sí, por etapas | Almacenamiento y corpus autorizado; actualización periódica |
| OIDC propio con Keycloak | Sí, mediante integración y configuración | Equipo/servidor y mantenimiento |
| Gestor de secretos OpenBao | Sí, mediante integración y operación segura | Almacenamiento persistente y claves de recuperación |
| Preproducción privada | Sí, con Compose | Equipo o servidor controlado y red segura |
| Producción de sesiones CFE | No debe habilitarse todavía | Motor CFE, evaluación, seguridad, restauración, piloto y aprobación humana |

## 6. Siguiente orden de trabajo

1. CI y pruebas del adaptador SearXNG.
2. Configuración reproducible del servicio SearXNG y verificación de su salida JSON.
3. Integración de Keycloak en un perfil local separado, sin abrir puertos públicos por defecto.
4. Integración de OpenBao con políticas mínimas y pruebas de rotación/recuperación.
5. Preproducción privada con TLS/VPN, PostgreSQL, observabilidad y backup/restore.
6. Pruebas de seguridad, concurrencia, recuperación y verificación de roles.
7. Solo después, aprobación de un piloto limitado. No activar el procesamiento real de sesiones como parte de estos cambios.
