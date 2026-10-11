# Motor de investigación de XIL-AC — estado e implementación

## Estado actual

**Primera integración de búsqueda web implementada en la rama de trabajo; pendiente de CI, configuración de secreto y prueba de extremo a extremo.** No equivale todavía a un motor de investigación completo: recupera resultados web y muestra sus fuentes, pero no lee artículos completos, no contrasta evidencia de forma automatizada ni redacta una síntesis generada por un modelo.

## Capacidad implementada en esta fase

- **POST /v1/research**: requiere autenticación y rol facilitator o admin.
- Adaptador Brave Search API con clave en **BRAVE_SEARCH_API_KEY**; la clave no se almacena en el repositorio.
- Límite de 1–10 resultados, tiempo máximo de conexión, límite de respuesta, normalización y deduplicación.
- Se aceptan únicamente enlaces HTTPS en los resultados que se muestran como fuentes.
- La consulta no se escribe en la auditoría; se registra el identificador de ejecución, actor, tipo de evento y resultado inicial.
- Si no puede persistirse la auditoría, la búsqueda no se envía al proveedor.
- El detector de contenido sensible actúa antes de enviar la consulta al proveedor externo. Es heurístico y no garantiza detectar todos los casos.
- Interfaz en **/research-ui/**; el token se mantiene solo en memoria de la página y no se guarda en almacenamiento del navegador.
- **POST /v1/process** y el procesamiento de sesiones CFE siguen cerrados por defecto y no se modifican para habilitar esta capacidad.

## Configuración local

1. Configurar **BRAVE_SEARCH_API_KEY** como variable de entorno o secreto del entorno de ejecución. Nunca guardar una clave real en **.env.example**, GitHub o registros.
2. Configurar **XILAC_API_TOKEN** y **DATABASE_URL** según las instrucciones del proyecto.
3. Instalar dependencias de desarrollo y ejecutar las pruebas.
4. Iniciar la API y abrir **/research-ui/** desde el mismo servidor. No abrir el HTML como archivo local: las llamadas relativas a la API requieren el origen del servidor.
5. Introducir un token autorizado. La pregunta se envía al proveedor de búsqueda externo configurado; no introducir sesiones, datos personales ni información confidencial.

Si no existe **BRAVE_SEARCH_API_KEY**, la API falla de forma explícita y no simula resultados.

## Flujo completo previsto

1. Definir la pregunta, alcance, fecha de corte y decisión que la investigación debe apoyar.
2. Diseñar consultas y variantes según la disciplina y el objetivo.
3. Recuperar fuentes primarias, revisiones y perspectivas críticas con adaptadores intercambiables.
4. Normalizar título, autor/organización, URL, fecha de publicación, fecha de consulta, tipo de fuente y fragmento permitido.
5. Evaluar calidad, pertinencia, sesgos y limitaciones.
6. Contrastar convergencias, contradicciones, vacíos e hipótesis alternativas.
7. Sintetizar con un modelo autorizado, enlazando cada afirmación factual a fuentes recuperadas.
8. Separar evidencia, interpretación, hipótesis, incertidumbre y recomendación.
9. Mantener revisión humana y posibilidad de corregir la interpretación.
10. Guardar solo metadatos y resultados expresamente autorizados; no mezclar datos identificables de consultantes con el corpus de investigación.

## Controles y pendientes

- [x] Adaptador de búsqueda real y resultados con enlaces.
- [x] Autenticación y autorización por rol en el endpoint.
- [x] Auditoría previa a la salida al proveedor; sin texto de consulta en el evento.
- [x] Controles de longitud, tiempo, respuesta, deduplicación y HTTPS.
- [x] UI conectada al endpoint y aviso de transmisión a un proveedor externo.
- [ ] Ejecutar CI, pruebas automáticas y revisión de los resultados del proveedor.
- [ ] Configurar el secreto en un entorno controlado y completar una prueba de extremo a extremo.
- [ ] Implementar limitación de solicitudes compartida entre instancias y límites de gasto.
- [ ] Implementar OIDC real y validar los permisos en el entorno de ejecución.
- [ ] Añadir protección CSRF/CORS según el despliegue y una política de seguridad de contenido.
- [ ] Añadir fuentes alternativas y mecanismos de recuperación para caídas del proveedor.
- [ ] Conectar recuperación de páginas autorizadas, evaluación y síntesis con citas.
- [ ] Medir precisión, calidad de recuperación, falsos positivos de privacidad, latencia y costo.
- [ ] Aprobar la puerta de producción antes de habilitar usuarios reales.

No declarar el motor completo ni producción activa hasta verificar cada condición aplicable en el entorno real.
