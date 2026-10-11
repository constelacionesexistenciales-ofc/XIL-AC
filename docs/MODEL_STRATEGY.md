# Estrategia de modelos propios de XIL-AC — v1

**Estado:** diseño y selector determinista inicial. No es un modelo entrenado, no ejecuta inferencia y no constituye una integración con proveedores.

## Objetivo

Construir un sistema de IA controlado por XIL-AC que aproveche capacidades destacadas de modelos abiertos sin copiar pesos, datos privados, código propietario ni métodos protegidos. La propiedad diferencial debe estar en el sistema completo: políticas, evaluación, recuperación de evidencias, memoria trazable, herramientas limitadas, interfaz y adaptación autorizada a CFE.

## Tres familias para evaluar

No existe un “top 3” universal: el orden cambia por tarea, tamaño, cuantización, hardware, idioma, licencia y fecha. Esta es una **lista corta técnica**, no una clasificación absoluta.

| Familia | Fortaleza a evaluar | Uso potencial en XIL-AC | Consideración |
|---|---|---|---|
| Qwen3 | Multilingüismo, uso de herramientas y variedad de tamaños | General, extracción estructurada, español y orquestación ligera | La documentación del proyecto declara Apache 2.0 para sus modelos abiertos; confirmar la licencia de la versión exacta descargada. |
| DeepSeek-R1 | Razonamiento de varios pasos y modelos destilados de distintos tamaños | Análisis complejo, revisión de hipótesis y apoyo a programación | El repositorio declara MIT para R1, pero revisar las condiciones y licencias originales de cada modelo derivado. |
| Mistral — modelos abiertos adecuados a hardware | Eficiencia, modelos instruct y variantes orientadas a código/razonamiento | Respuesta rápida, tareas locales y segunda opinión independiente | Las licencias varían por modelo y versión; no asumir que toda la familia comparte la misma licencia. |

Fuentes oficiales:
- Qwen3: https://github.com/QwenLM/Qwen3
- DeepSeek-R1: https://github.com/deepseek-ai/DeepSeek-R1
- Catálogo de modelos Mistral: https://docs.mistral.ai/models/
- Licencia Llama 4, como alternativa a evaluar y no elección por defecto: https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE

Antes de elegir versiones concretas se deben registrar: nombre exacto, revisión/hash, licencia del modelo y tokenizer, restricciones de redistribución, requisitos de hardware, contexto real, calidad en español, evaluación de herramientas, vulnerabilidades conocidas y coste de operación.

## Arquitectura propuesta: XIL-AC Model Core

1. **Núcleo determinista propio:** identidad, permisos, riesgo, límites, trazabilidad, cancelación y Human Gate. Un modelo nunca decide sus propios permisos.
2. **Enrutador de tareas:** selecciona una ruta configurada según tarea, sensibilidad, coste y latencia.
3. **Modelos locales intercambiables:** inferencia local como ruta preferida para información sensible; las rutas remotas deben ser explícitas, autorizadas y sujetas a preflight de privacidad.
4. **Motor de investigación:** recuperación de fuentes, normalización de URL, registro de evidencias, extracción de afirmaciones, contraste de fuentes independientes y abstención cuando falte evidencia.
5. **Memoria verificable:** hechos, hipótesis y preferencias separados; cada elemento con procedencia, fecha, nivel de confianza, consentimiento y política de retención.
6. **Evaluación propia:** conjunto fijo de pruebas en español, casos adversariales, privacidad, razonamiento, programación, fidelidad a fuentes, latencia y coste. Cambiar de modelo exige repetir la evaluación.
7. **Adaptación especializada:** primero instrucciones y recuperación; después ajuste fino de bajo rango (LoRA/QLoRA) con datos autorizados, desidentificados y evaluados. No entrenar con transcripciones de consultantes sin consentimiento explícito y un protocolo de privacidad.
8. **Fallback controlado:** si la ruta preferida falla, usar solo una alternativa aprobada para la misma clasificación de privacidad; si no existe, abstenerse y pedir intervención humana.

## Selector inicial implementado

El archivo core/model_router.py introduce una selección determinista de identificadores configurados. No realiza llamadas de red ni carga pesos. La tarea privacy_sensitive solo acepta un identificador que comience con local/; si no está configurado o apunta a un proveedor remoto, falla de forma cerrada.

Configuración prevista para la futura integración:
- general
- reasoning
- coding
- research
- local — obligatoria para tareas sensibles

La conexión con variables de entorno, adaptadores reales, autenticación, límites, auditoría persistente y despliegue local debe añadirse en cambios separados y probarse antes de habilitar inferencia.

## Qué significa “modelo propio”

### Ahora
Propiedad del diseño de sistema y del control de ejecución, con modelos de terceros intercambiables y licencias respetadas.

### Próxima etapa
Un banco de pruebas reproducible para comparar tres modelos concretos con las mismas consultas y rúbricas, en español y con casos CFE sintéticos.

### Más adelante
Ajustar un modelo base autorizado para XIL-AC, documentando datos, licencia, versión, procedimiento, resultados y limitaciones. Entrenar un modelo fundacional desde cero no es la primera opción: requiere grandes cantidades de datos, aceleradores, investigación especializada y un coste elevado.

## Criterios de aceptación antes de usarlo con consultantes

- Cero llamadas a proveedores desde la política de selección.
- Ruta sensible rechaza modelos remotos.
- Ruta ausente o desconocida falla de forma cerrada.
- Pruebas reproducibles en CI.
- No se envían transcripciones a proveedores durante esta fase.
- No se habilita el procesamiento real de sesiones CFE.
- La elección final de modelo se basa en pruebas medidas, no en publicidad ni en una tabla genérica de puntuaciones.

## Próximos pasos técnicos

1. Ejecutar CI de esta política inicial.
2. Añadir corpus sintético de evaluación en español.
3. Definir un contrato de adaptador común, con límites de tiempo/tokens y cancelación.
4. Integrar un servidor de inferencia local en entorno de desarrollo aislado.
5. Comparar Qwen3, DeepSeek-R1 y una variante abierta de Mistral en el mismo hardware.
6. Publicar métricas y decidir qué modelo queda como generalista, razonador y revisor independiente.
7. Solo después, conectar el selector con el registro de evidencias y el núcleo de autonomía.
