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
| T-024 | Implementar la primera rebanada vertical del doble bucle: máquina de estados en disco, bootstrap, bucle interno onboarding-reader y puerta de aprobación humana | Implementada |
| T-025 | Prueba manual interactiva end-to-end de `sda start` (bootstrap → editar scope.md a mano → onboarding-reader → rechazar → aprobar) | Implementada |
| T-026 | Fijar explícitamente modelo y esfuerzo de razonamiento del onboarding-reader (Sonnet + effort high) en vez del default implícito del CLI/SDK | Implementada |
| T-027 | Analizar qué implica tener un agente como sesión principal/líder que orqueste todo (Opus + effort high): diseño, impacto en el bucle externo, costo y observabilidad | Implementada |
| T-028 | Implementar el rediseño de T-027: herramientas en-proceso, prompt del orchestrator-leader y refactor de orchestrator.py | Implementada |
| T-029 | Diseñar memoria/persistencia del orchestrator-leader sobre el proyecto destino (avance, tareas, decisiones, lecciones) | No implementada |
| T-030 | Resolver el entrelazado visual entre la salida en streaming y el teclado del usuario en la terminal del orchestrator-leader | Implementada |

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

### T-024 — Implementar la primera rebanada vertical del doble bucle (bootstrap + onboarding-reader + puerta de aprobación humana)
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Diagnóstico previo: T-018/T-020/T-021/T-023 eran "plomería" de infraestructura, no el producto core de `idea.md` (doble bucle REPL, máquina de estados en disco, onboarding con puerta de aprobación humana, evaluación de calidad 4.0). Se pausaron esas tareas y, con aprobación explícita del usuario vía plan mode, se construyó la primera rebanada vertical end-to-end. Archivos nuevos en `src/sda/`: `state.py` (dataclass `HarnessState` + lectura/escritura atómica de `_harness_state.json`: `current_phase`, `active_repl`, `active_subagent`, `transaction_lock`, `pending_approval_file`); `bootstrap.py` (crea `_context/`, `_templates/`, `_prototype/`, `_persistence/`, stub de `scope.md` y copia la plantilla; idempotente); `templates/document-extract-temp.md` (plantilla del entregable con tabla de cobertura §1–§10); `prompts/onboarding_reader.md` (prompt de rol del subagente); `resources.py` (helpers `load_prompt`/`load_template` vía `importlib.resources`, empaquetados como package-data); `evaluator.py` (`evaluate_draft()` stub que siempre aprueba, `QUALITY_THRESHOLD = 4.0` documentado como pendiente de T-011); `orchestrator.py` (clase `Orchestrator`: bucle externo `run`, bucle interno `_conducir_onboarding` reutilizando la misma `Session` viva entre correcciones, puerta humana `_despachar_revision` con comandos `aprobar`/`rechazar <observación>`, cierre `_aprobar` que promueve el documento a `APPROVED`, marca `confirmado_por_humano: si` y sincroniza `_persistence/progress.md`). Modificados: `core/provider.py` y `providers/claude_sdk.py` (`create_session()` ahora acepta `cwd` y `allowed_tools` opcionales, antes fijo a `["ToolSearch"]`); `cli.py` (`sda start` invoca `run_orchestrator`); `repl.py` (se extrajeron `prompt_line()` y `forzar_utf8()` como utilidades reutilizables); `pyproject.toml` (nueva sección `[tool.setuptools.package-data]` para empaquetar los `.md` de `prompts/`/`templates/`). Diseño acordado con el usuario: ver D-020 a D-023. Verificado en vivo contra la suscripción real (sin API key, todo por scripts que llaman directamente a las funciones del orquestador, no vía `sda start` real): (1) bootstrap crea toda la estructura; (2) idempotencia confirmada en una segunda corrida; (3) heurística de "scope vacío" distingue el stub del contenido real del humano; (4) el onboarding-reader leyó un `scope.md` de prueba con ambigüedades deliberadas (medio de pago indeciso, timebox vago, términos inconsistentes) y produjo `document-extract.md` con la tabla §1–§10 correctamente clasificada, citas textuales con ubicación y las 3 ambigüedades listadas sin resolver; (5) el bucle de rechazo (`rechazar <observación>` sobre §9) hizo el ajuste puntual conservando el contexto de la misma sesión interna, sin rehacer el resto; (6) la aprobación promovió el documento a `estado: APPROVED`, `confirmado_por_humano: si`, escribió la marca en `_persistence/progress.md` y el estado global pasó a `READY_FOR_WORK`. Pendiente explícito: prueba manual/interactiva real vía `sda start` en terminal (ver T-025); todas las verificaciones de esta sesión fueron scripts directos, no el flujo CLI real de punta a punta.

### T-025 — Prueba manual interactiva end-to-end de `sda start`
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Pedido explícito del usuario: correr `sda start` de verdad en una terminal (no en script), desde una carpeta de proyecto de prueba, siguiendo el flujo completo construido en T-024: bootstrap → editar `_context/scope.md` a mano → escribir `listo` → revisar el `document-extract.md` generado por el onboarding-reader → probar `rechazar <observación>` → probar `aprobar`. Ninguna de las verificaciones de T-024 usó el flujo `sda start` real; todas llamaron directamente a las funciones internas del orquestador. Nota: no hay carpetas de prueba que preservar en el repo — cualquier prueba usará una carpeta temporal fuera de `TripleS_Harness`.

**Verificación en vivo (2026-07-24):** ejecutado varias veces en terminal real (`sda_test_004`, `sda_test_005`, `sda_test_006`), con el paquete `sda` instalado en modo editable (`pip install -e`) dentro de un entorno virtual en cada carpeta de prueba, fuera del repo. Flujo completo confirmado: bootstrap → edición manual de `_context/scope.md` → señal `listo` → bucle interno onboarding-reader → generación de `_prototype/document-extract.md` → puerta de aprobación humana → `aprobar` → documento bloqueado como `APPROVED`. En la primera corrida (`sda_test_004`) el resumen del onboarding-reader se vio pegado visualmente al comando `aprobar` escrito por el usuario; se confirmó que fue solo un artefacto de que el usuario tecleó su respuesta pegada al texto en la terminal, no un bug de truncamiento ni de lógica. A partir de este hallazgo se hicieron ajustes de UX de mensajería en `orchestrator.py`/`repl.py` (ver D-024), verificados limpios y espaciados en `sda_test_006`. Nota de diseño confirmada (no bug): el comando de continuar requiere coincidencia exacta (D-022); `listo continua` con texto extra no se reconoce, y esto es intencional.

### T-026 — Fijar explícitamente modelo y esfuerzo de razonamiento del onboarding-reader
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

**Implementación (2026-07-24):** se agregó `effort` (además de `model`) al `Provider` ABC (`create_session`) y a `ClaudeSDKProvider` (default de proveedor + override por sesión, pasados a `ClaudeAgentOptions` solo si no son `None`). En `orchestrator.py` se fijaron las constantes `_ONBOARDING_MODEL="sonnet"` y `_ONBOARDING_EFFORT="high"`, cableadas en `_abrir_onboarding`. Verificado en vivo: (1) construcción de opciones correcta (`model=sonnet`, `effort=high`; defaults quedan `None`, sin regresión); (2) llamada real al SDK con esas opciones respondió OK, confirmando que el CLI acepta `--model`/`--effort` y que `effort` funciona sin requerir `thinking` adaptive. Modelo aceptado con el alias `"sonnet"`. Sesión principal/líder (Opus + high) queda diferida a T-027.


Durante la verificación de T-025 se revisó el código (`src/sda/providers/claude_sdk.py`, `src/sda/cli.py`) y se confirmó que hoy el harness NO fija explícitamente ni el modelo de Anthropic ni el esfuerzo de razonamiento para ninguna sesión: `ClaudeSDKProvider()` se instancia sin argumento `model` en `cli.py::_cmd_start`, y `ClaudeAgentOptions` solo setearía `model` si no fuera `None` (nunca ocurre hoy); no existe ningún parámetro de esfuerzo (`effort`) en las opciones actuales. Todo queda delegado al default implícito del CLI/SDK según la suscripción del usuario.

**Decisión del usuario (2026-07-24):** el `onboarding-reader` debe usar **Sonnet + effort `high`**. La configuración del orquestador/sesión principal con Opus + high queda fuera de esta tarea y se traslada a T-027 (análisis), porque hoy el bucle externo (`orchestrator.py::run`) es Python puro y no abre ninguna sesión contra el LLM.

**Alcance de T-026 (solo onboarding-reader):**
- `src/sda/providers/claude_sdk.py`: dar soporte a `effort` (además del `model` ya existente); `create_session` los pasa a `ClaudeAgentOptions` solo si no son `None` (mismo patrón condicional actual). El SDK expone `ClaudeAgentOptions.model` y `ClaudeAgentOptions.effort` con `EffortLevel = low|medium|high|xhigh|max` (verificado vía docs del SDK).
- Mecanismo por-agente: agregar parámetros `model`/`effort` a `create_session(...)` para que cada agente elija su combinación (deja el camino listo para el futuro líder de T-027).
- `src/sda/orchestrator.py::_abrir_onboarding` (~línea 114): pasar `model="sonnet"`, `effort="high"` al crear la sesión interna.
- Verificar antes de cerrar: (a) valor de modelo que acepta el CLI (alias `"sonnet"` vs. id `claude-sonnet-5`); (b) si `effort` funciona por sí solo o requiere además `thinking={"type":"adaptive"}`.
- Verificación funcional: `sda start` end-to-end (bootstrap → onboarding-reader → aprobar) confirmando que el subproceso del CLI recibe `--model` y `--effort`, sin regresiones respecto a T-025.

Sin prioridad urgente; agrupada con las tareas de infraestructura pausadas.

### T-027 — Analizar el agente como sesión principal/líder que orqueste todo
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Tarea de análisis (no de implementación) surgida al acotar T-026. Hoy el bucle externo del orquestador (`orchestrator.py::run`) es Python puro: imprime mensajes y lee el teclado del humano, pero NO abre ninguna sesión contra el LLM. La única sesión real contra Claude es la interna del `onboarding-reader`. El usuario quiere que en el futuro exista un agente "líder" como sesión principal (con **Opus + effort `high`**) que conduzca la conversación con el humano y orqueste el doble bucle, en vez de ser código Python fijo.

Pendiente de analizar (sin implementar aún):
- Diseño: cómo un agente líder conversacional convive con la máquina de estados y los comandos actuales (`listo`, `aprobar`, `rechazar`), y cómo mantiene la observabilidad del bucle interno (Forma A).
- Impacto en `orchestrator.py`, `repl.py` (hoy `run_repl` es código sin uso) y `cli.py`.
- Costo y latencia de tener Opus corriendo de forma persistente en el bucle externo.
- Cómo se cablea Opus + high reutilizando el mecanismo por-agente que deja listo T-026.

**Análisis y spike de verificación (2026-07-24, rama `t-027-sesion-lider`):** se creó la rama `t-027-sesion-lider` a partir de master (decisión del usuario, para descartarla sin tocar master si el enfoque no convence; el merge se decidirá en una sesión futura). Se escribió el documento de diseño `docs/design/T-027-orchestrator-leader.md` (carpeta `docs/design/` nueva), que resuelve el diseño pendiente: el `orchestrator-leader` (Opus + effort high) reemplaza el bucle externo de `Orchestrator.run()` bajo el principio "el LLM decide / las herramientas hacen cumplir"; los efectos peligrosos (estado en disco, lock, puerta de aprobación) quedan encapsulados como efectos laterales deterministas de herramientas en-proceso que el líder invoca, nunca como código que el líder ejecuta directamente. El documento cubre el flujo end-to-end, el contrato de las herramientas del líder, el impacto en el código existente, la generalización a agentes futuros (líder + herramientas como "chasis" reutilizable) y riesgos/trade-offs, además de las decisiones propuestas D-026 a D-029.

Se diseñó y ejecutó en vivo el spike `spikes/t027_herramienta_en_proceso.py`, resultado VERDE: verificó de punta a punta (con un token aleatorio de control) que, bajo autenticación por suscripción y modo no interactivo (`permission_mode="bypassPermissions"`), un líder LLM (Opus + effort high) puede invocar una herramienta EN-PROCESO (`@tool` + `create_sdk_mcp_server` del SDK `claude_agent_sdk` 0.2.126) cuya implementación Python conduce una SEGUNDA `Session` (bucle interno, Sonnet + effort high) de forma observable turno a turno, y que el resultado regresa correctamente al líder. Hallazgo fino despejado: es seguro abrir y conducir un `ClaudeSDKClient` anidado desde dentro del callback de la herramienta del líder (no hay conflicto de event loop ni de sesión). API del SDK confirmada en el spike: `@tool(name, desc, schema)` + `create_sdk_mcp_server("harness", tools=[...])` + `ClaudeAgentOptions(mcp_servers={"harness": server}, allowed_tools=["mcp__harness__<tool>"])`; el nombre de la herramienta ante el modelo sigue el patrón `mcp__<server>__<tool>`.

Con el análisis y el spike verificados, T-027 queda completa como tarea de diseño; la implementación del rediseño se traslada a la nueva T-028.

### T-028 — Implementar el rediseño del orchestrator-leader (T-027)
**Estado:** Implementada
**Fecha creación:** 2026-07-24
**Fecha actualización:** 2026-07-24

Tarea de implementación derivada de T-027, en la misma rama `t-027-sesion-lider`. Paso 2 de §10 del documento de diseño (`docs/design/T-027-orchestrator-leader.md`):
- Crear `src/sda/tools/` con las herramientas en-proceso del líder: `run_inner_loop` (conduce el bucle interno onboarding-reader, moviendo la lógica hoy en `Orchestrator._conducir_onboarding`), `promote_to_approved` (única forma de llevar el documento a `APPROVED`, ver D-028) y `scope_esta_lleno` (valida determinísticamente si el humano ya llenó `scope.md`, ver D-029).
- Crear `src/sda/prompts/orchestrator_leader.md` (system prompt del líder, Opus + effort high).
- Refactorizar `src/sda/orchestrator.py`: mover `_conducir_onboarding` a la herramienta `run_inner_loop`; el bucle externo Python actual (`Orchestrator.run`) es reemplazado por una `Session` del líder que invoca las herramientas.
- Posiblemente extender `Provider.create_session`/`ClaudeSDKProvider` (`src/sda/core/provider.py`, `src/sda/providers/claude_sdk.py`) para aceptar herramientas en-proceso (`mcp_servers`/`allowed_tools` con nombres `mcp__<server>__<tool>`), análogo a como T-026 extendió `model`/`effort`.

Después de implementar: prueba end-to-end en vivo del flujo rediseñado (análoga a T-025, corrida real de `sda start` en terminal) y, si convence, merge de `t-027-sesion-lider` a master.

**Implementación (2026-07-24):** creados `src/sda/core/tool.py` (`InProcessTool`, abstracción SDK-agnóstica: nombre, descripción, parámetros, handler que devuelve texto), `src/sda/tools/__init__.py` y `src/sda/tools/leader_tools.py` (clase `LeaderTools` con las tres herramientas planeadas, moviendo aquí la lógica que antes vivía en `Orchestrator._conducir_onboarding`/`_aprobar`) y `src/sda/prompts/orchestrator_leader.md` (system prompt del líder). `src/sda/orchestrator.py` quedó refactorizado por completo: eliminado el if/elif de fases; construye la sesión del líder con sus herramientas en-proceso y expone el bucle conversacional humano↔líder, con un mensaje de apertura contextual según la fase (`_mensaje_apertura`). `src/sda/core/provider.py` y `src/sda/providers/claude_sdk.py` ganaron el parámetro `in_process_tools` en `create_session` (registradas como servidor MCP en-proceso vía `create_sdk_mcp_server`+`@tool`, nombres `mcp__harness__<tool>`); el SDK sigue importándose solo en `providers/` (D-010 preservado). `src/sda/bootstrap.py` se ajustó para que el stub de `scope.md` ya no exija la palabra exacta "listo" (D-029). Verificado en vivo con prueba end-to-end real (Opus real conduciendo Sonnet real): llegó hasta `document-extract.md` con `estado: APPROVED` + `confirmado_por_humano: si`, fase `READY_FOR_WORK`, lock liberado y `progress.md` sincronizado.

**Hallazgo de seguridad y hardening (2026-07-24):** al probar en una carpeta de proyecto real (fuera del repo), se detectó que las citas del líder (números de línea) eran reales porque el líder tenía en la práctica acceso de lectura sin restricción. Se confirmó (docs oficiales de `claude-agent-sdk` + pruebas en vivo) que `allowed_tools` NO restringe el toolset bajo `permission_mode="bypassPermissions"`: solo auto-aprueba, no quita herramientas; por lo tanto el "sandbox" que se creía tener tanto en el líder como en el onboarding-reader (desde T-024) nunca restringió nada de verdad (ver L-013). El mecanismo real de restricción es `tools=`/`disallowed_tools=`, verificado en vivo (`tools=["Glob"]` impide leer archivos). Se agregó el parámetro `builtin_tools` al contrato `Provider.create_session` (mapea a `tools=` del SDK), como sandbox duro por agente, distinto de `allowed_tools`: el líder pasó a `builtin_tools=["Read","Glob","Grep"]` (solo lectura) y el onboarding-reader de `allowed_tools=[...]` a `builtin_tools=["Read","Glob","Grep","Write"]` (ver D-031). Verificado en vivo en dos pruebas: (1) sandbox duro — sesión de solo lectura, ante orden explícita de crear `HACK.txt`, respondió que no podía y el archivo no se creó; (2) E2E completo post-hardening llegó de nuevo a APPROVED/READY_FOR_WORK, confirmando que las herramientas MCP en-proceso siguen funcionando bajo `builtin_tools` restrictivo y que el onboarding-reader sigue pudiendo escribir su entregable dentro de su sandbox. El merge de `t-027-sesion-lider` a master queda explícitamente pospuesto por el usuario (no se hace en esta sesión).

### T-029 — Diseñar memoria/persistencia del orchestrator-leader sobre el proyecto destino
**Estado:** No implementada
**Fecha creación:** 2026-07-25
**Fecha actualización:** 2026-07-25

Tarea de análisis/diseño (no de implementación) surgida al mejorar la UX de mensajería del líder (T-027/T-028 ya en producción). A medida que el `orchestrator-leader` gana más responsabilidad (hoy onboarding, mañana arquitectura o construcción de features), el usuario quiere que **siempre tenga conocimiento de todo lo hecho en el proyecto destino**: avance, tareas realizadas, decisiones tomadas, lecciones aprendidas. Aplica exclusivamente al **plano del producto `sda`** (el proyecto sobre el que opera, vía `project_dir`), no a `900_persistence/` de este repo (que es memoria de este harness para Claude Code, un plano distinto y ya resuelto).

Hallazgos de la conversación de análisis (2026-07-25), sin implementar aún:

- **Infraestructura semilla ya existe:** `bootstrap.py` ya crea `_persistence/` en todo proyecto destino (junto a `_context/`, `_prototype/`, `_templates/`); hoy solo se usa para una línea de progreso (`_sincronizar_persistencia()` en `leader_tools.py`, al aprobar el onboarding). Es la base natural a extender, no una carpeta nueva que inventar.
- **Recomendación de estructura:** replicar el mismo esquema de archivos que ya usa `900_persistence/` de este repo (`progress.md`, `tasks.md`, `decisions.md`, `lessons.md`, `assumptions.md`, `constraints.md`) dentro de `_persistence/` del proyecto destino — patrón ya validado, no inventar uno nuevo.
- **Descartado explícitamente usar `AGENTS.md`/`CLAUDE.md` para esto.** Son conceptualmente otra cosa (instrucciones para un asistente de código que edita el repo, no bitácora de un producto en ejecución). Además, verificado con la documentación oficial de Claude Code (`https://code.claude.com/docs/en/memory.md`): Claude Code **solo lee `CLAUDE.md`**, no `AGENTS.md` (aunque `CLAUDE.md` puede importar un `AGENTS.md` existente con `@AGENTS.md`). Si el proyecto destino llegara a tener un `CLAUDE.md` propio para la bitácora del líder, correría el riesgo de ser leído automáticamente por Claude Code si el humano abre ese mismo proyecto como asistente de código, mezclando dos roles distintos sin que nadie lo pidiera.
- **Dos huecos concretos a resolver en el diseño futuro:**
  1. *Lectura:* el líder ya tiene `Read/Glob/Grep` (podría leer `_persistence/` hoy), pero `orchestrator_leader.md` (su system prompt) nunca le instruye a hacerlo al arrancar. Hueco de instrucción, barato de cerrar.
  2. *Escritura:* hoy solo hay un escritor determinista de un evento fijo. Falta que el líder pueda registrar decisiones/lecciones mientras conversa. Recomendación: seguir el principio ya usado en el codebase ("el LLM decide, la herramienta hace cumplir", D-026) con herramientas en-proceso acotadas (p. ej. `record_decision`, `record_lesson`, `record_progress`) en vez de un `Write` genérico, para que el formato/append quede garantizado y no se pueda escribir fuera de `_persistence/`.
- **Relación con tareas pausadas:** complementa T-020 (persistencia de la sesión del SDK) sin sustituirla — una bitácora en Markdown no depende de garantías del proveedor, sobrevive a cambios de modelo y es auditable/editable a mano por el humano (mismo patrón que `scope.md`), mientras que T-020 resolvería memoria conversacional fina si algún día se retoma.

Pendiente explícito: diseñar en detalle el contrato de las nuevas herramientas de escritura, qué instrucciones exactas van al prompt del líder para la lectura al arrancar, y si conviene resumir/comprimir `_persistence/` en el mensaje de apertura en vez de dejar que el líder la lea bajo demanda con `Read`.

### T-030 — Resolver el entrelazado visual entre la salida en streaming y el teclado del usuario
**Estado:** Implementada
**Fecha creación:** 2026-07-25
**Fecha actualización:** 2026-07-25

Tarea de diseño/fix surgida al probar en vivo los ajustes de UX de mensajería (streaming vía `on_text` introducido en esta misma sesión, ver `sda/core/session.py::OnText`, `sda/providers/claude_sdk.py::ClaudeSDKSession.send`, `sda/orchestrator.py::_mostrar`). En una prueba real de `sda start`, el humano escribió "listo ya lo actualice" mientras el saludo del líder todavía se estaba imprimiendo, y el resultado en pantalla mostró el final del saludo (*"Cuando termines de escribir y guardes el archivo, avísame por aquí..."*) apareciendo **después** de lo que el humano ya había tecleado, además de un `>` suelto apareciendo entre dos líneas de estado del subagente (`⎿ [onboarding-reader] Trabajando...` / `⎿ [onboarding-reader] Trabajo terminado.`).

**Diagnóstico (sin implementar aún):** no es un bug de lógica — el código es estrictamente secuencial y nunca llama a `input()` antes de terminar de procesar un turno completo. Es un artefacto de terminal: la terminal ecoa las pulsaciones de teclado del humano en tiempo real, de forma independiente a cuándo el programa hace `print()`; si el humano teclea mientras el programa todavía está imprimiendo (o mientras el subagente interno sigue trabajando), los dos flujos se entrelazan visualmente sin que el código tenga control sobre eso. Ya se había observado una vez en T-025 como artefacto aislado. La sospecha es que el streaming introducido en esta sesión (imprimir bloque por bloque a medida que llegan, en vez de todo el turno de una sola vez al final) **amplía la ventana de riesgo**: ahora hay más pausas reales (esperando al modelo, esperando al subagente) entre llamadas a `print()`, dando más oportunidades para que el tecleo del humano se intercale.

**Opciones evaluadas (ninguna implementada):**
1. Mitigación de comportamiento (sin código): pedir al humano que espere a ver el `>` antes de escribir. Barato pero no robusto — cualquier usuario nuevo puede chocar con esto.
2. Descartar el buffer de teclado justo antes de llamar a `input()`. Evita el entrelazado pero borraría silenciosamente lo que el humano ya escribió (mal UX).
3. **Recomendado:** reemplazar `input()` plano por una librería de edición de línea asíncrona (p. ej. `prompt_toolkit`) que mantenga un área de entrada separada del área de salida, de forma que lo tecleado nunca se mezcle visualmente con lo impreso, sin importar el momento. Requiere una dependencia nueva y algo de rediseño de `repl.py::prompt_line`/`orchestrator.py`, pero es la única opción que resuelve el problema de fondo en vez de mitigarlo.

**Decisión del usuario (2026-07-25):** el merge de la rama `t-027-sesion-lider` a `master` queda **bloqueado explícitamente** hasta que esta tarea se resuelva — se suma como condición al bloqueo ya existente desde T-028 (pospuesto por decisión del usuario). No se ha decidido aún cuál opción implementar.

**Implementación y verificación (2026-07-25, misma rama):** se implementó la opción 3 (recomendada): migración de `input()` a `prompt_toolkit`. En `src/sda/repl.py` se eliminaron `prompt_line()` (el `input()` delegado a un hilo con `anyio.to_thread.run_sync`) y el alias público `forzar_utf8()`; se creó la clase `TerminalUI` y el context manager async `terminal_ui(prompt)`: el `PromptSession` de `prompt_toolkit` se mantiene siempre abierto en una tarea de fondo (`_leer_en_bucle`) que encola cada línea tecleada en un memory object stream de anyio con buffer infinito; el bucle de conversación consume con `await ui.leer()` (devuelve `None` ante Ctrl+C/Ctrl+D, sin dejar la tarea de fondo colgada). Todo el bloque va envuelto en `patch_stdout(raw=True)` para que los `print()` se inserten sobre el área de entrada sin escapar los códigos ANSI tenues que ya usa `subagent_line()`. `run_repl()` se migró al mismo mecanismo. `src/sda/orchestrator.py` pasó a usar `terminal_ui("\n> ")`/`ui.leer()` en vez de `prompt_line()` (el `"\n"` conserva la línea en blanco de separación previa). Se agregó `prompt_toolkit` a `pyproject.toml` como dependencia explícita (ya estaba instalada de forma transitiva, 3.0.52). Verificación en dos niveles: (1) spike headless nuevo `spikes/t030_terminal_doble_area.py`, sin credenciales, con entrada simulada de `prompt_toolkit` — dos casos, ambos en verde: el humano teclea dos turnos durante el streaming sin perder ninguno y en orden; Ctrl+D devuelve `None` y cierra limpio; (2) verificación en vivo del usuario en terminal real (`sda start`), confirmando que la superposición desapareció.

**Cambio de comportamiento:** escribir durante un turno del agente deja de ser un accidente visual y pasa a ser una acción soportada — el mensaje se encola y se procesa en orden cuando termina el turno en curso; nada se descarta.

**Iteraciones de UX descartadas durante la implementación:** (1) un prompt dinámico `(trabajando… lo que escribas se enviará al terminar) >` mientras el agente trabajaba — descartado por el usuario porque un prompt que se repinta queda escrito en el scrollback cada vez, ensuciando la transcripción; se eliminó junto con el context manager `ui.ocupado()` que lo alimentaba. (2) recuadrar el área de entrada con `show_frame=True` (imitando la UX de Claude Code) — implementado y verificado técnicamente, pero rechazado por el usuario tras probarlo en vivo ("no se ve muy bien") y revertido por completo; ver también L-014 (bug de `prompt_toolkit` descubierto durante esta prueba). Ver D-034.

El bloqueo de D-033 queda **levantado** en lo técnico. El merge de `t-027-sesion-lider` a master sigue pendiente de confirmación explícita del usuario, porque el bloqueo de T-028 (merge pospuesto por decisión del usuario) puede seguir vigente.

### T-031 — Tolerar errores transitorios de la API en las sesiones del harness
**Estado:** No implementada
**Fecha creación:** 2026-07-25
**Fecha actualización:** 2026-07-25

Tarea surgida de un incidente real durante una prueba de `sda start` (2026-07-25, justo después de cerrar T-030): la llamada a la API falló con un **HTTP 522 de Cloudflare** (`connection_timeout`, origen `api.anthropic.com`, `ray_id` a20bb5de8b05386d). El cuerpo del error venía marcado como `"retryable": true` con `"retry_after": 120`. No es un fallo del harness ni de los cambios de T-030 — es una indisponibilidad temporal del proveedor.

**Hueco detectado:** el harness no maneja errores transitorios de la API. La excepción se propaga desde `sda/providers/claude_sdk.py::ClaudeSDKSession.send` y se lleva por delante el bucle del líder en `sda/orchestrator.py::Orchestrator.run`. Consecuencias:
- Se pierde la sesión viva del líder y, con ella, todo el contexto conversacional acumulado (la sesión de larga vida es justo el mecanismo verificado en T-016 y sobre el que se apoya todo el doble bucle). El humano tiene que reanudar desde el estado en disco (`_harness_state.json`), que es mucho más pobre.
- El turno perdido ya se estaba pagando. Como el líder es Opus con effort high (D-025/D-026), es el componente más caro por turno del sistema.
- Afecta también al bucle interno (`run_inner_loop`, conducido por nuestro propio código, D-027), donde un fallo a mitad de la generación del borrador deja el trabajo del `onboarding-reader` a medias.

**Dirección propuesta (sin diseñar en detalle todavía):** reintento con backoff exponencial en la capa del proveedor (`ClaudeSDKProvider`/`ClaudeSDKSession`), que es la frontera correcta: mantiene la lógica de resiliencia fuera del dominio y del orquestador, respetando la abstracción `Provider`. Puntos a resolver en el diseño:
- Distinguir errores **reintentables** (5xx, timeouts de red, 429) de los **definitivos** (autenticación, petición inválida), para no reintentar en balde lo que nunca va a funcionar.
- Respetar el `retry_after` que venga en el error cuando exista, en vez de imponer siempre nuestra propia cadencia.
- Verificar primero **qué reintenta ya el Agent SDK por su cuenta**, para no duplicar backoff sobre backoff.
- Decidir qué se le muestra al humano mientras se reintenta. Cuidado con la lección de T-030/D-034: nada que se repinte en el prompt, porque queda escrito en el scrollback. Si hace falta señal visible, la vía limpia es `bottom_toolbar` de `prompt_toolkit`.
- Definir el comportamiento cuando se agotan los reintentos: idealmente **no** matar la sesión del líder, sino informar al humano y devolverle el control para que reintente el turno a mano, conservando el contexto.

**Relación con otras tareas:** independiente de T-029 (memoria del líder en el proyecto destino), aunque ambas atacan la misma fragilidad de fondo — que hoy toda la memoria de trabajo vive en una sesión en RAM que un error puede borrar. También se relaciona con T-020 (persistir/reanudar conversaciones del SDK): si T-020 se retomara algún día, un fallo irrecuperable dejaría de ser tan costoso.
