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

<!--
### L-XXX — Título breve
**Fecha:** YYYY-MM-DD
**Contexto:** qué estaba pasando
**Lección:** qué se aprendió
**Aplicación:** cómo se debe aplicar en adelante
-->
