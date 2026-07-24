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
| T-013 | Crear src/sda/cli.py con main() y sda --help funcional, más __main__.py | No implementada |
| T-014 | Crear src/sda/core/provider.py (Provider ABC) y src/sda/core/session.py (Session ABC) | No implementada |
| T-015 | Crear src/sda/providers/claude_sdk.py (ClaudeSDKProvider) con la política de autenticación por suscripción | No implementada |
| T-016 | Spike: abrir sesión persistente sobre suscripción, confirmar respuesta y conservación de contexto entre turnos | No implementada |
| T-017 | Spike: verificar descubrimiento de skills empaquetadas dentro de sda cuando el cwd es el proyecto destino | No implementada |
| T-018 | Ampliar session-start-protocol para que lea documentos de contexto en la raíz del proyecto (p. ej. idea.md) | No implementada |

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
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

`src/sda/cli.py` con `main()` y un `sda --help` que funcione, más `__main__.py` para permitir `python -m sda` en desarrollo. Ver D-014.

### T-014 — Crear core/provider.py y core/session.py
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

`src/sda/core/provider.py` (`Provider` ABC, fábrica de sesiones) y `src/sda/core/session.py` (`Session` ABC, conversación multi-turno). Ver D-009, D-016.

### T-015 — Crear providers/claude_sdk.py
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

`src/sda/providers/claude_sdk.py` — `ClaudeSDKProvider` con la política de autenticación por suscripción verificada (ver A-001, L-004, C-002, C-003). Ver D-008, D-010.

### T-016 — Spike: sesión persistente sobre suscripción con contexto entre turnos
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Spike en `spikes/` que abra una sesión persistente sobre suscripción, confirme que responde y que conserva contexto entre turnos. Ver D-011.

### T-017 — Spike: verificación del descubrimiento de skills empaquetadas
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Spike de verificación de si el SDK descubre las skills empaquetadas dentro de `src/sda/skills/` cuando el harness corre con el `cwd` del proyecto destino (no el del propio paquete `sda`). Ver A-004 (riesgo abierto), D-011.

### T-018 — Ampliar session-start-protocol para leer documentos de contexto en la raíz del proyecto
**Estado:** No implementada
**Fecha creación:** 2026-07-23
**Fecha actualización:** 2026-07-23

Tarea pendiente derivada de L-002: el `session-start-protocol` solo lee `900_persistence/` y no documentos de contexto en la raíz del proyecto (p. ej. `idea.md`). Sigue vigente y sin corregir; se propone ampliarlo para evitar diagnósticos incorrectos al reanudar sesiones futuras.
