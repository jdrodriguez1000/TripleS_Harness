"""Spike T-016 — sesión persistente sobre suscripción con contexto entre turnos.

Pregunta a responder: una misma ``Session`` (``ClaudeSDKSession``), sin reconectar
entre turnos, ¿conserva el contexto de un ``send`` a otro?

Ver D-011: los spikes viven fuera de src/ y tienen fecha de caducidad — si la
pregunta queda respondida, este archivo se promueve a producto o se borra.

Verificado en vivo (2026-07-24), instalando el paquete `sda` en modo editable
desde un proyecto externo (`sda_test_002`, fuera de este repo) y ejecutando este
mismo script: T1 respondió "ok" y T2 respondió "Verde", confirmando que la
sesión recuerda el turno anterior sin reconectar.
"""

from __future__ import annotations

import anyio

from sda.providers.claude_sdk import ClaudeSDKProvider


async def main() -> None:
    provider = ClaudeSDKProvider()
    async with provider.create_session() as session:
        r1 = await session.send("Mi color favorito es el verde. Respondé solo 'ok'.")
        print("T1:", r1.text)

        r2 = await session.send("¿Cuál dije que era mi color favorito?")
        print("T2:", r2.text)

        assert "verde" in r2.text.lower(), "la sesión no conservó el contexto entre turnos"

    print("SPIKE T-016 OK: contexto conservado entre turnos sin reconectar.")


if __name__ == "__main__":
    anyio.run(main)
