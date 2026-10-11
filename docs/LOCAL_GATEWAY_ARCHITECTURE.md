# Arquitectura de la Puerta Local XIL-AC

## Objetivo
Aplicación instalable local-first que inspecciona, minimiza y autoriza operaciones antes de transmitir datos a servicios remotos de XIL-AC.

## Principio no negociable
El cliente local es el primer control; la API remota mantiene su propio control como segunda barrera. El detector del servidor ocurre después de recibir el cuerpo y no es un filtro previo al envío. La compuerta remota para sesiones permanece cerrada hasta aprobar la Puerta de Producción.

## Capas

### 1. Interfaz instalable
- Texto y archivos seleccionados deliberadamente por el usuario.
- Acciones explícitas: revisar, limpiar, anonimizar, cancelar y continuar si la política lo permite.
- Vista previa del contenido transformado antes de transmitirlo.
- Sin captura oculta de pantalla, teclado, micrófono ni portapapeles; sin envío automático.

### 2. Motor local de privacidad
- Detección de identificadores y categorías sensibles.
- Minimización y seudonimización con revisión humana.
- Resultado estructurado con señales, categorías, confianza aproximada y acción sugerida; nunca devolver fragmentos coincidentes.
- “Sin señales detectadas” nunca equivale a “seguro” o “anonimizado”.

### 3. Motor de políticas
- DENY: alto riesgo, operación no autorizada o política desconocida.
- LOCAL_ONLY: tarea realizable sin red.
- REVIEW_REQUIRED: incertidumbre o transformación que necesita revisión humana.
- ALLOW_MINIMIZED: contenido minimizado aprobado para una operación remota específica.
- ALLOW: solo para operación y categoría expresamente aprobadas.
- Si el motor, la política o la configuración fallan, no transmitir.

### 4. Puerta de salida
- Todas las solicitudes propias de XIL-AC pasan por el adaptador local.
- Destinos autorizados, TLS verificado y secretos fuera del instalador.
- La API remota vuelve a comprobar identidad, permisos, tamaño, política y compuerta.
- El servidor nunca confía solo en la declaración del cliente de que el contenido está limpio.

### 5. Procesamiento local y recursos
- Ejecutar localmente validación, reglas, minimización y tareas deterministas.
- Medir memoria, CPU y latencia antes de asignar modelos locales más pesados.
- Reservar modelos remotos para tareas que justifiquen su costo y exposición.
- En equipos modestos, usar reglas livianas y procesamiento por lotes.
- Medir rendimiento en equipos reales; no inventar porcentajes de mejora.

### 6. Auditoría local mínima
- Registrar decisión, versión de reglas y código de resultado, sin transcripciones ni valores detectados.
- Historial técnico revisable y borrable.
- Sin telemetría por defecto; diagnósticos opcionales nunca deben incluir contenido.
- No almacenar sesiones por defecto.

## Plan multiplataforma

### Fase A — prototipo local
- Herramienta local sin red y conjunto de pruebas sintéticas.
- Verificar que abrir, analizar, limpiar y cancelar no generen solicitudes de red.
- El prototipo permite evaluar reglas, pero no es todavía una llave obligatoria.

### Fase B — escritorio instalable (primer objetivo: Windows)
- MVP elegido: Python + Tkinter para interfaz sencilla, motor local en módulo independiente y empaquetado con PyInstaller; Inno Setup para generar el instalador.
- La compilación se propone en un flujo automatizado de Windows; el artefacto solo se considera listo tras ejecutar y revisar las pruebas y el instalador.
- No se necesita un servicio local ni un puerto de escucha para el MVP: interfaz y motor corren en el mismo proceso.
- No incrustar credenciales de producción. La aplicación no debe importar bibliotecas de red ni contener una función de envío.
- Tras validar el MVP, reevaluar firma de binarios, actualización verificada, permisos mínimos y recuperación.

### Fase C — móvil
- Reutilizar reglas y contrato de políticas donde sea viable, con interfaces nativas cuando corresponda.
- Respetar el aislamiento de Android/iOS: una app normal no puede inspeccionar o bloquear libremente otras apps.
- No prometer control global sin capacidades de administración y permisos específicos.

### Fase D — control de red ampliado
- Evaluar proxy administrado, VPN local o políticas del sistema solo si se justifica y con consentimiento explícito.
- Documentar alcance, excepciones, consecuencias y recuperación.
- No inspeccionar comunicaciones de otras aplicaciones como comportamiento predeterminado.

## Contrato mínimo de decisión
- Identificador aleatorio de operación, finalidad, modo solicitado, categorías sin valores, decisión, razón y versión de política.
- No incluir texto original, fragmentos coincidentes, identificadores, transcripciones, credenciales ni tokens.

## Criterios de aceptación
- [ ] Funciona sin conexión.
- [ ] La inspección sucede antes de cualquier petición remota.
- [ ] Abrir, analizar, limpiar y cancelar no generan solicitudes de red.
- [ ] Ante incertidumbre, la acción predeterminada es no transmitir.
- [ ] El contenido transformado se muestra antes del envío.
- [ ] Ningún valor sensible aparece en resultados o registros.
- [ ] El cliente no puede abrir por sí solo la compuerta remota.
- [ ] Pruebas sintéticas cubren falsos positivos, falsos negativos y entradas malformadas.
- [ ] Se miden CPU, memoria y latencia en dispositivos objetivo.
- [ ] Se verifica firma del instalador, actualización, recuperación y desinstalación.
- [ ] Estado de pruebas y distribución solo se informa con evidencia.

## Límites
La aplicación puede ser obligatoria para el flujo propio de XIL-AC, pero no impide por sí sola copiar información a otra aplicación ni bloquear todo el tráfico del dispositivo. Eso requiere controles específicos del sistema operativo. La puerta local reduce riesgo; no garantiza detección total ni anonimización perfecta.

## Decisión recomendada
Construir primero el cliente de escritorio local y una biblioteca de políticas testeable. Mantener cerrada la API de sesiones y validar con datos sintéticos. Elegir sistema operativo objetivo antes de crear instaladores. No declarar llave obligatoria, protección integral o producción hasta disponer de evidencia verificable.