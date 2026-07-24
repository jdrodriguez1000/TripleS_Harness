# Assumptions

> Supuestos asumidos durante la planeación y ejecución del proyecto.

## Índice

- [A-001 — Autenticación por suscripción (no API key) es viable con el Agent SDK](#a-001--autenticación-por-suscripción-no-api-key-es-viable-con-el-agent-sdk)
- [A-002 — El harness es un programa Python propio (inferencia pendiente de confirmación explícita)](#a-002--el-harness-es-un-programa-python-propio-inferencia-pendiente-de-confirmación-explícita)
- [A-003 — El soporte multi-vendor (Codex u otros) queda abierto para el futuro](#a-003--el-soporte-multi-vendor-codex-u-otros-queda-abierto-para-el-futuro)
- [A-004 — Riesgo: el descubrimiento de skills empaquetadas dentro de sda no está confirmado cuando el cwd es el proyecto destino](#a-004--riesgo-el-descubrimiento-de-skills-empaquetadas-dentro-de-sda-no-está-confirmado-cuando-el-cwd-es-el-proyecto-destino)

## Detalle

### A-001 — Autenticación por suscripción (no API key) es viable con el Agent SDK
**Fecha:** 2026-07-23
**Supuesto:** el objetivo del proyecto es usar el Agent SDK de Anthropic autenticando con suscripción (no con API key), lo cual se está asumiendo como técnicamente posible.
**Riesgo si es falso:** si el SDK no soporta autenticación por suscripción, se cae la base de la arquitectura planteada para el harness. Era el supuesto de mayor riesgo del proyecto identificado hasta ahora.
**Estado:** RESUELTO/VERIFICADO (2026-07-23) — deja de ser supuesto. Se verificó en vivo, varias veces, sobre la suscripción real del usuario en el repo experimental `Harness_TripleS`, usando el paquete `claude-agent-sdk` (Python). Mecanismo: el SDK levanta el CLI `claude` como subproceso (requiere `claude` instalado y con `claude /login` hecho); sin `ANTHROPIC_API_KEY` ni `CLAUDE_CODE_OAUTH_TOKEN` en el entorno, cae a las credenciales OAuth de `~/.claude/.credentials.json` (la suscripción). Ver L-004 (trampa del entorno heredado) y C-002/C-003 (requisitos del modo no interactivo). Ref T-009, D-008.

### A-002 — El harness es un programa Python propio (inferencia pendiente de confirmación explícita)
**Fecha:** 2026-07-23
**Supuesto:** de las respuestas del usuario sobre Python y agent loops, el agente infirió que el harness será un programa Python propio que corre sus propios agent loops usando el Agent SDK, y no una capa de configuración sobre el CLI de Claude Code.
**Riesgo si es falso:** si el usuario en realidad concibe el harness como configuración/orquestación sobre el CLI existente, cambiaría de forma importante el diseño técnico y el plan de implementación.
**Estado:** RESUELTO/CONFIRMADO (2026-07-23) — el usuario confirmó explícitamente que el harness es un programa Python propio (ref T-008).

### A-003 — El soporte multi-vendor (Codex u otros) queda abierto para el futuro
**Fecha:** 2026-07-23
**Supuesto:** hoy el harness se construye pensando en Claude Code; a futuro se contempla dar soporte a Codex u otros proveedores, pero no quedó definido si esto es una restricción de v1 o una meta posterior.
**Riesgo si es falso:** si en realidad se espera soporte multi-vendor desde v1, decisiones de diseño actuales (acopladas a Claude Code / Agent SDK de Anthropic) podrían requerir revisión.
**Estado:** vigente — pendiente de definición explícita (ref T-010).

### A-004 — Riesgo: el descubrimiento de skills empaquetadas dentro de sda no está confirmado cuando el cwd es el proyecto destino
**Fecha:** 2026-07-23
**Supuesto:** las skills del Agent SDK se descubren desde los *setting sources* (típicamente `.claude/skills/` relativo al `cwd` del proceso). Como el harness (`sda`) correrá con el `cwd` del proyecto destino (no el del propio paquete `sda`), se está asumiendo, sin confirmar, que el SDK descubrirá igualmente las skills empaquetadas dentro de `src/sda/skills/`.
**Riesgo si es falso:** si el SDK no descubre skills empaquetadas fuera del `cwd`, el diseño de `skills/` (ver D-016) requeriría un mecanismo adicional (copiar/enlazar skills al proyecto destino, o registrar setting sources adicionales) antes de poder comprometerse.
**Estado:** vigente — requiere un spike de verificación dedicado (ref T-017) antes de comprometer el diseño final de `skills/`.

<!--
### A-001 — Título breve
**Fecha:** YYYY-MM-DD
**Supuesto:** qué se está asumiendo
**Riesgo si es falso:** qué pasa si el supuesto no se cumple
**Estado:** vigente | invalidado
-->
