# Experiencia universal de investigación — interfaz conectada a búsqueda web

Interfaz adaptable para investigaciones generales de XIL-AC/SILAC. Se sirve desde la API en **/research-ui/** y envía consultas a **POST /v1/research**.

## Capacidad disponible

- Envía una consulta al endpoint de búsqueda protegido.
- Pide un token de acceso para la sesión actual de la página; no usa localStorage, cookies ni almacenamiento persistente para ese token.
- Muestra títulos, dominios, descripciones y enlaces HTTPS devueltos por el proveedor.
- Expone errores de autenticación, permisos, privacidad y configuración sin fabricar resultados.
- Muestra un aviso de que la consulta se envía al proveedor externo configurado.
- El esquema visual por disciplina es orientativo y no constituye un análisis automático de evidencia.

## Ejecutar

Abrí **/research-ui/** desde la misma instancia de XIL-AC que sirve la API. No abras **index.html** directamente como archivo local, ya que las solicitudes relativas a la API no funcionarán.

## Configuración del servidor

Configurar **BRAVE_SEARCH_API_KEY** como secreto de entorno y **XILAC_API_TOKEN** solo para desarrollo local. En staging/producción, usar OIDC/JWT conforme a la configuración del backend. El secreto del proveedor nunca debe estar disponible en el navegador.

## Límites

Esta integración recupera resultados web. **No** descarga ni evalúa automáticamente los artículos, no contrasta fuentes de forma semántica y no genera una síntesis mediante un modelo. El proveedor debe estar configurado; si falta la clave, el sistema informa del error en vez de simular una investigación.

No introducir sesiones, datos personales, información clínica de consultantes ni consultas confidenciales. El control de privacidad del servidor es heurístico y no garantiza detectar todo contenido sensible.
