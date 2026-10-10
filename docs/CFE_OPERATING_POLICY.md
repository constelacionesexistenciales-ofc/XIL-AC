# Política operativa CFE / XIL-AC

## Investigación y desarrollo
La investigación, búsqueda web, contraste de fuentes, análisis bibliográfico, evolución del marco CFE, documentación y revisión técnica pueden continuar mediante la interfaz actual de ChatGPT. Esto no significa que exista un motor de búsqueda autónomo ya desplegado en el repositorio; el diseño está en `RESEARCH_ENGINE_PLAN.md`.

## Trabajo de sesiones
Durante esta etapa, el trabajo de sesiones y los informes se realizan únicamente mediante la interfaz actual de ChatGPT con revisión humana. No enviar contenido personal de consultantes a la API remota de preproducción.

## Recordatorio preventivo de privacidad
Como Alexis es el único usuario operativo en esta etapa, se utiliza un aviso claro como recordatorio; no se incorporan por ahora flujos complejos de aprobación ni administración de múltiples usuarios.

**Mensaje estándar:**

> La información recibida contiene o podría contener material sensible; no recomendamos seguir con esta operación. En esta etapa, no envíes transcripciones, audios ni datos identificables a la API remota. Continuá el trabajo de sesiones mediante la interfaz de ChatGPT acordada. La investigación general y el desarrollo metodológico pueden continuar por esa interfaz.

El aviso es preventivo y no implica que exista un detector automático fiable de información sensible. Si el contenido parece incluir datos personales o información confidencial, se muestra el recordatorio y se evita enviarlo al servicio remoto. El trabajo puede continuar por la interfaz de ChatGPT acordada, con criterio humano y evitando datos identificables innecesarios.

## Bloqueo y estado
`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. El endpoint remoto responde con el aviso de bloqueo. Esto es una salvaguarda adicional, no una garantía para enviar datos: el cuerpo HTTP puede llegar al servidor antes del rechazo. El motor CFE no está conectado; cambiar la variable no crea el motor ni autoriza el procesamiento.

## Versión estimada
La implementación propuesta corresponde a **XIL-AC 0.3.2**: mensaje estándar de privacidad, documentación operativa y prueba automatizada del aviso. No incluye detección automática de sensibilidad ni habilita el procesamiento de sesiones.

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
