# Decisions

> Decisiones tomadas durante la construcción y ejecución del proyecto.

## Índice

- [D-001 — Modelos y colores diferenciados para agentes de inicio/cierre de sesión](#d-001--modelos-y-colores-diferenciados-para-agentes-de-iniciocierre-de-sesión)
- [D-002 — Arquitectura del harness: dos agent loops anidados (no "REPLs")](#d-002--arquitectura-del-harness-dos-agent-loops-anidados-no-repls)
- [D-003 — Implementación como programa Python propio con el Agent SDK](#d-003--implementación-como-programa-python-propio-con-el-agent-sdk)
- [D-004 — Separación entre 900_persistence (memoria de construcción) y _persistence (memoria del harness en uso)](#d-004--separación-entre-900_persistence-memoria-de-construcción-y-_persistence-memoria-del-harness-en-uso)
- [D-005 — El evaluador de calidad es un agente aparte del orchestrator-leader](#d-005--el-evaluador-de-calidad-es-un-agente-aparte-del-orchestrator-leader)
- [D-006 — Alcance de v1: flujo end-to-end descrito en idea.md](#d-006--alcance-de-v1-flujo-end-to-end-descrito-en-ideamd)
- [D-007 — Continuar la construcción en TripleS_Harness, no migrar a Harness_TripleS](#d-007--continuar-la-construcción-en-triples_harness-no-migrar-a-harness_triples)
- [D-008 — Un solo camino de proveedor: el SDK, no el CLI](#d-008--un-solo-camino-de-proveedor-el-sdk-no-el-cli)
- [D-009 — Una sola cadena de abstracción de conversación: Provider (fábrica) + Session (conversación)](#d-009--una-sola-cadena-de-abstracción-de-conversación-provider-fábrica--session-conversación)
- [D-010 — El SDK solo se importa dentro de providers/](#d-010--el-sdk-solo-se-importa-dentro-de-providers)
- [D-011 — spikes/ vive fuera de src/ y tiene fecha de caducidad](#d-011--spikes-vive-fuera-de-src-y-tiene-fecha-de-caducidad)
- [D-012 — tools/ no conoce agents/, y agents/ no implementa herramientas](#d-012--tools-no-conoce-agents-y-agents-no-implementa-herramientas)
- [D-013 — Nombre del paquete: sda](#d-013--nombre-del-paquete-sda)
- [D-014 — Punto de entrada: console script sda.cli:main más __main__.py, sin main.py suelto](#d-014--punto-de-entrada-console-script-sdaclimain-más-__main__py-sin-mainpy-suelto)
- [D-015 — Convención de código: identificadores/archivos en inglés, docstrings/comentarios en español](#d-015--convención-de-código-identificadoresarchivos-en-inglés-docstringscomentarios-en-español)
- [D-016 — Estructura de carpetas del proyecto acordada](#d-016--estructura-de-carpetas-del-proyecto-acordada)

## Detalle

### D-001 — Modelos y colores diferenciados para agentes de inicio/cierre de sesión
**Fecha:** 2026-07-23
**Decisión:** `session-starter` usa modelo `haiku` y color rojo (solo lee y resume, tarea liviana); `session-closer` usa modelo `sonnet` y color azul (debe editar/sintetizar contenido en varios archivos, tarea más compleja).
**Razón:** el costo/latencia de inicio de sesión debe ser mínimo porque ocurre en cada arranque; el cierre requiere mejor criterio de síntesis para no perder o inventar información.
**Alternativas consideradas:** usar el mismo modelo para ambos agentes.
**Impacto:** ref T-003, T-004

### D-002 — Arquitectura del harness: dos agent loops anidados (no "REPLs")
**Fecha:** 2026-07-23
**Decisión:** la arquitectura del harness se describe como dos "agent loops anidados": un loop externo (`orchestrator-leader`) que es el único que habla con el humano, y un loop interno que es un sandbox donde corre un subagente supervisado turno a turno, con el propósito de poder observarlo y evaluarlo.
**Razón:** se descartó explícitamente el término "REPLs" porque no son sesiones interactivas de terminal sino bucles programáticos dentro del propio harness.
**Alternativas consideradas:** llamarlos "REPLs" (descartado por impreciso).
**Impacto:** ref T-007.

### D-003 — Implementación como programa Python propio con el Agent SDK
**Fecha:** 2026-07-23
**Decisión:** el harness se implementará como un programa Python propio que usa el Agent SDK de Anthropic y corre sus propios agent loops, y no como una capa de configuración sobre el CLI de Claude Code.
**Razón:** inferencia del agente a partir de las respuestas del usuario sobre Python y agent loops durante la conversación de alineación.
**Alternativas consideradas:** construir el harness como configuración/orquestación sobre el CLI existente de Claude Code (no descartada explícitamente por el usuario, pero contradicha por sus respuestas).
**Impacto:** ref T-007, T-008 (pendiente confirmación explícita), A-002. Consecuencia directa: los agentes del harness (`orchestrator-leader`, `onboarding-reader`, evaluador) serán código/prompts en Python, no archivos `.claude/agents/*.md`; los actuales `session-starter.md`/`session-closer.md` y sus skills son andamio para construir el harness, no el mecanismo final del harness.

### D-004 — Separación entre 900_persistence (memoria de construcción) y _persistence (memoria del harness en uso)
**Fecha:** 2026-07-23
**Decisión:** `900_persistence/` es la memoria de la construcción del propio harness (este proyecto); `_persistence/` será la memoria que el harness genere en los proyectos donde se use. Son conceptos distintos y no deben unificarse, ni siquiera en formato (900_persistence usa .md, `_persistence` del harness usaría .json).
**Razón:** evitar confundir la infraestructura de desarrollo del harness con el producto que el harness genera.
**Alternativas consideradas:** unificar ambas memorias en un solo esquema.
**Impacto:** ref T-007.

### D-005 — El evaluador de calidad es un agente aparte del orchestrator-leader
**Fecha:** 2026-07-23
**Decisión:** la evaluación de calidad interna del trabajo del loop interno la hará un agente evaluador independiente, no el `orchestrator-leader`.
**Razón:** separar responsabilidades entre quien orquesta/habla con el humano y quien juzga la calidad del trabajo producido.
**Alternativas consideradas:** que el propio `orchestrator-leader` evalúe.
**Impacto:** ref T-007, T-011 (rúbrica pendiente), C-001 (costo de evaluar con LLM).

### D-006 — Alcance de v1: flujo end-to-end descrito en idea.md
**Fecha:** 2026-07-23
**Decisión:** el alcance de la v1 del harness es el flujo end-to-end completo descrito en `idea.md` (onboarding-reader → `document-extract.md` aprobado por el humano), como vehículo de aprendizaje y base extensible poco a poco. La distribución será en Python con un script instalador que permita invocar el harness desde cualquier carpeta/terminal; se irán agregando más agentes sobre la misma maquinaria con el tiempo.
**Razón:** acotar el primer alcance a algo verificable y ya documentado en `idea.md`, en vez de expandir el diseño antes de validar la base técnica.
**Alternativas consideradas:** ninguna alternativa de alcance fue discutida; se aceptó el flujo ya propuesto en `idea.md`.
**Impacto:** ref T-007.

### D-007 — Continuar la construcción en TripleS_Harness, no migrar a Harness_TripleS
**Fecha:** 2026-07-23
**Decisión:** el usuario mostró un repositorio previo del mismo proyecto en `C:\Users\USUARIO\Documents\Company_TripleS\Harness_TripleS\scripts` (nombre casi invertido), mucho más avanzado: repo Git con 16 commits, paquete Python `soda` instalable, 190 tests verdes, `ruff` limpio, `soda init`/`soda start` funcionando y REPL de orquestador con contexto persistente verificado en vivo, con su propio `900_persistence/` hasta D-041/L-020/T-029. Se decide continuar la construcción en este repo (`TripleS_Harness`) y tratar el otro repo como un experimento del que solo se toman dos hallazgos técnicos verificados (autenticación por suscripción y delegación entre agentes, ver A-001 y punto de subagentes).
**Razón:** el usuario prefirió no adoptar el repo experimental completo (con su desorden de dos caminos vivos, ver L-003) y reconstruir limpio en `TripleS_Harness` aplicando las lecciones ya aprendidas.
**Alternativas consideradas:** migrar/continuar directamente sobre `Harness_TripleS`, descartada por el usuario.
**Impacto:** ref T-009. El repo `Harness_TripleS` no es la base de código de este proyecto; solo aporta conocimiento técnico ya extraído y documentado aquí.

### D-008 — Un solo camino de proveedor: el SDK, no el CLI
**Fecha:** 2026-07-23
**Decisión:** no se construye un proveedor por CLI. El único camino de implementación es el Agent SDK de Anthropic (`claude-agent-sdk`), que autentica con suscripción y cubre todo lo que el CLI hacía, más sesión persistente y subagentes.
**Razón:** evitar repetir el error diagnosticado en el repo anterior de mantener dos caminos vivos a la vez (CLI y SDK), que causó el desorden (ver L-003). El camino CLI es estrictamente inferior al del SDK para este proyecto.
**Alternativas consideradas:** mantener un proveedor CLI como respaldo o alternativa; descartada.
**Impacto:** ref T-014 (`core/provider.py`), T-015 (`providers/claude_sdk.py`).

### D-009 — Una sola cadena de abstracción de conversación: Provider (fábrica) + Session (conversación)
**Fecha:** 2026-07-23
**Decisión:** `Provider` es la fábrica de sesiones y `Session` es la conversación; un disparo de un solo turno es simplemente una sesión de un turno. No habrá dos abstracciones paralelas para "un disparo" y "una sesión multi-turno".
**Razón:** en el repo anterior existían dos abstracciones paralelas (`Provider` de un disparo + `Sesion` multi-turno) que dividían el camino y contribuían al desorden (ver L-003).
**Alternativas consideradas:** mantener abstracciones separadas para disparo único y sesión multi-turno; descartada.
**Impacto:** ref T-014 (`core/provider.py`, `core/session.py`).

### D-010 — El SDK solo se importa dentro de providers/
**Fecha:** 2026-07-23
**Decisión:** `claude_agent_sdk` solo se importa dentro del paquete `sda/providers/`. Ningún otro módulo del proyecto (core, tools, agents, cli, app) conoce el SDK directamente.
**Razón:** aislar el acoplamiento con el SDK de Anthropic en un solo punto para no clausurar el diseño frente a otros proveedores futuros (p. ej. Codex, ver T-010) y para mantener una sola cadena de abstracción clara.
**Alternativas consideradas:** ninguna; se adopta desde el inicio del diseño.
**Impacto:** ref T-015, D-016 (estructura de carpetas).

### D-011 — spikes/ vive fuera de src/ y tiene fecha de caducidad
**Fecha:** 2026-07-23
**Decisión:** los experimentos de verificación técnica (spikes) viven en `spikes/`, fuera de `src/`. Un spike que sobrevive a la pregunta que debía responder se convierte en deuda: al responderla, o se promueve a producto dentro de `src/` o se borra.
**Razón:** evitar que código experimental quede enterrado indefinidamente en el árbol de producción, como ocurrió de forma implícita en el repo anterior.
**Alternativas consideradas:** mezclar spikes dentro de `src/` marcados de alguna forma; descartada por riesgo de confusión.
**Impacto:** ref T-016, T-017 (spikes planeados para la próxima sesión).

### D-012 — tools/ no conoce agents/, y agents/ no implementa herramientas
**Fecha:** 2026-07-23
**Decisión:** `tools/` no importa ni conoce nada de `agents/`; `agents/` solo nombra/referencia herramientas (built-in o propias), nunca implementa su lógica.
**Razón:** mantener una separación clara de responsabilidades entre catálogo de herramientas y definición de agentes, evitando acoplamientos cruzados como los que oscurecieron el repo anterior.
**Alternativas consideradas:** ninguna; se adopta desde el inicio del diseño.
**Impacto:** ref D-016 (estructura de carpetas: `tools/`, `agents/`).

### D-013 — Nombre del paquete: sda
**Fecha:** 2026-07-23
**Decisión:** el paquete Python del harness se llamará `sda` (Software Development Agentic). El repo experimental anterior usaba `soda`.
**Razón:** decisión de nombre del usuario para este proyecto, distinguiéndolo del experimento previo.
**Alternativas consideradas:** reutilizar el nombre `soda` del repo experimental; descartada.
**Impacto:** ref T-012 (`pyproject.toml`), D-014, D-016.

### D-014 — Punto de entrada: console script sda.cli:main más __main__.py, sin main.py suelto
**Fecha:** 2026-07-23
**Decisión:** el punto de entrada es un console script declarado en `pyproject.toml` (`[project.scripts] sda = "sda.cli:main"`), más un `__main__.py` para permitir `python -m sda` en desarrollo. No habrá un `main.py` suelto en la raíz del proyecto.
**Razón:** convención estándar de empaquetado Python para un CLI instalable, evitando puntos de entrada ambiguos.
**Alternativas consideradas:** un script `main.py` en la raíz; descartada.
**Impacto:** ref T-012, T-013. Flujo acordado: `sda start` → console script → `src/sda/cli.py::main()` → `src/sda/app.py` (arma la flota y corre el agent loop externo) → `providers/claude_sdk.py` (abre la sesión persistente sobre suscripción).

### D-015 — Convención de código: identificadores/archivos en inglés, docstrings/comentarios en español
**Fecha:** 2026-07-23
**Decisión:** los identificadores y nombres de archivo del código se escriben en inglés; los docstrings y comentarios se escriben en español. Se adopta desde el primer archivo del proyecto.
**Razón:** en el repo anterior esta convención no se adoptó desde el inicio y costó tareas de limpieza dedicadas para migrarla después.
**Alternativas consideradas:** decidirlo más adelante o dejarlo libre por archivo; descartada por el riesgo ya observado en el repo anterior.
**Impacto:** aplica a todo el código nuevo desde T-012 en adelante.

### D-016 — Estructura de carpetas del proyecto acordada
**Fecha:** 2026-07-23
**Decisión:** se acuerda la siguiente estructura de carpetas para `TripleS_Harness`:
```
TripleS_Harness/
├── pyproject.toml
├── src/sda/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                  punto de entrada, main()
│   ├── app.py                  arma la flota y corre el bucle externo
│   ├── core/
│   │   ├── provider.py         Provider (ABC) — fábrica de sesiones
│   │   ├── session.py          Session (ABC) — conversación multi-turno
│   │   ├── fleet.py            único punto agente → modelo
│   │   └── state.py            _harness_state.json (máquina de estados)
│   ├── providers/
│   │   └── claude_sdk.py       ClaudeSDKProvider (el único por ahora)
│   ├── tools/
│   │   ├── builtin.py          nombres de las del CLI (Bash, Read, Edit…)
│   │   ├── memory.py           herramienta propia con @tool
│   │   └── catalog.py          catálogo único que unifica ambas
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── onboarding_reader.py
│   │   └── evaluator.py
│   ├── skills/
│   │   └── <nombre>/SKILL.md
│   └── templates/
│       └── _persistence/
├── tests/
├── spikes/
├── 900_persistence/
├── idea.md
└── CLAUDE.md
```
**Razón:** materializar en carpetas concretas las decisiones D-008 a D-013.
**Alternativas consideradas:** ninguna alternativa de estructura fue discutida en detalle; se acordó esta directamente.
**Impacto:** ref T-012 a T-017 (tareas de construcción del primer incremento).

<!--
### D-XXX — Título breve
**Fecha:** YYYY-MM-DD
**Decisión:** qué se decidió
**Razón:** por qué se decidió así
**Alternativas consideradas:** opciones descartadas
**Impacto:** ref T-XXX si aplica
-->
