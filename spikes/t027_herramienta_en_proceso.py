"""Spike T-027 — herramienta en-proceso que conduce un bucle interno observable.

Pregunta a responder (riesgo de §6.2 del diseño T-027): ¿puede el SDK, **bajo
autenticación por suscripción y modo no interactivo** (``bypassPermissions``),
darle a un agente LÍDER (Opus+high) una **herramienta en-proceso** (``@tool`` +
``create_sdk_mcp_server``) cuya implementación sea **código Python nuestro** que, al
invocarse, conduzca una **segunda ``Session``** (el bucle interno, Sonnet+high) y
devuelva su resultado al líder — todo mientras NOSOTROS observamos cada turno del
bucle interno?

Si la respuesta es sí, queda verificado el mecanismo que reconcilia "un agente
lidera el bucle externo" con la observabilidad turno-a-turno de D-021 (ver
D-027 propuesta): la herramienta es una *puerta de vuelta a nuestro código*.

Diseño de la prueba (end-to-end, con secreto aleatorio para que sea inobjetable):

  1. Definimos la herramienta en-proceso ``run_inner_probe(instruction)``. Su
     implementación Python: (a) registra que fue invocada en ``OBSERVED``
     (prueba de que corrió NUESTRO código), (b) genera un ``secreto`` aleatorio,
     (c) abre una SEGUNDA ``Session`` (bucle interno, Sonnet) y le pide devolver
     ``INNER_OK:<secreto>``, (d) CAPTURA y guarda el turno del bucle interno en
     ``OBSERVED`` (prueba de observabilidad), (e) devuelve un resumen con el
     secreto al líder.
  2. El líder (Opus+high) recibe del humano: "ejecuta el sondeo interno y dime el
     token exacto que devolvió". El líder DEBE llamar la herramienta.
  3. Veredicto — se exige que se cumplan las tres cosas:
       * ``OBSERVED`` contiene el registro de invocación   -> corrió nuestro Python.
       * ``OBSERVED`` contiene el turno del bucle interno   -> observabilidad real.
       * la respuesta final del líder contiene el secreto   -> el resultado del
         bucle interno viajó de vuelta al líder y de este al humano. Como el
         secreto es aleatorio, el líder NO podría saberlo sin llamar la herramienta.

Ver D-011: los spikes viven fuera de ``src/`` y tienen fecha de caducidad. Al
responder la pregunta, este material se borra o el mecanismo se promueve a ``src/``.
El script importa el SDK directamente: es código experimental fuera de ``src/``; el
límite de D-010 (SDK solo en ``providers/``) aplica al paquete de producción.
"""

from __future__ import annotations

import secrets

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

# Reutiliza la política de autenticación por suscripción del proveedor (L-004, C-003).
from sda.providers.claude_sdk import _subscription_env

# Modelos/effort fieles al diseño: líder Opus+high, bucle interno Sonnet+high (D-025).
_LEADER_MODEL = "opus"
_LEADER_EFFORT = "high"
_INNER_MODEL = "sonnet"
_INNER_EFFORT = "high"

# Bitácora de observabilidad: TODO lo que nuestro código Python ve queda aquí. Que
# esté poblada al final es la prueba de que la ejecución fue nuestra, no del SDK.
OBSERVED: list[str] = []


async def _run_inner_session(instruction: str) -> str:
    """Conduce una SEGUNDA ``Session`` (el bucle interno) y observa su turno.

    Es el equivalente, en miniatura, de lo que en producción sería
    ``run_inner_loop`` conduciendo al ``onboarding-reader``: abre una sesión aparte,
    le manda un turno, captura su respuesta y la registra en ``OBSERVED``.
    """
    opciones = ClaudeAgentOptions(
        model=_INNER_MODEL,
        effort=_INNER_EFFORT,
        permission_mode="bypassPermissions",
        allowed_tools=["ToolSearch"],
        env=_subscription_env(),
    )
    partes: list[str] = []
    inner = ClaudeSDKClient(opciones)
    await inner.connect()
    try:
        await inner.query(instruction)
        async for msg in inner.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        partes.append(block.text)
    finally:
        await inner.disconnect()
    texto = "".join(partes).strip()
    OBSERVED.append(f"[inner-turn] {texto!r}")
    return texto


@tool(
    "run_inner_probe",
    "Ejecuta el sondeo del bucle interno y devuelve el token que produjo.",
    {"instruction": str},
)
async def run_inner_probe(args: dict) -> dict:
    """Herramienta en-proceso del líder: puerta de vuelta a NUESTRO código Python.

    El líder solo decide *cuándo* llamarla y *con qué* ``instruction``; la ejecución
    (incluida la conducción del bucle interno) es 100% nuestra y observable.
    """
    OBSERVED.append(f"[tool-invoked] instruction={args.get('instruction')!r}")

    secreto = f"T027-{secrets.token_hex(4)}"
    instruccion_interna = (
        "Responde EXCLUSIVAMENTE con esta única línea, sin ningún otro texto:\n"
        f"INNER_OK:{secreto}"
    )
    texto_interno = await _run_inner_session(instruccion_interna)

    # Comprobamos, desde nuestro código, que el bucle interno hizo lo pedido.
    interno_ok = secreto in texto_interno
    OBSERVED.append(f"[tool-eval] secreto_en_respuesta_interna={interno_ok}")

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    "El sub-bucle interno terminó. Resumen ejecutivo: el bucle "
                    f"interno produjo el token {secreto}."
                ),
            }
        ]
    }


_LEADER_SYSTEM = (
    "Eres el orchestrator-leader, el agente líder del harness. Cuando el humano te "
    "pida ejecutar el sondeo del bucle interno, DEBES usar la herramienta "
    "run_inner_probe (pásale una instruccion breve). Cuando la herramienta te "
    "responda, reporta al humano el token EXACTO que devolvió, tal cual."
)


async def main() -> None:
    server = create_sdk_mcp_server("harness", tools=[run_inner_probe])
    opciones_lider = ClaudeAgentOptions(
        model=_LEADER_MODEL,
        effort=_LEADER_EFFORT,
        system_prompt=_LEADER_SYSTEM,
        permission_mode="bypassPermissions",
        mcp_servers={"harness": server},
        allowed_tools=["ToolSearch", "mcp__harness__run_inner_probe"],
        env=_subscription_env(),
    )

    print(f"líder:        {_LEADER_MODEL}+{_LEADER_EFFORT}")
    print(f"bucle interno:{_INNER_MODEL}+{_INNER_EFFORT}")
    print("herramienta:  mcp__harness__run_inner_probe (en-proceso)\n")

    partes_lider: list[str] = []
    lider = ClaudeSDKClient(opciones_lider)
    await lider.connect()
    try:
        await lider.query(
            "Ejecuta el sondeo del bucle interno y dime el token EXACTO que devolvió."
        )
        async for msg in lider.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        partes_lider.append(block.text)
    finally:
        await lider.disconnect()
    respuesta_lider = "".join(partes_lider).strip()

    print("----- observabilidad (lo que vio NUESTRO código) -----")
    for linea in OBSERVED:
        print("  ", linea)
    print("----- respuesta final del líder al humano -----")
    print("  ", repr(respuesta_lider), "\n")

    # --- Veredicto: las tres condiciones deben cumplirse ---------------------
    corrio_nuestro_codigo = any(o.startswith("[tool-invoked]") for o in OBSERVED)
    hubo_observabilidad = any(o.startswith("[inner-turn]") for o in OBSERVED)

    # El secreto que el líder debe reportar es el que capturamos del turno interno.
    secreto_capturado = ""
    for o in OBSERVED:
        if o.startswith("[inner-turn]") and "INNER_OK:" in o:
            secreto_capturado = o.split("INNER_OK:", 1)[1].split("'", 1)[0].strip()
            break
    secreto_llego_al_humano = bool(secreto_capturado) and secreto_capturado in respuesta_lider

    assert corrio_nuestro_codigo, (
        "FALLO: el líder no invocó la herramienta en-proceso; no corrió nuestro "
        "código Python. El mecanismo no funciona bajo esta configuración."
    )
    assert hubo_observabilidad, (
        "FALLO: la herramienta no logró conducir/observar la segunda Session "
        "(bucle interno) desde dentro del callback del líder."
    )
    assert secreto_llego_al_humano, (
        "FALLO: el líder no reportó el token del bucle interno; el resultado no "
        f"viajó de vuelta. secreto_capturado={secreto_capturado!r}, "
        f"respuesta={respuesta_lider!r}"
    )

    print(
        "SPIKE T-027 OK: bajo suscripción + modo no interactivo, el líder (Opus) "
        "invocó una herramienta EN-PROCESO que condujo una segunda Session (bucle "
        "interno, Sonnet) de forma OBSERVABLE, y su resultado regresó al líder. "
        "Mecanismo de D-027 verificado: la herramienta es la puerta de vuelta a "
        "nuestro código, preservando la observabilidad de D-021."
    )


if __name__ == "__main__":
    anyio.run(main)
