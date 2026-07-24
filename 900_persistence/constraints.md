# Constraints

> Restricciones y limitaciones del proyecto.

## Índice

- [C-001 — Un evaluador de calidad basado en LLM consume suscripción y puede encarecer el bucle interno](#c-001--un-evaluador-de-calidad-basado-en-llm-consume-suscripción-y-puede-encarecer-el-bucle-interno)
- [C-002 — El modo no interactivo del Agent SDK requiere permission_mode="bypassPermissions" y ToolSearch en allowed_tools](#c-002--el-modo-no-interactivo-del-agent-sdk-requiere-permission_modebypasspermissions-y-toolsearch-en-allowed_tools)
- [C-003 — No se puede eliminar una variable de entorno heredada del subproceso del SDK, solo sobrescribirla](#c-003--no-se-puede-eliminar-una-variable-de-entorno-heredada-del-subproceso-del-sdk-solo-sobrescribirla)
- [C-004 — Las skills son un filtro de contexto, no un sandbox de seguridad](#c-004--las-skills-son-un-filtro-de-contexto-no-un-sandbox-de-seguridad)

## Detalle

### C-001 — Un evaluador de calidad basado en LLM consume suscripción y puede encarecer el bucle interno
**Tipo:** técnica / recursos
**Descripción:** si el evaluador de calidad interna se implementa como un agente-LLM que juzga cada turno del loop interno, cada evaluación consume cuota/uso de la suscripción usada para autenticar el Agent SDK, lo que puede encarecer o limitar el bucle interno según el volumen de turnos evaluados.
**Origen:** advertencia planteada por el agente durante la sesión al discutir el evaluador y el umbral "4.0" mencionado en `idea.md`; aún no verificada con datos reales de costo/cuota.

### C-002 — El modo no interactivo del Agent SDK requiere permission_mode="bypassPermissions" y ToolSearch en allowed_tools
**Tipo:** técnica
**Descripción:** al usar `ClaudeAgentOptions` en modo no interactivo (sin humano respondiendo diálogos de permiso), es obligatorio fijar `permission_mode="bypassPermissions"`; sin él, el turno muere en el primer diálogo de permiso. Además es obligatorio incluir `ToolSearch` en `allowed_tools`; sin él falla la carga diferida del esquema de herramientas MCP.
**Origen:** verificado en vivo en el repo experimental `Harness_TripleS` al hacer funcionar `ClaudeSDKClient` en modo automatizado.

### C-003 — No se puede eliminar una variable de entorno heredada del subproceso del SDK, solo sobrescribirla
**Tipo:** técnica
**Descripción:** el Agent SDK arma el entorno del subproceso `claude` como `{**os.environ, **options.env}` y no permite borrar una variable heredada del proceso padre; solo se puede sobrescribir a cadena vacía vía `ClaudeAgentOptions(env=...)`, y el CLI trata `""` como ausente. Por eso `os.environ.pop("ANTHROPIC_API_KEY")` por sí solo no basta para forzar la autenticación por suscripción si la variable estaba presente en el proceso padre: hay que hacer las dos cosas (pop en el proceso padre y sobrescritura a `""` en `options.env`).
**Origen:** verificado en vivo en el repo experimental `Harness_TripleS`; ver A-001 (autenticación por suscripción) y L-004.

### C-004 — Las skills son un filtro de contexto, no un sandbox de seguridad
**Tipo:** técnica / seguridad
**Descripción:** el parámetro `skills` de `ClaudeAgentOptions` filtra qué skills quedan visibles para el modelo (nombres o `"all"`), pero una skill no listada sigue presente en disco y es alcanzable con `Read`/`Bash` si el agente tiene esas herramientas. No es un mecanismo de aislamiento; no se deben guardar secretos dentro de una skill asumiendo que "ocultarla" del listado la protege.
**Origen:** confirmado contra documentación oficial del SDK (`/anthropics/claude-agent-sdk-python`, vía ctx7) durante esta sesión. Ver D-016 (estructura de `skills/`) y A-004 (riesgo de descubrimiento de skills empaquetadas).

<!--
### C-001 — Título breve
**Tipo:** técnica | negocio | tiempo | recursos | legal
**Descripción:** en qué consiste la restricción
**Origen:** quién/qué la impone
-->
