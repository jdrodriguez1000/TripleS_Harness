# CLAUDE.md

## Protocolo de sesión (obligatorio)

Este proyecto usa la carpeta `900_persistence/` como memoria persistente del proyecto (avance, tareas, lecciones, decisiones, supuestos y restricciones). Para mantenerla al día, es OBLIGATORIO lo siguiente:

- **Al iniciar o reanudar una sesión**: invocar el agente `session-starter` (skill `session-start-protocol`) antes de comenzar cualquier trabajo. Se activa con frases como "iniciemos la sesión", "continuemos la sesión", "iniciemos", "trabajemos" o similares.
- **Al cerrar, terminar o pausar una sesión**: invocar el agente `session-closer` (skill `session-end-protocol`) antes de dar la sesión por terminada. Se activa con frases como "cerremos la sesión", "terminemos por hoy", "guardemos el avance" o similares.

Es OBLIGATORIO Y EXCLUSIVO que estos dos protocolos se ejecuten a través de los subagentes correspondientes (`session-starter` y `session-closer`), invocados mediante el mecanismo de subagentes (Agent/Task). El agente principal NUNCA debe ejecutar directamente los pasos de lectura o actualización de `900_persistence/` en nombre de estos protocolos; siempre debe delegarlos al subagente respectivo, incluso si el avance de la sesión fue mínimo.
