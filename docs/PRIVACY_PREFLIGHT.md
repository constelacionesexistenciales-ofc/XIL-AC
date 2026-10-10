# Comprobación local previa al envío

La utilidad `python -m core.privacy_preflight` lee texto desde la entrada estándar, aplica el detector heurístico local y devuelve solo el estado, las categorías y un aviso. No realiza solicitudes de red ni imprime el texto analizado.

Uso:

```bash
python -m core.privacy_preflight < borrador-local.txt
```

Código de salida `0`: no se detectaron señales explícitas. Código `2`: se detectó una señal o el contenido no pudo verificarse; no transmitir. Código `64`: falta la entrada estándar.

**No se detectaron señales no significa que el texto sea seguro.** El detector puede producir falsos positivos y omitir nombres sin etiqueta, identificadores indirectos, paráfrasis o contexto implícito. Revisá el contenido y eliminá datos identificables innecesarios. La API remota mantiene cerrada la compuerta de procesamiento de sesiones por defecto.

Esta utilidad es una barrera local manual, no una garantía de privacidad ni una interfaz integrada. No envía datos a ninguna parte.
