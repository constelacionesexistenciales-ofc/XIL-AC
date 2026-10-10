# Política operativa CFE / XIL-AC

## Investigación y desarrollo
La investigación, búsqueda web, contraste de fuentes, análisis bibliográfico, evolución del marco CFE, documentación y revisión técnica pueden continuar mediante la interfaz actual de ChatGPT. Esto no significa que exista un motor de búsqueda autónomo ya desplegado en el repositorio; el diseño está en `RESEARCH_ENGINE_PLAN.md`.

## Trabajo de sesiones
Durante esta etapa, el trabajo de sesiones y los informes se realizan únicamente mediante la interfaz actual de ChatGPT con revisión humana. No enviar contenido personal de consultantes a la API remota de preproducción.

## Aviso de privacidad
**Procesamiento temporalmente no disponible.** Esta función no está habilitada en el servicio externo de preproducción. No envíes transcripciones, audios, nombres ni datos identificables a ese servicio. Continuá el trabajo de sesión mediante la interfaz de ChatGPT acordada. La investigación general y el desarrollo metodológico sí pueden continuar.

## Bloqueo y estado
`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. El endpoint remoto responde con un aviso de bloqueo. Esto es una salvaguarda adicional, no una garantía para enviar datos: el cuerpo HTTP puede llegar al servidor antes del rechazo. El motor CFE no está conectado; cambiar la variable no crea el motor ni autoriza el procesamiento.

## Antes de habilitar sesiones en el futuro
- Motor real integrado y probado de extremo a extremo.
- Proveedor de identidad verificado y acceso limitado a Alexis.
- Proveedores de modelos y tratamiento de datos documentados.
- Consentimiento, minimización, retención, borrado y exportación definidos.
- Logs, trazas y auditoría comprobados sin contenido de sesión.
- Base y copias cifradas; restauración probada.
- Pruebas de permisos, aislamiento, seguridad, límites y fallos.
- Aprobación humana explícita de la puerta de producción.

Si no se pueden cumplir estos requisitos, el procesamiento de sesiones permanece fuera del servicio remoto.
