"""Spike T-017 — descubrimiento de skills empaquetadas desde un cwd externo.

Pregunta a responder (riesgo A-004): cuando el harness corre con el ``cwd`` del
**proyecto destino** (no el del paquete ``sda``), ¿puede exponerle al modelo una
skill que viaja **con el paquete** y no en el ``.claude/`` del proyecto destino?

Lo que dice la doc del SDK (verificado vía ctx7):
- ``skills`` auto-configura ``setting_sources=["user","project"]``.
- Esos sources solo miran ``~/.claude/skills/`` (user) y ``<cwd>/.claude/skills/``
  (project). **No** escanean un directorio interno del paquete instalado.
- El mecanismo nativo para traer skills junto al paquete es ``plugins``
  (``{"type": "local", "path": ...}``).

Este spike lo comprueba en vivo desde un ``cwd`` temporal externo (no este repo):

  1. BASELINE (negativo): una skill "pelada" (estilo ``src/sda/skills/<n>/SKILL.md``),
     que NO está bajo el ``.claude/`` del cwd, con ``skills="all"`` y SIN plugins.
     Se espera que el modelo NO conozca la palabra clave -> confirma A-004.
  2. PLUGIN (positivo): la misma idea de skill, pero empaquetada como plugin local.
     Se espera que el modelo SÍ conozca la palabra clave -> mecanismo confirmado.

Ver D-011: los spikes viven fuera de src/ y tienen fecha de caducidad. Al responder
la pregunta, este material se borra o el mecanismo se promueve a producto en src/.

El script importa el SDK directamente: es código experimental fuera de ``src/``, el
límite de D-010 (SDK solo en ``providers/``) aplica al paquete de producción.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)

# Reutiliza la política de autenticación por suscripción del proveedor (L-004, C-003).
from sda.providers.claude_sdk import _subscription_env

_FIXTURES = Path(__file__).parent / "t017_fixtures"
_BARE_SKILL_ROOT = _FIXTURES / "skill_bare"          # skill "pelada", fuera de todo .claude/
_PLUGIN_PATH = _FIXTURES / "plugin"                  # plugin local con skill empaquetada

_BARE_KEYWORD = "SKILL-T017-BARE-OK"
_PLUGIN_KEYWORD = "SKILL-T017-PLUGIN-OK"


async def _ask(options: ClaudeAgentOptions, prompt: str) -> str:
    """Abre una sesión efímera, manda un turno y devuelve el texto de la respuesta."""
    partes: list[str] = []
    client = ClaudeSDKClient(options)
    await client.connect()
    try:
        await client.query(prompt)
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        partes.append(block.text)
    finally:
        await client.disconnect()
    return "".join(partes)


async def main() -> None:
    # cwd externo: un proyecto destino simulado, vacío y fuera de este repo.
    with tempfile.TemporaryDirectory(prefix="sda_t017_dest_") as dest:
        print(f"cwd destino (externo): {dest}")
        print(f"skill pelada en:       {_BARE_SKILL_ROOT}")
        print(f"plugin en:             {_PLUGIN_PATH}\n")

        base_kwargs: dict[str, object] = {
            "cwd": dest,
            "permission_mode": "bypassPermissions",
            "allowed_tools": ["ToolSearch"],  # skills="all" auto-agrega la tool Skill (C-002)
            "env": _subscription_env(),
        }

        # --- CASO 1: BASELINE negativo (sin plugins) ------------------------------
        baseline = ClaudeAgentOptions(skills="all", **base_kwargs)
        r_bare = await _ask(
            baseline,
            "¿Cuál es la palabra clave secreta del spike T-017 (variante baseline)? "
            "Si tienes una skill que la conozca, úsala. Si no la conoces, di "
            "exactamente 'NO-LA-SE' y nada más.",
        )
        print(f"BASELINE -> {r_bare!r}")

        # --- CASO 2: PLUGIN local (positivo) --------------------------------------
        con_plugin = ClaudeAgentOptions(
            skills="all",
            plugins=[{"type": "local", "path": str(_PLUGIN_PATH)}],
            **base_kwargs,
        )
        r_plugin = await _ask(
            con_plugin,
            "¿Cuál es la palabra clave secreta del spike T-017 (variante plugin)? "
            "Si tienes una skill que la conozca, úsala. Si no la conoces, di "
            "exactamente 'NO-LA-SE' y nada más.",
        )
        print(f"PLUGIN   -> {r_plugin!r}\n")

        # --- Veredicto ------------------------------------------------------------
        bare_visto = _BARE_KEYWORD in r_bare
        plugin_visto = _PLUGIN_KEYWORD in r_plugin

        assert not bare_visto, (
            "INESPERADO: la skill 'pelada' fue descubierta desde un cwd externo; "
            "A-004 no era un riesgo y hay que revisar el análisis."
        )
        assert plugin_visto, (
            "FALLO: el plugin local NO expuso su skill desde un cwd externo; "
            "el mecanismo candidato no funciona, revisar estructura del plugin."
        )

        print(
            "SPIKE T-017 OK: la skill 'pelada' NO se descubre desde un cwd externo "
            "(A-004 confirmado) y el PLUGIN LOCAL SÍ expone su skill empaquetada."
        )


if __name__ == "__main__":
    anyio.run(main)
