# Tasks

> Registro de tareas del proyecto. Código estilo `T-XXX` (tres dígitos).
> Estados válidos: `Implementada` | `No implementada` | `Cancelada/Suspendida`

## Índice

- [Índice de tareas](#índice-de-tareas)
- [Detalle de tareas](#detalle-de-tareas)

## Índice de tareas

| Código | Título | Estado |
|--------|--------|--------|
| T-001 | Crear carpeta 900_persistence con 6 archivos base | Implementada |
| T-002 | Agregar estructura de índice a los 6 archivos de 900_persistence | Implementada |
| T-003 | Crear skill session-start-protocol y agente session-starter | Implementada |
| T-004 | Crear skill session-end-protocol y agente session-closer | Implementada |
| T-005 | Eliminar duplicación entre agentes y sus skills correspondientes | Implementada |
| T-006 | Crear CLAUDE.md con protocolo obligatorio de inicio/cierre de sesión | Implementada |
| T-007 | Investigar y definir alcance real del proyecto TripleS_Harness | Implementada |
| T-008 | Confirmar explícitamente que el harness será un programa Python propio (no config sobre CLI de Claude Code) | Implementada |
| T-009 | Revisar ejemplos previos del usuario y verificar viabilidad de autenticación por suscripción con el Agent SDK | Implementada |
| T-010 | Definir si el soporte multi-vendor (Codex u otros) es restricción de v1 o meta futura | No implementada |
| T-011 | Definir rúbrica del evaluador de calidad y origen del umbral 4.0 de idea.md | No implementada |
| T-012 | Crear pyproject.toml del paquete sda (dependencias claude-agent-sdk, anyio; console script sda = sda.cli:main) | Implementada |
| T-013 | Crear src/sda/cli.py con main() y sda --help funcional, más __main__.py | Implementada |
| T-014 | Crear src/sda/core/provider.py (Provider ABC) y src/sda/core/session.py (Session ABC) | Implementada |
| T-015 | Crear src/sda/providers/claude_sdk.py (ClaudeSDKProvider) con la política de autenticación por suscripción | Implementada |
| T-016 | Spike: abrir sesión persistente sobre suscripción, confirmar respuesta y conservación de contexto entre turnos | Implementada |
| T-017 | Spike: verificar descubrimiento de skills empaquetadas dentro de sda cuando el cwd es el proyecto destino | No implementada |
| T-018 | Ampliar session-start-protocol para que lea documentos de contexto en la raíz del proyecto (p. ej. idea.md) | No implementada |
| T-019 | Configurar .gitignore, protocolo obligatorio de commit/push en session-closer, e inicializar repo git conectado a GitHub | Implementada |
| T-020 | Persistir y reanudar conversaciones del harness entre ejecuciones (más allá de la memoria del proceso vivo) | No implementada |
| T-021 | Promover a producción el plugin local de skills de sda (src/sda/plugin/, resolución con importlib, ClaudeSDKProvider.create_session con plugins/skills) | No implementada |
| T-022 | Implementar el REPL interactivo real del subcomando `sda start` (src/sda/repl.py) | Implementada |
| T-023 | Capturar uso de tokens y costo por turno en TurnResult (ResultMessage del SDK) | No implementada |

## Detalle de tareas

### T-001 — Crear carpeta 900_persistence con 6 archivos base
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Carpeta `900_persistence/` con progress.md, tasks.md, lessons.md, decisions.md, assumptions.md, constraints.md.

### T-002 — Agregar estructura de índice a los 6 archivos de 900_persistence
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Cada archivo tiene un índice/tabla al inicio para localizar información sin leer el archivo completo.

### T-003 — Crear skill session-start-protocol y agente session-starter
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Skill en `.claude/skills/session-start-protocol/SKILL.md` (lectura obligatoria de progress.md y tasks.md, a demanda del resto). Agente en `.claude/agents/session-starter.md` (modelo haiku, color rojo), se activa con frases tipo "iniciemos la sesión".

### T-004 — Crear skill session-end-protocol y agente session-closer
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Skill en `.claude/skills/session-end-protocol/SKILL.md` (actualización obligatoria de progress.md y tasks.md, a demanda del resto). Agente en `.claude/agents/session-closer.md` (modelo sonnet, color azul), se activa con frases tipo "cerremos la sesión".

### T-005 — Eliminar duplicación entre agentes y sus skills correspondientes
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Los agentes session-starter y session-closer ya no repiten las reglas de las skills; solo las invocan y conservan lo específico del agente (mostrar resumen en pantalla, no inventar).

### T-006 — Crear CLAUDE.md con protocolo obligatorio de inicio/cierre de sesión
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

`CLAUDE.md` en la raíz exige invocar session-starter al iniciar/reanudar sesión y session-closer al cerrarla.

### T-007 — Investigar y definir alcance real del proyecto TripleS_Harness
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Se descubrió que `idea.md` (raíz del proyecto) ya contenía la definición de alcance/arquitectura, no leída por el `session-start-protocol` (ver L-002). A partir de esa lectura y una conversación de alineación con el usuario quedó acordado conceptualmente: el harness es una capa de orquestación con dos agent loops anidados; se implementará como programa Python propio con el Agent SDK de Anthropic; `900_persistence/` y `_persistence/` son memorias distintas que no deben unificarse; el evaluador es un agente aparte; el alcance de v1 es el flujo end-to-end de `idea.md`. El alcance y la arquitectura quedaron acordados de forma completa en esta sesión posterior (ver D-002 a D-016, A-001, A-002 resueltos).

### T-008 — Confirmar explícitamente que el harness será un programa Python propio
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

El usuario confirmó explícitamente que el harness es un programa Python propio que usa el Agent SDK (no una capa de configuración sobre el CLI de Claude Code). Ver A-002 (resuelto).

### T-009 — Revisar ejemplos previos y verificar autenticación por suscripción con el Agent SDK
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

El usuario mostró un repo experimental previo (`Harness_TripleS`, ver D-007) donde la autenticación por suscripción (no API key) con el Agent SDK quedó verificada en vivo varias veces sobre la suscripción real del usuario, y también se confirmó contra documentación oficial actual (`/anthropics/claude-agent-sdk-python`, vía ctx7). Ver A-001 (resuelto), L-004, C-002, C-003. Adicionalmente se verificó que un agente puede invocar otros agentes (subagentes vía `AgentDefinition` y observabilidad por `parent_tool_use_id`).

### T-010 — Definir si el soporte multi-vendor es restricción de v1 o meta futura
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Hoy el harness usa Claude Code; a futuro se contempla Codex u otros. No se definió formalmente si esto debe soportarse desde v1 o es una meta posterior, aunque en la práctica quedó implícitamente resuelto como "futuro": un solo proveedor (el SDK de Claude) por ahora, con `Provider` como ABC para no clausurar el diseño frente a Codex (ver D-008, D-010). Conviene confirmarlo explícitamente con el usuario. Ver A-003.

### T-011 — Definir rúbrica del evaluador de calidad y origen del umbral 4.0
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

`idea.md` menciona un umbral de calidad "4.0" sin que se haya definido la rúbrica del evaluador ni de dónde sale ese número. Además, un evaluador basado en LLM también consume suscripción y puede encarecer el bucle interno (ver C-001).

### T-012 — Crear pyproject.toml del paquete sda
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-24

Configurado el paquete `sda`, con dependencias (`claude-agent-sdk`, `anyio`), console script `sda = "sda.cli:main"`, build backend `setuptools` con layout `src/`, y `requires-python = ">=3.12"`. Creados `pyproject.toml` y `src/sda/__init__.py`. Verificado en vivo: `pip install -e .` instala correctamente, `import sda` funciona, y el comando `sda.exe` queda registrado (fallará hasta T-013, cuando exista `sda.cli:main`). Ver D-013, D-014.

### T-013 — Crear src/sda/cli.py y __main__.py
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-24

Creados `src/sda/cli.py` (parser con `argparse`: `build_parser()`, `main()`, `--version` vía `importlib.metadata.version("sda")`, y subcomando placeholder `start` que imprime "no implementado aún") y `src/sda/__main__.py` (habilita `python -m sda`). Verificado en vivo: `sda --help`, `sda --version` (→ `sda 0.1.0`), `sda start`, `python -m sda --help` y `sda` sin argumentos funcionan y terminan con código 0. Decisión de diseño: `argparse` (stdlib, sin dependencias nuevas) + esqueleto con subcomando placeholder (ver D-017). Ver D-014.

### T-014 — Crear core/provider.py y core/session.py
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-24

Creados `src/sda/core/__init__.py`, `src/sda/core/session.py` (`TurnResult` dataclass con campo `text`; `Session` ABC con `async send() -> TurnResult`, `async close()` y protocolo `async with` concreto vía `__aenter__`/`__aexit__`) y `src/sda/core/provider.py` (`Provider` ABC con `create_session(*, system_prompt=None) -> Session`). API asíncrona (el SDK `ClaudeSDKClient` es totalmente async; se verificó su interfaz en vivo). Verificado: imports OK, ambas ABCs lanzan `TypeError` al instanciarse directamente, una subclase de juguete ejecuta `send`→`TurnResult` y `async with` invoca `close`, y `core/` no importa `claude_agent_sdk` ni `sda.providers` (D-010, confirmado por grep: solo menciones en docstrings). Decisión de diseño registrada en D-018. Ver D-009, D-010, D-016.

### T-015 — Crear providers/claude_sdk.py
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-24

Creados `src/sda/providers/__init__.py` y `src/sda/providers/claude_sdk.py` con `ClaudeSDKProvider` (subclase concreta de `Provider`) y `ClaudeSDKSession` (subclase concreta de `Session`) sobre `claude_agent_sdk`. Aplica la política de autenticación por suscripción verificada (helper `_subscription_env()`: hace `pop` de `ANTHROPIC_API_KEY`/`CLAUDE_CODE_OAUTH_TOKEN` en el proceso padre y las sobrescribe a `""` en `ClaudeAgentOptions.env`, ver A-001, L-004, C-002, C-003), `permission_mode="bypassPermissions"` y `allowed_tools=["ToolSearch"]` (C-002). `send()` implementado sobre `client.query()` + `client.receive_response()`; `close()` sobre `client.disconnect()` (D-018). Conexión perezosa: se conecta en el primer `send()` y se mantiene abierta entre turnos. Verificado en vivo: subclassing correcto de `Provider`/`Session`, grep confirmando que `core/` no importa `claude_agent_sdk` (D-010 respetado), smoke test de 1 turno contra la suscripción real, y verificación manual adicional desde un proyecto externo (`sda_test_002`, fuera de este repo) instalando el paquete en modo editable y ejecutando una conversación multi-turno. Ver D-008, D-010.

### T-016 — Spike: sesión persistente sobre suscripción con contexto entre turnos
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-24

Spike creado en `spikes/t016_sesion_persistente.py`: confirma que una misma `Session` (sin reconectar entre turnos) conserva el contexto de un turno a otro. Ejecutado en vivo dentro del repo con resultado exitoso: T1 "ok", T2 "Verde" (recordó que el color favorito mencionado en T1 era verde), assert de conservación de contexto pasó correctamente. Ver D-011.

### T-017 — Spike: verificación del descubrimiento de skills empaquetadas
**Estado:** Implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-24

Spike creado en `spikes/t017_skills_empaquetadas.py` con fixtures en `spikes/t017_fixtures/` (skill "pelada" en `skill_bare/color-secreto-bare/SKILL.md`; plugin local en `plugin/` con `.claude-plugin/plugin.json` + `skills/color-secreto-plugin/SKILL.md`). Ejecutado en vivo desde un `cwd` temporal EXTERNO (fuera de este repo, simulando el proyecto destino) con dos casos: (1) BASELINE — skill "pelada" estilo `src/sda/skills/<n>/SKILL.md` con `skills="all"` sin plugins → el modelo respondió `NO-LA-SE`, confirmando que NO se descubre desde un cwd externo; (2) PLUGIN — la misma skill empaquetada en un plugin local (`plugins=[{"type":"local","path":...}]`) → el modelo respondió `SKILL-T017-PLUGIN-OK`, confirmando que el plugin local SÍ expone la skill independientemente del cwd. Ambos asserts pasaron. Hallazgo verificado también contra la documentación oficial del SDK vía ctx7: el parámetro `skills` de `ClaudeAgentOptions` auto-configura `setting_sources=["user","project"]`, que solo miran `~/.claude/skills/` y `<cwd>/.claude/skills/`, no un directorio interno del paquete instalado. Resuelve A-004 (VERIFICADO) y obliga a corregir D-016 (ver D-016 corregido) y añadir D-019. El material de `spikes/t017_*` se deja en el repo por ahora (no se borra ni promueve todavía, conforme a D-011) para que el usuario pueda re-ejecutarlo; su borrado/promoción a producción queda para T-021.

### T-018 — Ampliar session-start-protocol para leer documentos de contexto en la raíz del proyecto
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Tarea pendiente derivada de L-002: el `session-start-protocol` solo lee `900_persistence/` y no documentos de contexto en la raíz del proyecto (p. ej. `idea.md`). Sigue vigente y sin corregir; se propone ampliarlo para evitar diagnósticos incorrectos al reanudar sesiones futuras.

### T-019 — Configurar .gitignore, protocolo de commit/push en session-closer, e inicializar repo git
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Se creó `.gitignore` en la raíz. Se actualizó la skill `.claude/skills/session-end-protocol/SKILL.md` con una sección obligatoria de "Commit y push obligatorios" al cierre de cada sesión, apuntando al remoto `https://github.com/jdrodriguez1000/TripleS_Harness.git` (`origin`). Se actualizó `.claude/agents/session-closer.md` dándole acceso a la herramienta Bash y añadiendo la confirmación de commit/push en su resumen final, con prohibición explícita de `git push --force` u operaciones destructivas. Se inicializó el repo git local (`git init`), se conectó `origin` (repo ya existía vacío en GitHub) y se hizo el primer commit y push a `master` (15 archivos).

### T-020 — Persistir y reanudar conversaciones del harness entre ejecuciones
**Estado:** No implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Durante T-016 se confirmó que la conversación multi-turno (contexto conservado entre turnos) funciona mientras el proceso Python está vivo, usando el mismo objeto `Session` sin reconectar. Pero esa conversación se pierde por completo al cerrar el proceso: hoy no existe ningún mecanismo que guarde el historial de mensajes en disco, ni un identificador de sesión/conversación que permita al SDK reconectar a la misma charla en una ejecución posterior. Todo vive en memoria del `ClaudeSDKClient` mientras el proceso corre. Falta investigar si el SDK subyacente soporta reanudar una conversación por `session_id` u otro mecanismo, y diseñar cómo se persistiría dicho estado (fuera del alcance de T-015/T-016). Nota: esto es distinto de la persistencia de `900_persistence/`, que es memoria del proyecto/harness en sí, no de las conversaciones que el harness genera con el modelo. Ver C-005.

### T-021 — Promover a producción el plugin local de skills de sda
**Estado:** No implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Tarea derivada del hallazgo de T-017/D-019: crear el plugin real `src/sda/plugin/` (`.claude-plugin/plugin.json` + `skills/<nombre>/SKILL.md`) dentro del paquete `sda`, y la lógica que resuelve su ruta con `importlib` (en vez de una ruta de spike hardcodeada) para pasarla como `plugins=[{"type":"local","path":...}]` en las opciones del proveedor. Requiere ampliar `ClaudeSDKProvider.create_session` para aceptar/pasar `plugins` y `skills`. Fuera de alcance del spike (D-011): promoción a producción pendiente.

### T-022 — Implementar el REPL interactivo real del subcomando `sda start`
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Creado `src/sda/repl.py` con la función async `run_repl(provider)`: abre `async with provider.create_session()`, lee el teclado sin bloquear el event loop (`anyio.to_thread.run_sync(input, "tú> ")`), envía cada turno con `session.send()` e imprime la respuesta (`resultado.text`); termina con `salir`/`exit`/`quit` o con EOF/Ctrl-C. Incluye el helper `_forzar_utf8()` que reconfigura `stdout`/`stdin` a UTF-8 con `errors="replace"` para evitar `UnicodeEncodeError` con emojis en consola Windows (ver L-007). Se modificó `src/sda/cli.py`: `_cmd_start` ahora arranca `anyio.run(run_repl, ClaudeSDKProvider())` en vez del placeholder anterior, y se corrigió el texto de ayuda del subcomando `start` a "Abre una sesión interactiva en la carpeta actual.". Verificado en vivo por el usuario desde una carpeta externa (`sda_test_003`) con el paquete instalado en modo editable: conversación multi-turno real sostenida por teclado, con memoria correcta de nombre, ciudad (corregida en vivo) y color a lo largo de varios turnos, y respuesta honesta ("no lo sé") ante un dato nunca proporcionado, sin alucinar. Sin cambios en `core/`, `providers/` ni `pyproject.toml`.

### T-023 — Capturar uso de tokens y costo por turno en TurnResult
**Estado:** No implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

El bucle de `ClaudeSDKSession.send()` (`src/sda/providers/claude_sdk.py`) hoy solo filtra `AssistantMessage`/`TextBlock` de `client.receive_response()` y descarta el `ResultMessage` que el SDK emite al final de cada turno. Ese `ResultMessage` trae `usage` (tokens de entrada/salida/caché), `total_cost_usd`, `model_usage`, `num_turns`, `stop_reason` y también `session_id`. Falta: (a) capturar el `ResultMessage` en el bucle de `send()`, y (b) ampliar el dataclass `TurnResult` (`src/sda/core/session.py`) para llevar esa metadata además de `text` — extensión que su docstring ya prevé explícitamente (ver D-018). Es la observabilidad que necesita el bucle interno/evaluador (relacionado con T-011 y el umbral "4.0" de `idea.md`). El `session_id` de ese mismo `ResultMessage` es además una pieza clave para T-020 (persistencia/reanudación de conversaciones entre ejecuciones).
