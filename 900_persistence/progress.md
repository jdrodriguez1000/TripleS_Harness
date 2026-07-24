# Progress

> Estado general del proyecto: qué se ha hecho y qué sigue.
> Actualizar la fecha y el estado general cada vez que se registre un avance.

**Última actualización:** 2026-07-23
**Estado general:** Alcance y arquitectura del proyecto TripleS_Harness quedaron completamente acordados y verificados. El supuesto de mayor riesgo (autenticación por suscripción con el Agent SDK) quedó VERIFICADO en vivo, y la arquitectura Python fue CONFIRMADA explícitamente por el usuario. Se decidió continuar la construcción en este repo (no en el repo experimental previo `Harness_TripleS`, mucho más avanzado pero con un diseño desordenado). Quedaron acordadas reglas de diseño (un solo camino de proveedor, una sola cadena de abstracción, aislamiento del SDK en `providers/`) y la estructura completa de carpetas del paquete `sda`. Próximo paso: iniciar la construcción real del primer incremento (pyproject.toml, cli.py, core/, providers/claude_sdk.py y dos spikes de verificación).

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

## En progreso

- Ninguna tarea de diseño/alineación en progreso; el alcance y la arquitectura quedaron acordados. Empieza la fase de construcción real del primer incremento | ref: T-012 a T-017

## Próximo

- Crear `pyproject.toml` del paquete `sda` con dependencias y console script | ref: T-012
- Crear `src/sda/cli.py` con `main()` y `__main__.py` | ref: T-013
- Crear `core/provider.py` (Provider ABC) y `core/session.py` (Session ABC) | ref: T-014
- Crear `providers/claude_sdk.py` (ClaudeSDKProvider) con la política de autenticación por suscripción | ref: T-015
- Spike: sesión persistente sobre suscripción con contexto entre turnos | ref: T-016
- Spike: verificación del descubrimiento de skills empaquetadas dentro de sda | ref: T-017
- Definir si el soporte multi-vendor (Codex u otros) es restricción de v1 o meta futura (implícitamente resuelto como "futuro", falta confirmar) | ref: T-010
- Definir la rúbrica del evaluador de calidad y el origen del umbral 4.0 mencionado en `idea.md` | ref: T-011
- Ampliar el session-start-protocol para leer documentos de contexto en la raíz del proyecto | ref: T-018

## Bloqueos

- Ninguno actualmente. El bloqueo anterior (viabilidad de autenticación por suscripción) quedó resuelto: ver A-001 (verificado). Riesgo abierto sin verificar (no bloqueante aún): descubrimiento de skills empaquetadas dentro de sda cuando el cwd es el proyecto destino, ver A-004 y T-017.
