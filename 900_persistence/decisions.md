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
- [D-017 — CLI con argparse (stdlib) y subcomando placeholder desde el esqueleto](#d-017--cli-con-argparse-stdlib-y-subcomando-placeholder-desde-el-esqueleto)
- [D-018 — API asíncrona para Session/Provider y TurnResult como retorno del turno](#d-018--api-asíncrona-para-sessionprovider-y-turnresult-como-retorno-del-turno)
- [D-019 — Las skills propias de sda se entregan mediante un plugin local único (corrige D-016)](#d-019--las-skills-propias-de-sda-se-entregan-mediante-un-plugin-local-único-corrige-d-016)
- [D-020 — Pivote de infraestructura a la primera rebanada vertical del doble bucle, evaluación 4.0 diferida como stub](#d-020--pivote-de-infraestructura-a-la-primera-rebanada-vertical-del-doble-bucle-evaluación-40-diferida-como-stub)
- [D-021 — Comunicación bucle externo↔interno vía Forma A: dos Session Python separadas conducidas por el orquestador](#d-021--comunicación-bucle-externointerno-vía-forma-a-dos-session-python-separadas-conducidas-por-el-orquestador)
- [D-022 — Señal explícita del humano ("listo"/"continuar") para pasar de bootstrap a onboarding](#d-022--señal-explícita-del-humano-listocontinuar-para-pasar-de-bootstrap-a-onboarding)
- [D-023 — Áreas de descubrimiento §1–§10 adoptadas de una plantilla existente del usuario, regla "se cita, no se interpreta"](#d-023--áreas-de-descubrimiento-1–10-adoptadas-de-una-plantilla-existente-del-usuario-regla-se-cita-no-se-interpreta)
- [D-024 — UX de mensajería en terminal: prefijos por hablante y espaciado entre bloques](#d-024--ux-de-mensajería-en-terminal-prefijos-por-hablante-y-espaciado-entre-bloques)
- [D-025 — Fijar Sonnet + effort high para el onboarding-reader; diferir la sesión principal/líder (Opus + high) a T-027](#d-025--fijar-sonnet--effort-high-para-el-onboarding-reader-diferir-la-sesión-principalíder-opus--high-a-t-027)
- [D-026 — El orchestrator-leader es un agente LLM bajo el principio "el LLM decide / las herramientas hacen cumplir"](#d-026--el-orchestrator-leader-es-un-agente-llm-bajo-el-principio-el-llm-decide--las-herramientas-hacen-cumplir)
- [D-027 — El bucle interno se invoca vía herramienta en-proceso, no vía subagente nativo del SDK](#d-027--el-bucle-interno-se-invoca-vía-herramienta-en-proceso-no-vía-subagente-nativo-del-sdk)
- [D-028 — La puerta de aprobación humana es un límite forzado por herramienta](#d-028--la-puerta-de-aprobación-humana-es-un-límite-forzado-por-herramienta)
- [D-029 — La señal humana de "continuar" pasa a intención en lenguaje natural, validada por herramienta determinista](#d-029--la-señal-humana-de-continuar-pasa-a-intención-en-lenguaje-natural-validada-por-herramienta-determinista)
- [D-030 — D-026 a D-029 quedan firmes como decisiones implementadas y verificadas](#d-030--d-026-a-d-029-quedan-firmes-como-decisiones-implementadas-y-verificadas)
- [D-031 — El sandbox real por-agente se implementa con `builtin_tools` (`tools=` del SDK), no con `allowed_tools`](#d-031--el-sandbox-real-por-agente-se-implementa-con-builtin_tools-tools-del-sdk-no-con-allowed_tools)
- [D-032 — El líder es el único interlocutor visible en terminal, con streaming real de texto](#d-032--el-líder-es-el-único-interlocutor-visible-en-terminal-con-streaming-real-de-texto)
- [D-033 — El merge de `t-027-sesion-lider` a master queda bloqueado hasta resolver T-030](#d-033--el-merge-de-t-027-sesion-lider-a-master-queda-bloqueado-hasta-resolver-t-030)
- [D-034 — El área de entrada del harness es un prompt en línea, fijo y mudo (sin recuadro ni indicadores de estado)](#d-034--el-área-de-entrada-del-harness-es-un-prompt-en-línea-fijo-y-mudo-sin-recuadro-ni-indicadores-de-estado)

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
**CORRECCIÓN (2026-07-24, ver D-019):** el nodo `skills/<nombre>/SKILL.md` suelto dentro de `src/sda/` de este diagrama queda INVALIDADO por el spike T-017: no es descubrible cuando el harness corre con el `cwd` del proyecto destino. Las skills de `sda` deben vivir dentro de un plugin local único (`src/sda/plugin/`), no como carpeta `skills/` suelta al mismo nivel que `core/`/`providers/`. Ver D-019.

### D-017 — CLI con argparse (stdlib) y subcomando placeholder desde el esqueleto
**Fecha:** 2026-07-24
**Decisión:** el CLI (`src/sda/cli.py`) se construye con `argparse` de la librería estándar, no con `click` ni otra librería de terceros. El esqueleto ya declara subcomandos (empezando por `start`) como placeholders que imprimen "no implementado aún" en vez de exponer solo `--help`/`--version` sin comandos. La versión se lee con `importlib.metadata.version("sda")` para no duplicar el número que ya vive en `pyproject.toml`.
**Razón:** evitar una dependencia nueva coherente con el enfoque minimalista del proyecto; dejar listos los ganchos del flujo de `idea.md`/D-014 (`sda start`) para que T-014/T-015 solo conecten lógica sin rediseñar el CLI.
**Alternativas consideradas:** usar `click` (descartada por añadir dependencia directa); CLI mínimo solo con `--help`/`--version` sin subcomandos (descartada por no reflejar el flujo previsto).
**Impacto:** ref T-013. Los subcomandos se irán activando con lógica real en T-014 en adelante.

### D-018 — API asíncrona para Session/Provider y TurnResult como retorno del turno
**Fecha:** 2026-07-24
**Decisión:** las ABCs del núcleo son asíncronas: `Session.send()` y `Session.close()` son `async`, y `Session` implementa el protocolo `async with` (`__aenter__`/`__aexit__` concretos en la ABC, con `__aexit__` llamando a `close()`). `Provider.create_session()` es sync (solo construye el objeto; la conexión real es async dentro de la sesión). Un turno (`send`) devuelve un `TurnResult` (dataclass en `core/session.py`) con al menos el campo `text`, extensible con metadata sin romper el contrato.
**Razón:** el SDK subyacente (`claude_agent_sdk.ClaudeSDKClient`) es totalmente async (verificado en vivo: `connect`/`disconnect`/`query`/`receive_response` son `async`), y una sesión persistente con contexto entre turnos (spike T-016) requiere un cliente async de larga vida; esconder `anyio.run()` dentro de cada `send()` sync lo impediría. Un `TurnResult` (en vez de `str`) evita cambiar la firma del contrato cuando el evaluador del bucle interno necesite metadata (uso de tokens, mensajes crudos).
**Alternativas consideradas:** API sync con `anyio.run()` escondido en cada `send()` (descartada: choca con la sesión persistente de T-016); que `send()` devuelva `str` simple (descartada: obligaría a romper el contrato al añadir observabilidad).
**Impacto:** ref T-014. El puente sync→async (desde `cli.py::main`, que es sync) vivirá en `app.py` con `anyio.run(...)`, no en `core/`. T-015 implementará `send` sobre `client.query()` + `receive_response()` y `close` sobre `disconnect()`.

### D-019 — Las skills propias de sda se entregan mediante un plugin local único (corrige D-016)
**Fecha:** 2026-07-24
**Decisión:** las skills propias de `sda` se entregan mediante un plugin local ÚNICO, cargado por ruta explícita (`plugins=[{"type":"local","path":...}]`), no vía descubrimiento por `cwd`. Es un solo plugin contenedor para todas las skills del harness (no uno por skill); agregar una skill nueva = agregar una carpeta `skills/<nombre>/SKILL.md` dentro de ese plugin (`src/sda/plugin/.claude-plugin/plugin.json` + `src/sda/plugin/skills/<nombre>/SKILL.md`). La ruta del plugin se resolverá dentro del paquete instalado con `importlib` cuando se promueva a producción (tarea futura T-021, fuera del alcance del spike, ver D-011). Costo conocido: los nombres de las skills quedan calificados como `plugin:skill` en vez de solo `skill`.
**Razón:** el spike T-017 demostró en vivo que el layout "pelado" `src/sda/skills/<nombre>/SKILL.md` (D-016 original) no se descubre desde un `cwd` externo, porque `skills` en `ClaudeAgentOptions` auto-configura `setting_sources=["user","project"]`, que solo miran `~/.claude/skills/` y `<cwd>/.claude/skills/`, no un directorio interno de un paquete instalado. El mecanismo nativo que sí funciona independientemente del `cwd` es el plugin local.
**Alternativas consideradas:** copiar/enlazar las skills al `.claude/skills/` del proyecto destino en tiempo de arranque (descartada: requeriría escritura en el proyecto destino y sincronización manual); registrar `setting_sources` adicionales apuntando al paquete instalado (descartada: no es una opción soportada por el SDK para rutas arbitrarias fuera de user/project); un plugin por skill en vez de un plugin único contenedor (descartada: más complejidad de manifiestos sin beneficio claro para el alcance actual).
**Impacto:** ref T-017 (spike que lo confirmó), D-016 (corregido), A-004 (resuelto), T-021 (tarea de promoción a producción pendiente).

### D-020 — Pivote de infraestructura a la primera rebanada vertical del doble bucle, evaluación 4.0 diferida como stub
**Fecha:** 2026-07-24
**Decisión:** se pausan las tareas de infraestructura de desarrollo pendientes (T-018, T-020, T-021, T-023) y se construye, con aprobación explícita del usuario vía plan mode, la primera rebanada vertical del producto core descrito en `idea.md`: bootstrapping + bucle interno del onboarding-reader + puerta de aprobación humana (ver T-024). La evaluación de calidad interna (umbral 4.0) queda diferida como stub que siempre aprueba (`evaluator.py::evaluate_draft()`), dejando el seam listo para conectar la rúbrica real más adelante (T-011).
**Razón:** se diagnosticó que ninguno de los pilares centrales de `idea.md` (doble bucle REPL, máquina de estados en disco, onboarding con puerta de aprobación humana, evaluación de calidad) existía todavía en el código; las tareas pendientes previas eran plomería alrededor de un producto que aún no tenía su primera rebanada vertical funcionando.
**Alternativas consideradas:** seguir completando la infraestructura pendiente (T-018/T-020/T-021/T-023) antes de tocar el producto core; descartada porque no verificaba el diseño central del harness.
**Impacto:** ref T-024. T-018, T-020, T-021, T-023 quedan pendientes pero de menor prioridad frente al producto core.

### D-021 — Comunicación bucle externo↔interno vía Forma A: dos Session Python separadas conducidas por el orquestador
**Fecha:** 2026-07-24
**Decisión:** el orquestador (`Orchestrator`) conduce en código Python dos `Session` separadas (una para sí mismo, otra para el subagente onboarding-reader), en vez de delegar el subagente a un mecanismo nativo del SDK tipo `AgentDefinition`/Task.
**Razón:** `idea.md` exige poder observar y evaluar el bucle interno turno a turno; conducir explícitamente ambas sesiones desde el propio código del harness permite interceptar cada turno del subagente (para la futura evaluación de calidad) de una forma que un subagente nativo delegado no expondría con el mismo nivel de control.
**Alternativas consideradas:** usar subagentes nativos del SDK (`AgentDefinition`, observabilidad vía `parent_tool_use_id`, ya verificado como posible en T-009); descartada para este componente porque oculta el detalle turno a turno que el harness necesita evaluar.
**Impacto:** ref T-024 (`orchestrator.py::_conducir_onboarding`).

### D-022 — Señal explícita del humano ("listo"/"continuar") para pasar de bootstrap a onboarding
**Fecha:** 2026-07-24
**Decisión:** el paso de la fase de bootstrap (edición manual de `_context/scope.md`) a la fase de onboarding lo dispara una señal explícita que escribe el humano en la terminal (`listo`/`continuar`), no una heurística del sistema que intente adivinar cuándo terminó de editar el archivo.
**Razón:** una heurística de "archivo cambiado" o "archivo no vacío" es frágil y puede disparar el onboarding a mitad de una edición; una señal explícita del humano es simple, predecible y coherente con la puerta de aprobación humana que ya exige `idea.md` en otros puntos del flujo.
**Alternativas consideradas:** detectar automáticamente cambios en `scope.md` (con watcher de archivo o comparación de hash); descartada por complejidad y por introducir falsos disparos.
**Impacto:** ref T-024 (`orchestrator.py::run`).

### D-023 — Áreas de descubrimiento §1–§10 adoptadas de una plantilla existente del usuario, regla "se cita, no se interpreta"
**Fecha:** 2026-07-24
**Decisión:** la plantilla `templates/document-extract-temp.md` adopta las 10 áreas de descubrimiento de una plantilla que el usuario ya usaba en otro proyecto (Objetivo, Hipótesis de valor, Tipo de prototipo [n/a, lo deduce el sistema], Stakeholders, Actores, Camino feliz, Gatekeeper, Timebox, Exclusiones, Split por audiencia). El onboarding-reader debe citar textualmente (con ubicación) el contenido de `scope.md` que cubre cada área, marcar cobertura como cubierta/parcial/ausente/n-a, y listar aparte las ambigüedades sin resolverlas — regla de oro "se cita, no se interpreta".
**Razón:** `document-extract.md` es insumo del futuro agente entrevistador, cuya función es no repreguntar lo que el scope ya cubre; resolver ambigüedades en esta etapa (en vez de listarlas) le quitaría al entrevistador la información que necesita para decidir qué preguntar. Además el proyecto está en fase de prototipado (meta: prototipo rápido y barato), lo que refuerza reutilizar una plantilla ya probada en vez de diseñar una nueva desde cero.
**Alternativas consideradas:** que el onboarding-reader interprete/resuelva las ambigüedades del scope; descartada porque usurparía el rol del futuro entrevistador. Diseñar una plantilla nueva de áreas desde cero; descartada por no aportar valor frente a una ya validada por el usuario.
**Impacto:** ref T-024 (`templates/document-extract-temp.md`, `prompts/onboarding_reader.md`).

### D-024 — UX de mensajería en terminal: prefijos por hablante y espaciado entre bloques
**Fecha:** 2026-07-24
**Decisión:** durante la prueba manual de T-025 el usuario pidió, por legibilidad (no por bug), ajustar cómo se ve la interacción en terminal: (1) el prompt del humano cambia de `tú> ` a `[User] > ` en `orchestrator.py` y `repl.py`; (2) la invocación del onboarding-reader se separa en mensajes distintos con prefijos por hablante: `[sda] Invocando al agente onboarding-reader…`, luego `[onboarding-reader] Trabajando en la construcción de _prototype/document-extract.md. Te aviso cuando termine…`, y al terminar `[onboarding-reader] Trabajo terminado.` (todo en el único punto compartido `_conducir_onboarding`, por lo que aplica igual al primer borrador y al flujo de rechazo/corrección); (3) se agregó espaciado (líneas en blanco) entre bloques de mensajes en `_pedir_scope`, `_presentar_borrador`, el mensaje de aprobación y los avisos de fase en `run()`.
**Razón:** la primera corrida en vivo (`sda_test_004`) mostró una salida de terminal donde el resumen del onboarding-reader y el prompt del humano quedaban visualmente pegados, dificultando distinguir quién "habla" en cada bloque; aunque se confirmó que no era un bug de truncamiento (fue el usuario tecleando pegado al texto), el usuario decidió mejorar la legibilidad de la interacción humano-harness de cara a los agentes futuros que se sumarán al doble bucle.
**Alternativas consideradas:** dejar el prompt/mensajería como estaba (`tú>`, un solo bloque de texto sin separación); descartada por preferencia explícita de UX del usuario.
**Impacto:** ref T-025 (`src/sda/orchestrator.py`, `src/sda/repl.py`). Del mismo espíritu que D-022 (señales explícitas del humano): ambas buscan que la interacción humano-harness sea clara y sin ambigüedad sobre quién dice qué y cuándo.

### D-025 — Fijar Sonnet + effort high para el onboarding-reader; diferir la sesión principal/líder (Opus + high) a T-027
**Fecha:** 2026-07-24
**Decisión:** el usuario decidió explícitamente que el onboarding-reader use **Sonnet + effort `high`** (en vez del default implícito del CLI/SDK), y que fijar Opus + effort `high` para una futura sesión principal/líder que orqueste todo el doble bucle quede fuera de esta tarea, trasladado a la nueva tarea de análisis T-027.
**Razón:** hoy el bucle externo (`orchestrator.py::run`) es código Python puro que no abre ninguna sesión contra el LLM; la única sesión real es la interna del onboarding-reader, por lo que no hay todavía un lugar en el código donde cablear un modelo/effort para un "líder". Introducir esa sesión líder es un cambio de diseño mayor que merece su propio análisis antes de implementarse.
**Alternativas consideradas:** implementar de una vez el líder Opus+high dentro del alcance de T-026; descartada por ampliar el alcance más allá de lo pedido y por requerir diseño previo (impacto en `orchestrator.py`, `repl.py`, costo/latencia de Opus persistente).
**Impacto:** ref T-026 (implementada, mecanismo por-agente `model`/`effort` en `Provider.create_session`/`ClaudeSDKProvider` reutilizable), T-027 (análisis pendiente).

### D-026 — El orchestrator-leader es un agente LLM bajo el principio "el LLM decide / las herramientas hacen cumplir"
**Fecha:** 2026-07-24
**Decisión:** el `orchestrator-leader` es un agente LLM (Opus + effort high) que lidera el bucle externo del harness, tomando la conversación con el humano y decidiendo qué hacer en cada momento. Los efectos peligrosos del flujo (cambios de estado en disco, adquisición de locks, cruce de la puerta de aprobación) no viven en el LLM: son efectos laterales deterministas de herramientas en-proceso que el líder solo puede invocar, nunca ejecutar directamente.
**Razón:** reemplazar el bucle externo Python puro (`Orchestrator.run()`) por un agente conversacional real (pedido explícito del usuario, ver T-027) sin sacrificar el determinismo ni la seguridad que hoy garantiza el código: si el LLM "decide", las herramientas siguen siendo las únicas que "hacen cumplir" las reglas del harness.
**Alternativas consideradas:** dejar el bucle externo como código Python puro indefinidamente (descartada por el pedido explícito del usuario de tener un líder conversacional); dar al líder acceso directo a editar el estado/archivos sin pasar por herramientas dedicadas (descartada por perder el control determinista que D-021/D-022 ya establecieron para el bucle interno).
**Impacto:** ref T-027 (análisis), T-028 (implementación pendiente), `docs/design/T-027-orchestrator-leader.md`.

### D-027 — El bucle interno se invoca vía herramienta en-proceso, no vía subagente nativo del SDK
**Fecha:** 2026-07-24
**Decisión:** el líder invoca el bucle interno del onboarding-reader mediante una herramienta en-proceso (`run_inner_loop`, `@tool` + `create_sdk_mcp_server`), no mediante un subagente nativo del SDK (`AgentDefinition`/Task).
**Razón:** reconciliar "el bucle externo es un agente que lidera" (D-026) con la observabilidad turno a turno del bucle interno que ya exige D-021: una herramienta en-proceso es código Python propio del harness que puede conducir la segunda `Session` explícitamente e interceptar cada turno, tal como ya lo hacía `Orchestrator._conducir_onboarding`; un subagente nativo delegado ocultaría ese detalle. Verificado por el spike `spikes/t027_herramienta_en_proceso.py`: es seguro abrir/conducir un `ClaudeSDKClient` anidado desde dentro del callback de la herramienta del líder.
**Alternativas consideradas:** subagente nativo vía `AgentDefinition` con observabilidad por `parent_tool_use_id` (descartada, mismo motivo que D-021: oculta el detalle turno a turno necesario para evaluar el bucle interno).
**Impacto:** ref T-027, T-028 (`src/sda/tools/run_inner_loop`), D-021 (se mantiene vigente, ahora invocado desde una herramienta en vez de desde código de bucle externo puro).

### D-028 — La puerta de aprobación humana es un límite forzado por herramienta
**Fecha:** 2026-07-24
**Decisión:** la promoción de un documento a `APPROVED` solo puede ocurrir mediante la herramienta `promote_to_approved`, y esa herramienta solo la ejecuta si `current_phase == HUMAN_REVIEW` y ya hubo un turno humano de por medio. El líder LLM no tiene ningún otro camino para marcar algo como aprobado.
**Razón:** aun con un líder conversacional, la puerta de aprobación humana (requisito central de `idea.md`) no puede depender de que el LLM "decida bien"; debe seguir siendo un límite determinista que el código impone, igual que en el diseño Python puro actual (`Orchestrator._aprobar`).
**Alternativas consideradas:** confiar en que el prompt del líder le indique no auto-aprobar sin instrucción humana (descartada: un prompt es una guía, no una garantía; el requisito de seguridad exige un límite en código).
**Impacto:** ref T-027, T-028 (`src/sda/tools/promote_to_approved`).

### D-029 — La señal humana de "continuar" pasa a intención en lenguaje natural, validada por herramienta determinista
**Fecha:** 2026-07-24
**Decisión:** con un líder conversacional, la señal humana para avanzar de bootstrap a onboarding deja de requerir la palabra exacta `listo`/`continuar` (D-022) y pasa a poder expresarse como intención en lenguaje natural dentro de la conversación con el líder; pero el avance real de fase sigue condicionado a que la herramienta determinista `scope_esta_lleno()` confirme que `scope.md` ya no es el stub vacío.
**Razón:** un líder conversacional puede/debe interpretar lenguaje natural (es su valor agregado frente al comando exacto), pero la decisión de si el scope está realmente listo no puede depender de que el LLM "lo crea"; se conserva el espíritu de D-022 (una condición objetiva, no una heurística de archivo cambiado) mediante una herramienta explícita.
**Alternativas consideradas:** mantener la palabra exacta también con el líder conversacional (descartada: contradice el valor de tener un líder que entienda lenguaje natural); dejar que el líder decida sin herramienta si el scope está listo (descartada: mismo riesgo que D-028, el LLM no debe ser el único juez de una condición que afecta el estado del harness).
**Impacto:** ref T-027, T-028 (`src/sda/tools/scope_esta_lleno`), D-022 (matizada, no invalidada).

### D-030 — D-026 a D-029 quedan firmes como decisiones implementadas y verificadas
**Fecha:** 2026-07-24
**Decisión:** las decisiones propuestas D-026 a D-029 (documento de diseño de T-027) se registran como decisiones firmes del proyecto, no ya propuestas, porque T-028 las implementó y verificó en vivo end-to-end.
**Razón:** el análisis (T-027) quedó respaldado por implementación real y prueba en vivo (T-028); no hay razón para mantenerlas como "propuestas" una vez construidas y confirmadas funcionando.
**Alternativas consideradas:** ninguna; es solo la formalización de decisiones ya tomadas en T-027 tras su verificación en T-028.
**Impacto:** ref T-027, T-028.

### D-031 — El sandbox real por-agente se implementa con `builtin_tools` (`tools=` del SDK), no con `allowed_tools`
**Fecha:** 2026-07-24
**Decisión:** el sandbox por-agente (qué herramientas nativas puede usar cada sesión) se implementa con el nuevo parámetro `builtin_tools` de `Provider.create_session` (mapeado a `tools=` de `ClaudeAgentOptions`), no con `allowed_tools`. El líder (`orchestrator-leader`) queda con `builtin_tools=["Read","Glob","Grep"]` (solo lectura); el onboarding-reader con `builtin_tools=["Read","Glob","Grep","Write"]` (lectura + escritura de su entregable). Las herramientas MCP en-proceso del líder (`scope_esta_lleno`, `run_inner_loop`, `promote_to_approved`) siguen disponibles porque no son "builtin".
**Razón:** se descubrió (ver L-013) que `allowed_tools` bajo `permission_mode="bypassPermissions"` no restringe el toolset, solo auto-aprueba; por lo tanto el modelo de "manos atadas" que T-024/T-027/D-026 asumían para el sandbox del líder y del onboarding-reader era nominal, no real. `tools=`/`disallowed_tools=` es el mecanismo verificado que sí restringe de verdad qué herramientas nativas existen para una sesión.
**Alternativas consideradas:** mantener `allowed_tools` como mecanismo de sandbox (descartada: no cumple la función de seguridad que se le atribuía); usar `disallowed_tools` (denylist) en vez de `builtin_tools`/`tools=` (allowlist) (descartada: una allowlist explícita por agente es más segura por defecto que una denylist que exige enumerar todo lo que se quiere prohibir).
**Impacto:** ref T-028, D-026 (nota: la afirmación de sandbox de T-024/onboarding-reader también era nominal hasta este hardening), L-013.

### D-032 — El líder es el único interlocutor visible en terminal, con streaming real de texto
**Fecha:** 2026-07-25
**Decisión:** se retiran las etiquetas `[sda]`/`[líder]`/`[User]` y el banner de arranque fijo de la terminal; el `orchestrator-leader` queda como el único interlocutor visible, sin prefijos, y el prompt del humano se simplifica de `[User] > ` a `> `. Se retira también la exposición en pantalla de modelo/effort del onboarding-reader. Las líneas de estado de subagentes (p. ej. "Trabajando en...", "Trabajo terminado.") se mantienen pero indentadas con el helper `subagent_line()` (símbolo `⎿`, color ANSI dim) para distinguirlas visualmente del líder sin usar etiquetas de texto. Se agrega además streaming real: `Session.send()` (contrato `core/session.py`) acepta un callback opcional `on_text` (tipo `OnText`), implementado en `ClaudeSDKSession.send()` y usado en `orchestrator.py` para imprimir cada bloque de texto del líder a medida que se genera, en vez de esperar el turno completo.
**Razón:** D-024 (prefijos por hablante) resolvió la ambigüedad de quién habla, pero a costo de una experiencia robótica con etiquetas técnicas visibles; con un solo líder conversacional como interlocutor principal, el usuario prefiere una experiencia de chat natural, y el streaming permite ver la intención del líder ("voy a trabajar en...") antes de que lance el subagente, en vez de esperar en silencio a que termine todo el turno.
**Alternativas consideradas:** mantener las etiquetas `[sda]/[líder]/[User]` de D-024 indefinidamente (descartada por preferencia explícita de UX del usuario, ahora que hay un líder conversacional real y no un bucle Python plano); no implementar streaming y mantener impresión al final del turno completo (descartada porque no comunica la intención del líder mientras trabaja).
**Impacto:** ref archivos modificados: `src/sda/core/session.py`, `src/sda/providers/claude_sdk.py`, `src/sda/orchestrator.py`, `src/sda/repl.py`, `src/sda/tools/leader_tools.py`. Introduce el riesgo documentado en T-030 (ventana de entrelazado visual ampliada por el streaming).

### D-033 — El merge de `t-027-sesion-lider` a master queda bloqueado hasta resolver T-030
**Fecha:** 2026-07-25
**Decisión:** además del bloqueo ya existente desde T-028 (merge pospuesto por decisión del usuario), se agrega una condición explícita: el merge de la rama `t-027-sesion-lider` a `master` no debe hacerse hasta que T-030 (entrelazado visual entre streaming y teclado del usuario) quede resuelto.
**Razón:** el streaming introducido en D-032 amplió la ventana de riesgo de que el tecleo del humano se entrelace visualmente con la salida del programa en terminal (ver diagnóstico en T-030); el usuario considera que ese problema de UX debe cerrarse antes de llevar esta rama a producción (master).
**Alternativas consideradas:** hacer merge igual y arreglar T-030 después en master directamente (descartada explícitamente por el usuario).
**Impacto:** ref T-028, T-030. Bloquea el ítem "evaluar y, si convence, hacer merge de `t-027-sesion-lider` a master" en `progress.md` con una condición adicional.

### D-034 — El área de entrada del harness es un prompt en línea, fijo y mudo (sin recuadro ni indicadores de estado)
**Fecha:** 2026-07-25
**Decisión:** el área de entrada del humano en `sda start` (y en `run_repl`) es un prompt de `prompt_toolkit` en línea, con texto fijo (`"\n> "`) que nunca cambia ni se repinta con indicadores de estado ("trabajando…") ni recuadro (`show_frame`).
**Razón:** durante la implementación de T-030 se probaron dos alternativas y ambas se descartaron: un prompt dinámico que mostraba "(trabajando…)" mientras el agente procesaba quedaba escrito en el scrollback de la terminal cada vez que se repintaba, ensuciando la transcripción de la conversación; y un recuadro (`show_frame=True`) imitando la UX de Claude Code, aunque funcionó técnicamente, fue rechazado por el usuario tras probarlo en vivo por preferencia visual ("no se ve muy bien"). Un prompt fijo y mudo evita ambos problemas sin sacrificar la robustez ya lograda (el tecleo del humano nunca se pierde ni se entrelaza visualmente, ver T-030).
**Alternativas consideradas:** prompt dinámico con indicador de estado (descartada, ensucia el scrollback); recuadro del área de entrada con `show_frame=True` (descartada, preferencia visual del usuario tras verificarlo en vivo); `Application` de pantalla completa de `prompt_toolkit` con `HSplit`/`Frame` (descartada en el análisis previo por perder el scrollback nativo de la terminal y obligar a enrutar toda la salida a un buffer propio).
**Impacto:** ref T-030 (`src/sda/repl.py::TerminalUI`). Si en el futuro hace falta una señal de "trabajando", la vía limpia sin ensuciar el scrollback es el `bottom_toolbar` de `prompt_toolkit`, que se borra automáticamente cuando el prompt retorna (no evaluado en código, solo identificado como la opción correcta a futuro).

<!--
### D-XXX — Título breve
**Fecha:** YYYY-MM-DD
**Decisión:** qué se decidió
**Razón:** por qué se decidió así
**Alternativas consideradas:** opciones descartadas
**Impacto:** ref T-XXX si aplica
-->
