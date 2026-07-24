# Lessons

> Lecciones aprendidas durante la ejecución del proyecto.

## Índice

- [L-001 — No duplicar reglas entre un agente y su skill](#l-001--no-duplicar-reglas-entre-un-agente-y-su-skill)
- [L-002 — El protocolo de inicio de sesión no lee documentos de contexto en la raíz del proyecto](#l-002--el-protocolo-de-inicio-de-sesión-no-lee-documentos-de-contexto-en-la-raíz-del-proyecto)
- [L-003 — Mantener dos caminos vivos en paralelo (CLI y SDK, o dos abstracciones de conversación) generó el desorden del repo experimental anterior](#l-003--mantener-dos-caminos-vivos-en-paralelo-cli-y-sdk-o-dos-abstracciones-de-conversación-generó-el-desorden-del-repo-experimental-anterior)
- [L-004 — Trampa del entorno heredado por el subproceso del Agent SDK](#l-004--trampa-del-entorno-heredado-por-el-subproceso-del-agent-sdk)
- [L-005 — Las herramientas built-in del CLI están implementadas dentro del CLI, no se reimplementan](#l-005--las-herramientas-built-in-del-cli-están-implementadas-dentro-del-cli-no-se-reimplementan)
- [L-006 — Las skills son carpetas con SKILL.md, no archivos .py](#l-006--las-skills-son-carpetas-con-skillmd-no-archivos-py)
- [L-007 — La consola de Windows (cp1252) rompe al imprimir emojis del modelo](#l-007--la-consola-de-windows-cp1252-rompe-al-imprimir-emojis-del-modelo)
- [L-008 — Completar tareas de infraestructura no equivale a construir el producto core del harness](#l-008--completar-tareas-de-infraestructura-no-equivale-a-construir-el-producto-core-del-harness)
- [L-009 — Un texto de terminal que se ve "pegado"/cortado puede ser el usuario tecleando encima, no un bug de truncamiento](#l-009--un-texto-de-terminal-que-se-ve-pegadocortado-puede-ser-el-usuario-tecleando-encima-no-un-bug-de-truncamiento)
- [L-010 — `effort` del SDK funciona por sí solo, sin requerir `thinking` adaptive, y no se reporta de vuelta](#l-010--effort-del-sdk-funciona-por-sí-solo-sin-requerir-thinking-adaptive-y-no-se-reporta-de-vuelta)
- [L-011 — El CLI usa un modelo auxiliar (Haiku) para tareas internas de infraestructura, independiente del modelo fijado por agente](#l-011--el-cli-usa-un-modelo-auxiliar-haiku-para-tareas-internas-de-infraestructura-independiente-del-modelo-fijado-por-agente)
- [L-012 — El SDK soporta herramientas en-proceso que conviven con autenticación por suscripción y con una Session anidada](#l-012--el-sdk-soporta-herramientas-en-proceso-que-conviven-con-autenticación-por-suscripción-y-con-una-session-anidada)

## Detalle

### L-001 — No duplicar reglas entre un agente y su skill
**Fecha:** 2026-07-23
**Contexto:** al crear session-starter y session-closer se copiaron dentro del agente las mismas reglas ya definidas en su skill (qué archivos leer/actualizar, obligatorio vs. a demanda).
**Lección:** cuando un agente existe para ejecutar una skill, el agente debe limitarse a invocarla y añadir solo lo que le es propio (activación, presentación de resultados); duplicar reglas genera riesgo de que ambas fuentes queden desincronizadas si se edita solo una.
**Aplicación:** al definir nuevos agentes que envuelven una skill, revisar que no repitan contenido normativo ya cubierto por la skill.

### L-002 — El protocolo de inicio de sesión no lee documentos de contexto en la raíz del proyecto
**Fecha:** 2026-07-23
**Contexto:** el `session-start-protocol` solo lee archivos dentro de `900_persistence/`. Existe un archivo `idea.md` en la raíz del proyecto (10.9 KB) que ya contenía la definición de alcance y arquitectura del harness, pero el protocolo no lo consulta.
**Lección:** por eso el `session-starter` reportó al inicio de esta sesión que "no se ha investigado ni definido el alcance", cuando en realidad ya existía documentación relevante fuera de `900_persistence/`. Un protocolo de inicio que solo mira su propia carpeta de memoria puede dar conclusiones incorrectas si hay contexto de proyecto en otros archivos de la raíz.
**Aplicación:** al reanudar sesiones futuras, revisar también documentos de contexto en la raíz del proyecto (p. ej. `idea.md`) antes de concluir que algo no está definido; considerar si el `session-start-protocol` debe ampliarse para listar/leer la raíz del proyecto.

### L-003 — Mantener dos caminos vivos en paralelo (CLI y SDK, o dos abstracciones de conversación) generó el desorden del repo experimental anterior
**Fecha:** 2026-07-23
**Contexto:** al revisar el repo experimental `Harness_TripleS` con el usuario, este explicó que perdió el control del diseño porque mantuvo dos caminos vivos a la vez: un archivo para trabajar con el CLI de Claude Code y otro para trabajar con el Agent SDK; de forma análoga, existían dos abstracciones paralelas de conversación (`Provider` de un disparo + `Sesion` multi-turno).
**Lección:** cuando dos formas de resolver el mismo problema conviven "por si acaso", el diseño se bifurca silenciosamente y cada nueva funcionalidad debe decidir a cuál camino atarse, lo que degrada la mantenibilidad rápidamente incluso con buena cobertura de tests.
**Aplicación:** en este proyecto se decide explícitamente un solo camino de proveedor (el SDK, ver D-008) y una sola cadena de abstracción de conversación (`Provider`/`Session`, ver D-009), desde el primer archivo.

### L-004 — Trampa del entorno heredado por el subproceso del Agent SDK
**Fecha:** 2026-07-23
**Contexto:** al verificar la autenticación por suscripción en el repo experimental, se descubrió que `os.environ.pop("ANTHROPIC_API_KEY")` en el proceso padre no bastaba para forzar que el subproceso `claude` usara las credenciales OAuth de la suscripción.
**Lección:** el SDK arma el entorno del subproceso como `{**os.environ, **options.env}` y no permite borrar una variable heredada; solo se puede sobrescribir a cadena vacía vía `ClaudeAgentOptions(env=...)`, valor que el CLI trata como ausente. Hay que hacer ambas cosas (pop en el padre y sobrescritura a `""` en `options.env`) para garantizar autenticación por suscripción.
**Aplicación:** al implementar `providers/claude_sdk.py` (ref T-015), aplicar ambas medidas explícitamente y no asumir que basta con no exportar la variable. Ver C-003, A-001.

### L-005 — Las herramientas built-in del CLI están implementadas dentro del CLI, no se reimplementan
**Fecha:** 2026-07-23
**Contexto:** al verificar la documentación oficial del Agent SDK (`/anthropics/claude-agent-sdk-python`, vía ctx7), se corrigió un supuesto implícito del usuario sobre cómo funcionan herramientas como `Bash`, `Read`, `Write`, `Edit`, `Grep`, `Glob` o `WebFetch`.
**Lección:** estas herramientas built-in están implementadas dentro del propio CLI `claude`; el proyecto no escribe su lógica, solo concede o niega acceso a ellas por agente (vía `tools`/`disallowedTools` de `AgentDefinition`). Solo las herramientas propias, declaradas con `@tool` y `create_sdk_mcp_server`, se implementan en código (referenciadas como `mcp__<servidor>__<herramienta>`).
**Aplicación:** al diseñar `tools/builtin.py` (ref D-016), este módulo debe limitarse a nombrar/registrar las herramientas del CLI para el catálogo, no a implementarlas.

### L-006 — Las skills son carpetas con SKILL.md, no archivos .py
**Fecha:** 2026-07-23
**Contexto:** al verificar contra documentación oficial del SDK durante esta sesión.
**Lección:** las skills del harness no son módulos Python; son carpetas que contienen un archivo `SKILL.md`, y el nombre de la skill sale del campo `name` dentro de ese `SKILL.md` o, en su defecto, del nombre de la carpeta. Además, `skills` en `ClaudeAgentOptions` es un filtro de contexto (qué skills ve el modelo), no un mecanismo de aislamiento de archivos (ver C-004).
**Aplicación:** al construir `src/sda/skills/<nombre>/SKILL.md` (ref D-016), no se debe intentar implementar skills como paquetes `.py`; y no se debe asumir que ocultar una skill del listado la protege de acceso vía `Read`/`Bash`.

### L-007 — La consola de Windows (cp1252) rompe al imprimir emojis del modelo
**Fecha:** 2026-07-24
**Contexto:** al implementar el REPL interactivo real (`src/sda/repl.py`, ref T-022) e imprimir la respuesta del modelo directamente en la consola de Windows.
**Lección:** la consola de Windows suele usar cp1252 por defecto, que no puede codificar emojis ni ciertos caracteres tipográficos; como el modelo los usa con frecuencia en sus respuestas, imprimir sin más lanza `UnicodeEncodeError` y corta el turno.
**Aplicación:** reconfigurar `stdout`/`stdin` a UTF-8 con `errors="replace"` al inicio del REPL (helper `_forzar_utf8()` en `src/sda/repl.py`); es una precaución barata y segura de aplicar también en otros puntos de entrada interactivos del harness, sea cual sea la plataforma.

### L-008 — Completar tareas de infraestructura no equivale a construir el producto core del harness
**Fecha:** 2026-07-24
**Contexto:** al iniciar esta sesión, la lista de "próximo" en `progress.md` solo tenía tareas de infraestructura de desarrollo (T-018, T-020, T-021, T-023). Al releer `idea.md` con foco en el producto, se detectó que ninguno de los pilares centrales descritos ahí (doble bucle REPL, máquina de estados en disco, flujo de onboarding con `document-extract.md`, evaluación de calidad interna, puerta de aprobación humana) existía todavía en el código.
**Lección:** una lista de tareas pendientes puede ir acumulando trabajo de plomería/andamiaje sin que nadie note que el producto central definido en el documento de alcance sigue sin una sola rebanada vertical funcionando; conviene revisar periódicamente contra el documento de alcance original, no solo contra la lista de tareas acumulada.
**Aplicación:** al priorizar próximas tareas, verificar explícitamente contra `idea.md` (o el documento de alcance vigente) si ya existe al menos una rebanada vertical end-to-end del producto core antes de seguir sumando tareas de infraestructura alrededor de él. Ver D-020, T-024.

### L-009 — Un texto de terminal que se ve "pegado"/cortado puede ser el usuario tecleando encima, no un bug de truncamiento
**Fecha:** 2026-07-24
**Contexto:** en la primera corrida manual de `sda start` (ref T-025, `sda_test_004`), el resumen del onboarding-reader se vio visualmente pegado al comando `aprobar` escrito por el usuario en la terminal, sugiriendo a primera vista un corte de texto o un bug de sincronización de la salida.
**Lección:** al investigar, se confirmó que el texto del resumen no estaba truncado ni la lógica fallaba; el usuario simplemente escribió su respuesta pegada al final del texto impreso, sin salto de línea de por medio. Un síntoma visual de "texto cortado/pegado" en una interfaz de terminal puede tener una causa mucho más simple (timing de tecleo del humano) que un defecto de la lógica del programa.
**Aplicación:** ante un reporte de "se ve cortado/pegado" en salida de consola, primero descartar una explicación simple de interacción humano-terminal (falta de salto de línea, tecleo simultáneo) antes de asumir un bug de truncamiento; de todos modos, si mejora la legibilidad, es válido añadir espaciado/prefijos por hablante para evitar la ambigüedad visual en el futuro (ver D-024).

### L-010 — `effort` del SDK funciona por sí solo, sin requerir `thinking` adaptive, y no se reporta de vuelta
**Fecha:** 2026-07-24
**Contexto:** al implementar y verificar T-026 (fijar `model="sonnet"`/`effort="high"` para el onboarding-reader) en `src/sda/providers/claude_sdk.py`.
**Lección:** `ClaudeAgentOptions.effort` (`EffortLevel = low|medium|high|xhigh|max`) mapea directamente a `--effort` del CLI y funciona de forma independiente, sin necesidad de activar `thinking={"type":"adaptive"}` ni ningún otro parámetro adicional. Sin embargo, el SDK no devuelve el `effort` usado en ninguna parte de la respuesta (`AssistantMessage`, `ResultMessage.model_usage`); solo se puede confirmar por observación indirecta (comportamiento del modelo) o instrumentación temporal de debug.
**Aplicación:** al fijar `effort` para cualquier agente futuro del harness, no asumir que hace falta configurar `thinking` en paralelo; y si se necesita verificar en vivo qué `effort` se está aplicando realmente, no confiar en la telemetría del SDK, sino en pruebas controladas o logging temporal.

### L-011 — El CLI usa un modelo auxiliar (Haiku) para tareas internas de infraestructura, independiente del modelo fijado por agente
**Fecha:** 2026-07-24
**Contexto:** durante la verificación en vivo de T-026 (`sda start` real, proyecto `sda_test_007`), se observó un uso mínimo de `claude-haiku-4-5` en la telemetría de la sesión, a pesar de haber fijado `model="sonnet"` para el onboarding-reader.
**Lección:** el CLI de Claude Code invoca internamente un modelo auxiliar más económico (Haiku) para tareas de infraestructura propias del proceso (p. ej. resúmenes o gestión interna de tareas), separado del modelo que el harness fija explícitamente para el trabajo del agente. Ese uso de Haiku no es un error ni una fuga del modelo configurado.
**Aplicación:** al revisar telemetría de uso/costo por modelo (relevante para T-023/T-011), no interpretar apariciones de un modelo distinto al fijado como una falla de configuración; distinguir entre el modelo del agente y el modelo auxiliar de infraestructura del CLI.

### L-012 — El SDK soporta herramientas en-proceso que conviven con autenticación por suscripción y con una Session anidada
**Fecha:** 2026-07-24
**Contexto:** al ejecutar el spike `spikes/t027_herramienta_en_proceso.py` (ref T-027), se necesitaba confirmar si un líder LLM (Opus + effort high) podía invocar una herramienta implementada en Python que, a su vez, condujera una segunda `Session` completa del SDK (bucle interno, Sonnet + effort high) sin romper la autenticación por suscripción ni chocar con el `ClaudeSDKClient` del propio líder.
**Lección:** el SDK (`claude_agent_sdk` 0.2.126) soporta herramientas en-proceso vía `@tool(name, desc, schema)` + `create_sdk_mcp_server("harness", tools=[...])`, registradas en `ClaudeAgentOptions(mcp_servers={"harness": server}, allowed_tools=["mcp__harness__<tool>"])` (el modelo las ve con el nombre `mcp__<server>__<tool>`). Es seguro que el callback Python de esa herramienta abra y conduzca un `ClaudeSDKClient` anidado (una segunda `Session` independiente) mientras la autenticación por suscripción sigue vigente (bajo `permission_mode="bypassPermissions"`, modo no interactivo) y sin conflicto de event loop ni de sesión con el líder que la invocó.
**Aplicación:** esta es la base técnica que habilita D-026/D-027 (el orchestrator-leader como agente que invoca el bucle interno vía herramienta en-proceso) y, en general, cualquier agente futuro del doble bucle que necesite invocar sub-flujos deterministas o anidados desde una herramienta propia, en vez de delegarlos a un subagente nativo del SDK.

<!--
### L-XXX — Título breve
**Fecha:** YYYY-MM-DD
**Contexto:** qué estaba pasando
**Lección:** qué se aprendió
**Aplicación:** cómo se debe aplicar en adelante
-->
