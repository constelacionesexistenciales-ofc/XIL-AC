# Auditoría integral de dependencias, ingeniería inversa lícita y tecnología propia — XIL-AC

**Corte:** 2026-10-11  
**Base examinada:** `main` en `ca912dbfce082ec7cb9a35df12dac14a9d1789f0`, más revisión documental de las PR abiertas #27 y #29.  
**Estado:** auditoría estática del repositorio y metadatos de GitHub; no es auditoría de infraestructura desplegada, pentest, auditoría legal ni benchmark de rendimiento.  
**Regla de honestidad:** lo que aparece en una rama o una PR se considera propuesto, no integrado. Un archivo de despliegue no prueba que exista un despliegue.

## 1. Conclusión ejecutiva

XIL-AC ya contiene un núcleo de ingeniería propio: API, controles de acceso, límites de solicitud, detector heurístico de privacidad, registro de evidencias, trazabilidad, control de riesgo, migraciones y pruebas. Sin embargo, todavía depende de servicios y ecosistemas externos para alojar el código y ejecutar CI, obtener resultados web, distribuir paquetes, proporcionar imágenes de contenedor y —si se activa en el futuro— servir modelos de lenguaje.

La ventaja competitiva no debe perseguir la copia de ChatGPT, Claude, Gemini u otros sistemas. Debe surgir de una arquitectura que XIL-AC controle: política determinista, evaluación reproducible, trazabilidad afirmación→evidencia, aislamiento de datos, adaptadores sustituibles, interfaz universal, evaluación específica en español y CFE, y un Human Gate real.

**No es correcto afirmar que XIL-AC ya sea independiente de proveedores ni que sea superior en rendimiento.** Esa superioridad debe demostrarse tarea por tarea, con datos de prueba, métricas, coste y revisión independiente.

## 2. Inventario del sistema observado

| Área | Evidencia en el repositorio | Estado real y dependencia |
|---|---|---|
| Núcleo/API | `core/api.py`, `core/config.py`, `core/auth.py` | Código propio en Python/FastAPI. Depende de Python y paquetes mantenidos por terceros. |
| Autenticación/autorización | `core/auth.py`, roles y validación JWT/OIDC | Verificación JWT implementada; el proveedor OIDC real no está desplegado/verificado. Keycloak es una opción autohospedable, no una integración ya terminada. |
| Datos | PostgreSQL, `psycopg`, migraciones SQL | Esquema y conexión preparados. Falta evidencia de una base productiva, copias, restauración y operación sostenida. PostgreSQL es software externo abierto que podemos autohospedar. |
| Riesgo y autonomía | `core/autonomy.py`, `core/risk_gate.py` | Evaluador determinista inicial; no equivale a un agente autónomo ni ejecuta una acción con aprobación humana real. |
| Trazabilidad/auditoría | `core/trace.py`, `core/audit.py`, `core/evidence_registry.py` | Componentes propios iniciales; falta cerrar el ciclo de ejecución completo y su persistencia/retención operativa. |
| Privacidad | `core/privacy_detector.py`, `scripts/privacy_preflight.py`, `desktop-gateway/` | Detector heurístico y prototipo local. No garantiza anonimización; la app de escritorio requiere pruebas manuales en Windows y aún no es una puerta universal de salida. |
| Investigación web | `core/research.py`, interfaz y documentación | En `main` hay un adaptador de búsqueda basado en proveedor externo. La PR #29 propone SearXNG; CI verde en esa PR no significa que esté fusionada ni desplegada. |
| Evidencias científicas | `core/evidence_registry.py` | Modelo de datos propio; aún no extrae ni contrasta automáticamente afirmaciones de fuentes recuperadas. |
| Modelos de lenguaje | PR #27, `core/model_router.py` en rama | Solo selector de identificadores con política de fallo cerrado. No descarga pesos, no ejecuta inferencia, no entrena modelos y no elimina todavía la dependencia de un proveedor de IA. |
| Interfaz de investigación | `frontend/universal-research/` | HTML/CSS/JavaScript propios; navegador y sistema operativo siguen siendo dependencias de ejecución. |
| Escritorio Windows | Tkinter, DPAPI, PyInstaller e Inno Setup documentados | Prototipo. La compilación en CI no demuestra instalación, funcionamiento ni seguridad en un equipo Windows real. |
| Contenedores | `Dockerfile`, `compose.yaml`, `render.yaml` | Docker/Compose e imágenes base son dependencias externas. La configuración no prueba despliegue. `render.yaml` no prueba que exista un servicio activo en Render. |
| Pruebas/seguridad | pytest, HTTPX, Ruff, Bandit y flujos de GitHub Actions | Herramientas externas reemplazables. CodeQL aparece omitido en ejecuciones recientes de las PR revisadas; no debe contarse como análisis aprobado. |
| Repositorio/CI | Repositorio privado GitHub, GitHub Actions, Dependabot | Dependencia operacional importante: control de código, ejecución CI y gestión de cambios están alojados en GitHub. Existe permiso administrativo en la conexión revisada, pero no se han auditado todos los ajustes de cuenta. |

## 3. Mapa de dependencias externas

Clasificación: **A** = crítica para la operación actual o prevista; **B** = importante pero sustituible; **C** = opcional o de desarrollo.

| Dependencia | Tipo | Grado | Qué ocurre si falla | Alternativa / estrategia |
|---|---|---:|---|---|
| GitHub | Código, PR, issues, CI y releases | A | Se dificulta el flujo de cambios y pruebas alojadas | Mantener copias Git verificadas y exportaciones; preparar migración a Forgejo/Gitea autohospedado. La migración debe probarse, no suponerse. |
| GitHub Actions | Ejecución de CI | A | No se ejecutan las verificaciones alojadas | Ejecutar la misma suite en runner propio y conservar Actions como opción. No retirar CI hasta comparar resultados. |
| Python y paquetes PyPI | Runtime y librerías | A | Instalación, actualizaciones o compatibilidad pueden fallar | Fijar versiones y hashes, SBOM, revisión de licencias, caché/índice interno y builds reproducibles. No conviene reescribir FastAPI/JWT/driver de PostgreSQL sin beneficio probado. |
| Brave Search | Búsqueda web actual en `main` | A para investigación web con esa configuración | Sin credencial, cuota o servicio no hay resultados | Adaptador común; SearXNG autohospedado y fuentes especializadas. PR #29 sigue pendiente de integración. |
| Motores consultados por SearXNG | Índices/resultados externos | A para metabúsqueda fresca | Bloqueos, cambios de HTML/API, cuotas o sesgos de cobertura | Diversificar motores y fuentes; no describir SearXNG como índice web propio. |
| Índices web globales | Corpus de Internet actualizado | A para cobertura amplia | No hay sustituto pequeño y gratuito con la misma cobertura/actualidad | Crear índice propio de un corpus limitado y permitido; combinar fuentes abiertas. No prometer equivalencia universal. |
| PostgreSQL | Persistencia compartida | A | API degradada o bloqueo seguro de operaciones dependientes | Autohospedar PostgreSQL, backups, restauración ensayada y monitorización. El software puede ser propio en operación, pero no lo desarrollamos desde cero. |
| Proveedor OIDC | Identidad | A en staging/producción | Autenticación no disponible; la aplicación debe fallar de forma cerrada | Keycloak autohospedado u otro compatible con OIDC. No crear un sistema casero de contraseñas/tokens como sustituto de un IdP auditado. |
| Gestor de secretos | Credenciales de producción | A | Riesgo de exposición o imposibilidad de rotación | OpenBao autohospedado o gestor del entorno. Aún no hay integración ni despliegue verificados. |
| Imágenes Docker (Python/PostgreSQL/SearXNG) | Cadena de suministro y runtime | B/A | Build o despliegue puede romperse o recibir una actualización no deseada | Fijar versiones y digest, escanear imágenes, SBOM, actualizar por PR y verificar procedencia. Evitar `latest` en producción. |
| Modelo de lenguaje | Generación, extracción y síntesis futura | A para las funciones generativas | Sin modelo no existe inferencia; los modelos locales también requieren hardware | Adaptador de modelos; modelo abierto local validado por benchmark y fallback explícito. La PR #27 no contiene inferencia real. |
| Hardware / aceleración | Inferencia local | A para modelos grandes locales | Latencia alta, falta de memoria o imposibilidad de ejecutar el modelo | Elegir modelos cuantizados por hardware real; CPU/GPU/NPU según pruebas. No es reemplazable solo con código. |
| Sistema operativo Windows / DPAPI | Protección del almacén local del prototipo de escritorio | B | Algunas funciones de la app local no operan igual en otros sistemas | Mantener adaptador por plataforma; para multiplataforma, implementar y auditar mecanismos nativos equivalentes. |
| Chromium / Playwright (pruebas de navegador) | QA de interfaz | C | No se ejecutan pruebas de navegador | Runner propio o navegador compatible; conservar cobertura E2E. |
| Render (declaración de despliegue) | Posible destino de alojamiento | C hasta verificar uso real | No afecta a la ejecución local; si se usa, puede ser bloqueo operacional | Despliegue propio o proveedor alternativo mediante configuración portable. No se verificó un despliegue activo. |

## 4. Qué conviene desarrollar como tecnología propia

Prioridad por valor diferencial y control; no por cantidad de código.

### P0 — Control y seguridad propios
1. **Registro único de dependencias y capacidades**: adaptadores declarados, versión, licencia, proveedor, destino de datos, timeout, límites y alternativa.
2. **Política determinista de permisos y riesgo**: el modelo nunca concede sus propios permisos; aprobación humana vinculada a una acción concreta, identidad, alcance, caducidad y `execution_id`.
3. **TRACE de extremo a extremo**: relacionar solicitud, decisión, proveedor/modelo, fuentes, costes, resultado, abstención y aprobaciones sin guardar transcripciones sensibles por defecto.
4. **Puerta local universal de salida**: revisar el contenido antes de cualquier envío remoto; bloquear por defecto ante incertidumbre. El prototipo de escritorio actual no intercepta otras aplicaciones.
5. **Gestión de dependencias y cadena de suministro**: versiones fijadas, hashes cuando aplique, SBOM, análisis de licencias, escaneo de vulnerabilidades, procedencia y proceso de actualización reversible.

### P1 — Motor de investigación diferencial
1. Contrato común de búsqueda con adaptadores independientes.
2. Recuperación de fuentes permitidas con límites de tamaño/tiempo, validación de destino y defensa contra SSRF.
3. Deduplicación, canonización, fecha de consulta, procedencia y calidad de metadatos.
4. Extracción de afirmaciones con fragmentos de respaldo, evidencia contraria y abstención explícita.
5. Evaluación de fuentes y de afirmaciones separada del ranking del buscador.
6. Conjunto de evaluación versionado en español: precisión de citas, cobertura, omisiones, contradicciones, actualidad, latencia y coste.

### P2 — Modelo propio de operación, no necesariamente un modelo fundacional
1. Adaptadores para inferencia local y remota, con límites explícitos de privacidad.
2. Banco de pruebas reproducible para español, instrucciones, extracción, razonamiento, programación y tareas CFE sintéticas autorizadas.
3. Selección por calidad medida, latencia, memoria, coste, licencia y nivel de privacidad; sin elegir modelos por fama.
4. Datos propios autorizados y curados para evaluar/adaptar el sistema; nunca entrenar con transcripciones reales sin base jurídica, consentimiento y controles apropiados.
5. Evaluar ajuste fino (LoRA/QLoRA) solo cuando los resultados demuestren que mejora frente a un modelo base y una buena recuperación documental.

### P3 — Menos dependencia operativa
1. Runner de CI autohospedado y copia remota de repositorio.
2. Despliegue privado reproducible con backups, restauración, observabilidad y actualización reversible.
3. Identidad autohospedada con Keycloak y secretos con OpenBao, ambos con políticas, persistencia, auditoría y recuperación probadas.
4. Índice documental propio inicial sobre corpus acotados, públicos o licenciados; crecer solo cuando coste y valor lo justifiquen.

## 5. Ingeniería inversa: qué sí podemos y qué no

La ingeniería inversa responsable se limita a comportamientos accesibles y a materiales que tenemos derecho a examinar. El objetivo es aprender principios, definir pruebas y producir una implementación original. No se debe asumir que una observación permite conocer el diseño interno.

| Tecnología/objetivo | Qué sí podemos hacer | Qué no podemos prometer o hacer solo con ingeniería inversa |
|---|---|---|
| Interfaces ChatGPT, Claude, Gemini y otras | Evaluar flujos visibles, latencia observada, usabilidad, patrones de interacción y resultados bajo casos de prueba autorizados; diseñar una interfaz propia mejor medida | Obtener su código fuente privado, prompts de sistema no publicados, arquitectura interna, pesos, datos de entrenamiento o reproducir exactamente su funcionamiento interno |
| Modelos cerrados | Comparar salidas observables, construir un conjunto de evaluación y desarrollar alternativas originales | Recuperar de forma fiable los pesos, datos de entrenamiento o razonamiento interno privado a partir de entradas y salidas; garantizar paridad total |
| Modelos abiertos | Leer licencias y documentación, usar los pesos disponibles según sus condiciones, ejecutar benchmarks y adaptar cuando la licencia lo permita | Suponer que “abierto” significa sin restricciones; ignorar licencias del modelo, tokenizer, datos, derivados o uso comercial |
| Buscadores e índices web | Crear adaptadores, comparar resultados, usar APIs/documentos permitidos y construir un índice propio de un corpus permitido | Clonar el índice global privado de un buscador, obtener sus señales internas de ranking o copiar bases de datos protegidas sin autorización |
| APIs comerciales | Analizar contrato público, errores, cuotas y resultados dentro de las condiciones de uso; crear interfaz intercambiable | Evadir controles de acceso, límites, autenticación o condiciones contractuales; replicar el servicio privado mediante acceso no autorizado |
| Protocolos y formatos | Implementar protocolos publicados y formatos documentados de forma compatible | Copiar implementaciones propietarias protegidas o afirmar compatibilidad completa sin suite de conformidad |
| Seguridad de terceros | Evaluar superficies accesibles con autorización, pruebas controladas y divulgación responsable | Entrar en sistemas sin permiso, extraer secretos o explotar infraestructura de terceros fuera del alcance autorizado |
| Datos de consultantes / casos CFE | Diseñar conjuntos sintéticos o anonimizados con consentimiento y gobernanza verificable | Tratar un detector heurístico como anonimización garantizada o utilizar datos privados sin autorización y base adecuada |
| Infraestructura física y hardware | Medir consumo, rendimiento y compatibilidad; seleccionar hardware disponible | Crear por software una GPU, memoria, ancho de banda, electricidad o capacidad física que no existe |
| Componentes patentados, marcas y material protegido | Desarrollar una alternativa funcional independiente tras revisión de patentes, marcas, licencias y jurisdicción | Afirmar libertad de operación o ausencia de infracción sin revisión jurídica competente |

**Límite explícito:** no puedo extraer secretos de sistemas privados, acceder a código o infraestructura sin autorización, reconstruir fielmente pesos o datos propietarios que no están disponibles, ni garantizar una copia funcional de una tecnología cerrada mediante ingeniería inversa. Sí puedo ayudar a estudiar información pública, diseñar pruebas permitidas, construir código original, implementar componentes abiertos y documentar incertidumbres. La evaluación jurídica de licencias, patentes y condiciones concretas requiere revisión especializada.

## 6. Cómo demostraremos que XIL-AC es superior

No se aceptarán frases como “mejor que ChatGPT” sin pruebas. La comparación debe usar el mismo conjunto de tareas y conservar versión, fecha, configuración y condiciones.

| Dimensión | Métrica verificable | Condición para declarar mejora |
|---|---|---|
| Exactitud de investigación | Afirmaciones correctas y respaldadas / afirmaciones evaluadas | Mejora estadísticamente defendible sin empeorar de forma inaceptable la cobertura |
| Fidelidad de citas | Citas que realmente respaldan la afirmación / citas revisadas | Umbral definido antes de la prueba; cero tolerancia a citas inventadas en la evaluación crítica |
| Contradicciones | Conflictos relevantes detectados frente a conflictos del conjunto de referencia | Medir precisión y recuperación, no solo cantidad detectada |
| Privacidad | Casos sensibles bloqueados, falsos positivos y falsos negativos | No usar “cero riesgo”; umbrales por categoría y revisión humana de casos límite |
| Autonomía segura | Acciones fuera de política ejecutadas | Cero en el conjunto de pruebas; las aprobaciones deben estar ligadas a alcance y caducidad |
| Resiliencia | Comportamiento ante timeout, caída de DB, IdP, buscador o modelo | Fallo cerrado, error identificable y recuperación documentada |
| Portabilidad | Tiempo para sustituir proveedor y pruebas que pasan | Sustitución de adaptador sin cambiar contratos ni política de seguridad |
| Coste | Coste por tarea completa y coste mensual operativo | Comparación con mismo nivel de calidad y carga |
| Rendimiento | Latencia p50/p95, throughput y uso de memoria | Medido en hardware y carga declarados |
| Mantenibilidad | Tiempo de actualización, incidencias y complejidad de módulos | Menos acoplamiento y duplicación sin reducir controles o pruebas |

El conjunto de pruebas debe contener consultas sintéticas o públicas y casos CFE autorizados. Las métricas, exclusiones y umbrales se registran antes de ejecutar los experimentos para evitar elegir solo los resultados favorables.

## 7. Bloqueos que no se resuelven con código solamente

- **Credenciales y servicios reales:** hay que configurar de forma segura el IdP, gestor de secretos y credenciales que se decida usar.
- **Hardware y presupuesto:** ejecutar modelos locales grandes e indexar corpus amplios requiere recursos físicos y operación.
- **Autorización y gobernanza de datos:** los datos reales requieren permisos, reglas de retención, eliminación y control de acceso.
- **Infraestructura:** un despliegue privado necesita servidor o alojamiento, DNS/TLS cuando corresponda, backups, monitorización y responsable operativo.
- **Validación humana:** la aprobación de riesgo, las pruebas de Windows y la autorización para sesiones reales no se pueden inferir de CI.
- **Licencias y legalidad:** la compatibilidad de licencias, patentes y términos de uso debe revisarse para los componentes y usos concretos.

## 8. Secuencia de trabajo propuesta

1. Cerrar la revisión de las PR #29 (SearXNG) y #27 (selector de modelos): CI, revisión del código y decisión explícita de integración; no fusionarlas solo por tener CI verde.
2. Publicar el inventario de dependencias y un registro de riesgos/alternativas, que este documento inicia.
3. Construir un contrato de adaptadores con pruebas de conformidad y fallos controlados.
4. Añadir SBOM, fijación de versiones/digests y auditoría de licencias/cadena de suministro.
5. Construir el evaluador de investigación y un corpus de pruebas reproducible antes de afirmar superioridad.
6. Implementar y probar inferencia local real en el hardware disponible; el selector de modelos no cuenta como inferencia.
7. Completar identidad, secretos, preproducción privada, observabilidad, backup/restore y pruebas de seguridad/carga.
8. Mantener el procesamiento de sesiones CFE deshabilitado hasta pasar la puerta de producción y recibir autorización humana explícita.

## 9. Estado de la auditoría

- [x] Inspección del árbol de archivos de `main`.
- [x] Lectura de la base, configuración, documentación de producción, privacidad, investigación y registro de evidencias.
- [x] Revisión de las PR abiertas #27 y #29 y de los estados recientes de CI/CodeQL.
- [x] Separación entre funciones integradas, propuestas y despliegues no verificados.
- [ ] Revisión completa de cada archivo y cada dependencia transitiva con herramientas de análisis de composición de software.
- [ ] SBOM generado y revisado.
- [ ] Auditoría de licencias y vulnerabilidades con versiones concretas.
- [ ] Pruebas de integración reales contra SearXNG, Keycloak, OpenBao y un modelo local.
- [ ] Pruebas de carga, recuperación, seguridad y despliegue.
- [ ] Benchmark comparativo reproducible.

**Conclusión:** esta auditoría establece la línea base y la estrategia. No declara la plataforma autónoma, completamente independiente ni superior todavía. La siguiente evidencia debe provenir de cambios revisables, pruebas automatizadas y mediciones reproducibles.
