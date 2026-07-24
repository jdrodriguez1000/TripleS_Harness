# Progress

> Estado general del proyecto: qué se ha hecho y qué sigue.
> Actualizar la fecha y el estado general cada vez que se registre un avance.

**Última actualización:** 2026-07-24
**Estado general:** Arquitectura acordada y en construcción activa. El repo quedó conectado a GitHub (`origin`) con protocolo de commit/push obligatorio en cada cierre de sesión. El primer incremento del paquete `sda` ya tiene su primer proveedor concreto funcional: base de empaquetado (T-012), CLI (T-013), ABCs del núcleo `Provider`/`Session` (T-014) y `ClaudeSDKProvider`/`ClaudeSDKSession` (T-015) verificados en vivo contra la suscripción real, incluyendo conversación multi-turno con contexto conservado (T-016). Se descubrió una limitación relevante: esa conversación solo vive en memoria mientras el proceso está vivo, sin persistencia entre ejecuciones (ver C-005, nueva tarea T-020 pendiente). Próximo paso abierto: T-017 (spike de descubrimiento de skills empaquetadas) y evaluar el diseño de T-020.

## Índice

- [Resumen actual](#resumen-actual)
- [Hecho](#hecho)
- [En progreso](#en-progreso)
- [Próximo](#próximo)
- [Bloqueos](#bloqueos)

## Resumen actual

Se creó la infraestructura de memoria persistente del proyecto (`900_persistence/`) y los protocolos/agentes de inicio y cierre de sesión que la mantienen actualizada. Se descubrió que `idea.md` (raíz del proyecto) ya contenía la definición de alcance y arquitectura, no leída por el `session-start-protocol` (ver L-002, pendiente de corregir en T-018). A partir de esa lectura y una conversación de alineación con el usuario, quedó acordado: el harness es una capa de orquestación con dos agent loops anidados; se implementará como programa Python propio usando el Agent SDK de Anthropic (CONFIRMADO explícitamente por el usuario, ver A-002); `900_persistence/` y `_persistence/` son conceptos distintos que no deben unificarse; el evaluador de calidad será un agente aparte; el alcance de v1 es el flujo end-to-end de `idea.md`.

En la continuación de esta misma sesión, el usuario mostró un repositorio experimental previo del mismo proyecto (`Harness_TripleS`, nombre casi invertido, mucho más avanzado: 16 commits, paquete `soda`, 190 tests, `soda start` funcionando). Se decidió NO migrar a ese repo y continuar en `TripleS_Harness` (ver D-007), tomando solo dos hallazgos técnicos verificados: (1) la autenticación por suscripción con el Agent SDK queda VERIFICADA en vivo, resolviendo A-001, con su mecanismo documentado (ver L-004, C-002, C-003); (2) un agente puede invocar otros agentes vía `AgentDefinition`, con observabilidad del loop interno mediante `parent_tool_use_id` (requisito central de `idea.md`). Ambos hallazgos se verificaron también contra documentación oficial del SDK vía ctx7 (ver L-005, L-006, C-004).

El usuario explicó que el desorden del repo anterior vino de mantener dos caminos vivos en paralelo (CLI y SDK; dos abstracciones de conversación) — ver L-003. De ahí se derivaron reglas de diseño acordadas: un solo camino de proveedor (el SDK, D-008), una sola cadena de abstracción `Provider`/`Session` (D-009), el SDK solo se importa dentro de `providers/` (D-010), `spikes/` fuera de `src/` con fecha de caducidad (D-011), y `tools/`/`agents/` sin conocerse mutuamente (D-012). Se acordó el nombre del paquete (`sda`, D-013), el punto de entrada (console script + `__main__.py`, D-014), la convención de código en inglés/español (D-015) y la estructura completa de carpetas (D-016). Queda un riesgo abierto sin verificar: si el SDK descubre las skills empaquetadas dentro de `sda` cuando el `cwd` es el proyecto destino (A-004), a resolver con un spike (T-017).

En la sesión del 2026-07-24 se configuró el respaldo del proyecto en GitHub: `.gitignore`, sección obligatoria de commit/push en `session-end-protocol` y en el agente `session-closer` (con Bash habilitado y prohibición explícita de operaciones destructivas), `git init` local, conexión de `origin` (`https://github.com/jdrodriguez1000/TripleS_Harness.git`) y primer commit/push exitoso (T-019). Sobre esa base se construyeron tres piezas del primer incremento del paquete `sda`: T-012 (pyproject.toml, ya verificado en sesión previa), T-013 (`cli.py`/`__main__.py` con `argparse`, verificado en vivo por el propio usuario en una carpeta externa vía el comando `sda` instalado globalmente, ver D-017) y T-014 (`core/session.py` y `core/provider.py`, ABCs asíncronas `Session`/`Provider` con `TurnResult` como retorno de turno, ver D-018), verificadas ambas por instanciación fallida esperada de las ABCs, una subclase de juguete y grep confirmando el aislamiento del SDK (D-010).

En una continuación de esa misma sesión (2026-07-24) se implementó T-015: `src/sda/providers/claude_sdk.py` con `ClaudeSDKProvider`/`ClaudeSDKSession`, primera implementación concreta sobre `claude_agent_sdk` aplicando la política de autenticación por suscripción ya verificada (A-001, L-004, C-002, C-003), con conexión perezosa que se abre en el primer `send()` y se mantiene entre turnos. Verificado en vivo (subclassing correcto, aislamiento del SDK respetado por `core/`, smoke test contra la suscripción real, y verificación manual adicional desde un proyecto externo instalando el paquete en modo editable). Después se implementó el spike T-016 (`spikes/t016_sesion_persistente.py`), confirmando en vivo que una misma `Session` conserva contexto entre turnos (recordó un dato mencionado en el turno anterior). De esa verificación surgió un hallazgo importante: esa conversación solo vive en memoria del proceso mientras está vivo, sin ningún mecanismo de persistencia en disco ni forma de reanudarla en una ejecución posterior — se registró como restricción nueva (C-005) y como tarea pendiente T-020 para investigar y diseñar a futuro.

## Hecho

- 2026-07-23 | Carpeta `900_persistence/` creada con los 6 archivos base y estructura de índice (progress, tasks, lessons, decisions, assumptions, constraints) | ref: T-001, T-002
- 2026-07-23 | Skill `session-start-protocol` y agente `session-starter` (haiku, rojo) creados | ref: T-003
- 2026-07-23 | Skill `session-end-protocol` y agente `session-closer` (sonnet, azul) creados | ref: T-004
- 2026-07-23 | Eliminada duplicación de contenido entre agentes (session-starter, session-closer) y sus skills correspondientes | ref: T-005
- 2026-07-23 | Creado `CLAUDE.md` en la raíz exigiendo invocar session-starter/session-closer al inicio/cierre de cada sesión | ref: T-006
- 2026-07-23 | Acordado con el usuario el alcance conceptual del harness (arquitectura de dos agent loops anidados, implementación Python + Agent SDK, separación 900_persistence vs _persistence, evaluador como agente aparte, alcance v1 = flujo de idea.md) | ref: T-007
- 2026-07-23 | Confirmación explícita del usuario: el harness es un programa Python propio | ref: T-008
- 2026-07-23 | Verificada en vivo la autenticación por suscripción (no API key) con el Agent SDK, y verificado que un agente puede invocar otros agentes con observabilidad del loop interno | ref: T-009
- 2026-07-23 | Decidido continuar la construcción en TripleS_Harness (no migrar al repo experimental Harness_TripleS) | ref: D-007
- 2026-07-23 | Acordadas reglas de diseño (un solo camino SDK, una sola cadena Provider/Session, aislamiento del SDK en providers/, spikes/ con caducidad, tools/agents desacoplados) y arquitectura completa: nombre del paquete (sda), punto de entrada, convención de código, estructura de carpetas | ref: D-008 a D-016
- 2026-07-23/24 | Creado pyproject.toml del paquete sda (dependencias, console script, layout src/), verificado con pip install -e . | ref: T-012
- 2026-07-24 | Configurado .gitignore, protocolo obligatorio de commit/push en session-end-protocol y session-closer, repo git inicializado y conectado a GitHub (origin), primer commit/push exitoso | ref: T-019
- 2026-07-24 | Creado src/sda/cli.py y __main__.py (argparse, --version, subcomando placeholder start), verificado en vivo por el usuario | ref: T-013, D-017
- 2026-07-24 | Creadas las ABCs del núcleo core/session.py (Session, TurnResult) y core/provider.py (Provider), API asíncrona, aislamiento del SDK confirmado por grep | ref: T-014, D-018
- 2026-07-24 | Creado src/sda/providers/claude_sdk.py (ClaudeSDKProvider, ClaudeSDKSession) sobre claude_agent_sdk con política de autenticación por suscripción, verificado en vivo (smoke test y verificación externa) | ref: T-015
- 2026-07-24 | Spike sesión persistente (spikes/t016_sesion_persistente.py) verificado en vivo: contexto conservado entre turnos dentro del mismo proceso | ref: T-016
- 2026-07-24 | Detectada y registrada la limitación de que la conversación no persiste entre ejecuciones del proceso (sin session_id ni historial en disco) | ref: C-005, T-020

## En progreso

- Ninguna tarea en construcción activa en este momento; queda por definir el próximo foco (T-017, T-020 u otra)

## Próximo

- Spike: verificación del descubrimiento de skills empaquetadas dentro de sda | ref: T-017
- Investigar y diseñar la persistencia/reanudación de conversaciones del harness entre ejecuciones | ref: T-020
- Definir si el soporte multi-vendor (Codex u otros) es restricción de v1 o meta futura (implícitamente resuelto como "futuro", falta confirmar) | ref: T-010
- Definir la rúbrica del evaluador de calidad y el origen del umbral 4.0 mencionado en `idea.md` | ref: T-011
- Ampliar el session-start-protocol para leer documentos de contexto en la raíz del proyecto | ref: T-018

## Bloqueos

- Ninguno actualmente. El bloqueo anterior (viabilidad de autenticación por suscripción) quedó resuelto: ver A-001 (verificado). Riesgo abierto sin verificar (no bloqueante aún): descubrimiento de skills empaquetadas dentro de sda cuando el cwd es el proyecto destino, ver A-004 y T-017.
