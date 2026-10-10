# Revisión local de privacidad — XIL-AC 0.4.1

## Propósito
La herramienta `index.html` permite revisar un texto antes de considerar cualquier intercambio con XIL-AC. Toda la lógica se ejecuta en el navegador del dispositivo. La página no incluye una función de envío, solicitudes de red, bibliotecas externas, almacenamiento local, ni persistencia del texto.

## Cómo utilizar
1. Obtener el archivo `local-privacy-review/index.html` desde el repositorio privado.
2. Guardarlo en el dispositivo y abrir el archivo localmente en un navegador actualizado.
3. Pegar únicamente el texto que se desea revisar y seleccionar **Revisar texto**.
4. Si se detectan señales, no enviar el texto a la API remota.
5. Si no se detectan señales, no interpretar el resultado como autorización para enviar: revisar manualmente y mantener la compuerta remota cerrada.

## Alcance y límites
- Busca patrones explícitos de correos, teléfonos, documentos etiquetados, nombres/domicilios etiquetados, salud, violencia/abuso, autolesión, intimidad y adicciones.
- Muestra categorías detectadas, nunca los fragmentos coincidentes.
- No envía, guarda ni registra el texto mediante la propia página.
- No puede garantizar que el texto esté anonimizado. Puede omitir nombres sin etiqueta, identificadores indirectos, contexto implícito, paráfrasis o datos únicos.
- El dispositivo, el navegador, las extensiones, la sincronización del portapapeles y otros programas quedan fuera del control de esta página.
- No sustituye el criterio humano ni una evaluación de seguridad.

## Validación manual mínima
- [ ] Abrir el archivo sin conexión a internet.
- [ ] Revisar un ejemplo sintético con un correo y comprobar que aparece la categoría sin mostrar el correo.
- [ ] Revisar un ejemplo sintético con una referencia a violencia/autolesión y comprobar que se advierte riesgo elevado.
- [ ] Revisar un texto sintético neutral y comprobar que la interfaz dice “sin señales explícitas”, no “seguro”.
- [ ] Pulsar **Borrar texto y resultado** y comprobar que el campo queda vacío.
- [ ] En las herramientas de desarrollo del navegador, comprobar que la página no realiza solicitudes de red ni utiliza almacenamiento web.

## Estado
Implementación de cliente local propuesta para revisión en rama. No está desplegada ni integrada como barrera automática en la API. La API remota debe permanecer cerrada para el procesamiento de sesiones.
