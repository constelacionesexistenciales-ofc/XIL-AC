# Política operativa CFE / XIL-AC

## Investigación y desarrollo
La investigación, búsqueda web, contraste de fuentes, análisis bibliográfico, evolución del marco CFE, documentación y revisión técnica pueden continuar mediante la interfaz actual de ChatGPT. El motor autónomo de búsqueda de XIL-AC requiere integración independiente; su plan está en `RESEARCH_ENGINE_PLAN.md`.

## Trabajo de sesiones
Durante esta etapa, el trabajo de sesiones y los informes se realizan únicamente mediante la interfaz actual de ChatGPT con revisión humana. No enviar contenido personal de consultantes a la API remota de preproducción.

## Detector preventivo de privacidad — versión 0.4.0
XIL-AC incorpora un detector heurístico basado en reglas que busca señales explícitas de:
- correos electrónicos, teléfonos y documentos etiquetados;
- nombres o domicilios escritos mediante etiquetas;
- datos de salud, tratamiento psicológico y medicación;
- violencia, abuso, riesgo autolesivo y otros datos íntimos.

El detector devuelve solo categorías y nivel de riesgo; no devuelve los fragmentos encontrados ni los escribe en los registros. Si encuentra señales, la API responde con bloqueo y recordatorio preventivo. La compuerta de procesamiento de sesiones permanece cerrada por defecto incluso si no detecta señales.

**Límite esencial:** este detector no es infalible. Puede generar falsos positivos y no detectar nombres sin etiqueta, identificadores indirectos, paráfrasis o contexto implícito. No diagnostica ni determina por sí solo si un texto es seguro.

**Límite de transporte:** cuando el detector se ejecuta dentro de la API, el texto ya llegó al servicio remoto. Por tanto, esa integración es una segunda barrera y no impide el envío inicial. Para prevenir la transmisión, debe ejecutarse en un cliente local antes de enviar el contenido. Hasta que exista esa interfaz local, no enviar contenido de consultantes a la API remota.

## Mensaje estándar
> La información recibida contiene o podría contener material sensible; no recomendamos seguir con esta operación. En esta etapa, no envíes transcripciones, audios ni datos identificables a la API remota. Continuá el trabajo de sesiones mediante la interfaz de ChatGPT acordada. La investigación general y el desarrollo metodológico pueden continuar por esa interfaz.

Como Alexis es el único usuario operativo, el aviso funciona como recordatorio; no se incorporan por ahora flujos complejos de aprobación ni administración de múltiples usuarios.

## Bloqueo y estado
`CFE_SESSION_PROCESSING_ENABLED=false` por defecto. La API remota responde con un aviso de bloqueo. El cuerpo HTTP puede llegar al servidor antes del rechazo. El motor CFE no está conectado; cambiar la variable no crea el motor ni autoriza el procesamiento.

## Próximos pasos antes de habilitar sesiones
- Integrar una inspección local previa al envío en el cliente. Existe una utilidad CLI inicial (`python -m scripts.privacy_preflight`) que no transmite datos, pero no está integrada automáticamente con una interfaz.
- Evaluar el detector con ejemplos sintéticos y medir falsos positivos y falsos negativos.
- Mantener el bloqueo remoto hasta que el motor real, la identidad, la retención y las pruebas de seguridad estén aprobados.
- Probar el tratamiento de datos, borrado, acceso, copias y recuperación.
- Obtener aprobación humana explícita de la puerta de producción.

Si no se pueden cumplir estos requisitos, el procesamiento de sesiones permanece fuera del servicio remoto.
