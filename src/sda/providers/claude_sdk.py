"""Proveedor concreto sobre el Agent SDK de Anthropic (``claude_agent_sdk``).

Es la única implementación de ``Provider`` por ahora y el único módulo del
proyecto que importa el SDK (D-010). Autentica **por suscripción**, no con API
key: el SDK levanta el CLI ``claude`` como subproceso y, en ausencia de las
variables de entorno de API, cae a las credenciales OAuth de
``~/.claude/.credentials.json`` (A-001, L-004).
"""

from __future__ import annotations

import os

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

from sda.core.provider import Provider
from sda.core.session import Session, TurnResult
from sda.core.tool import InProcessTool

# Variables de entorno que, si están presentes, harían que el SDK autentique con
# API key/token en lugar de la suscripción. Ver L-004, C-003.
_API_ENV_VARS = ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN")

# Nombre del servidor MCP en-proceso bajo el que se registran las herramientas del
# líder. Los nombres que ve el modelo quedan como ``mcp__<server>__<tool>``.
_MCP_SERVER_NAME = "harness"


def _subscription_env() -> dict[str, str]:
    """Neutraliza la autenticación por API key para forzar la de suscripción.

    Hay que hacer **las dos cosas** (L-004, C-003): borrar la variable del proceso
    padre y sobrescribirla a cadena vacía en ``options.env``, porque el SDK arma el
    entorno del subproceso como ``{**os.environ, **options.env}`` y no permite
    borrar una variable heredada; el CLI trata ``""`` como ausente.
    """
    for name in _API_ENV_VARS:
        os.environ.pop(name, None)
    return {name: "" for name in _API_ENV_VARS}


def _mcp_tool_name(name: str) -> str:
    """Nombre con el que el modelo ve una herramienta del servidor en-proceso."""
    return f"mcp__{_MCP_SERVER_NAME}__{name}"


def _a_sdk_tool(t: InProcessTool):
    """Adapta un ``InProcessTool`` SDK-agnóstico a una herramienta del Agent SDK.

    Envuelve el handler de dominio (que devuelve texto plano) en la forma cruda que
    el SDK espera (``{"content": [{"type": "text", ...}]}``), de modo que ``sda.tools``
    no tenga que conocer el SDK (D-010, D-012). Cada herramienta se define en su
    propia función para que el decorador ``@tool`` capture el ``t`` correcto.
    """

    @tool(t.name, t.description, t.parameters)
    async def _envuelta(args: dict) -> dict:
        texto = await t.handler(args)
        return {"content": [{"type": "text", "text": texto}]}

    return _envuelta


class ClaudeSDKSession(Session):
    """``Session`` sobre ``ClaudeSDKClient``.

    La conexión es perezosa: se abre en el primer ``send`` y se mantiene viva entre
    turnos, de modo que una misma sesión conserva el contexto (base para T-016).
    ``send`` se implementa sobre ``query`` + ``receive_response`` y ``close`` sobre
    ``disconnect`` (D-018).
    """

    def __init__(self, options: ClaudeAgentOptions) -> None:
        self._options = options
        self._client: ClaudeSDKClient | None = None

    async def send(self, prompt: str) -> TurnResult:
        """Envía un turno y devuelve el texto acumulado de la respuesta."""
        if self._client is None:
            self._client = ClaudeSDKClient(self._options)
            # connect() sin prompt inicial: cada turno se manda con query().
            await self._client.connect()

        await self._client.query(prompt)

        partes: list[str] = []
        async for msg in self._client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        partes.append(block.text)

        return TurnResult(text="".join(partes))

    async def close(self) -> None:
        """Cierra la conexión subyacente. Idempotente."""
        if self._client is not None:
            await self._client.disconnect()
            self._client = None


class ClaudeSDKProvider(Provider):
    """Fábrica de ``ClaudeSDKSession`` con autenticación por suscripción.

    Acepta un ``model`` y un ``effort`` opcionales como **defaults del proveedor**;
    cada llamada a ``create_session`` puede sobreescribirlos para fijar modelo y
    esfuerzo **por agente** (T-026). La política de suscripción y los requisitos del
    modo no interactivo (C-002) se aplican de forma fija en ``create_session``.
    """

    def __init__(self, *, model: str | None = None, effort: str | None = None) -> None:
        self._model = model
        self._effort = effort

    def create_session(
        self,
        *,
        system_prompt: str | None = None,
        cwd: str | None = None,
        allowed_tools: list[str] | None = None,
        builtin_tools: list[str] | None = None,
        model: str | None = None,
        effort: str | None = None,
        in_process_tools: list[InProcessTool] | None = None,
    ) -> Session:
        """Crea (aún sin conectar) una ``ClaudeSDKSession`` lista para usarse.

        ``cwd`` fija la carpeta que el agente explora (clave para el bucle interno,
        que debe leer el proyecto destino). ``allowed_tools`` permite darle a una
        sesión su propio conjunto de herramientas: por defecto solo ``ToolSearch``
        (obligatorio en modo no interactivo para la carga diferida de esquemas,
        C-002), pero el onboarding-reader necesita además Read/Glob/Grep/Write.

        ``model`` y ``effort`` fijan explícitamente el modelo y el esfuerzo de
        razonamiento de esta sesión (T-026); si vienen en ``None``, se usa el default
        del proveedor, y si tampoco lo hay, el default implícito del CLI/SDK. El SDK
        acepta ``effort`` en ``low|medium|high|xhigh|max`` (mapeado a ``--effort``).

        ``in_process_tools`` se registran como un **servidor MCP en-proceso** del SDK
        (verificado en el spike T-027); sus nombres (``mcp__harness__<tool>``) se
        añaden automáticamente a las herramientas permitidas para que el modelo pueda
        invocarlas. Es el mecanismo del líder-agente (D-026, D-027).

        ``builtin_tools`` fija el conjunto base de herramientas nativas (``tools`` del
        SDK). A diferencia de ``allowed_tools`` (que solo auto-aprueba), este SÍ es un
        límite duro bajo ``bypassPermissions``: lo verificamos en vivo (una sesión con
        ``tools=["Glob"]`` no pudo leer archivos). Es el sandbox real por agente. Las
        herramientas en-proceso (MCP) no son "builtin" y siguen disponibles aunque
        ``builtin_tools`` sea restrictivo, porque se registran vía ``mcp_servers``.
        """
        modelo = model if model is not None else self._model
        esfuerzo = effort if effort is not None else self._effort

        tools_base = allowed_tools if allowed_tools is not None else ["ToolSearch"]

        opciones: dict[str, object] = {
            "system_prompt": system_prompt,
            # Modo no interactivo: sin humano que responda diálogos de permiso.
            "permission_mode": "bypassPermissions",
            "allowed_tools": list(tools_base),
            "env": _subscription_env(),
        }
        if builtin_tools is not None:
            # Sandbox duro: solo estas herramientas nativas existen para el agente.
            opciones["tools"] = list(builtin_tools)
        if in_process_tools:
            servidor = create_sdk_mcp_server(
                _MCP_SERVER_NAME,
                tools=[_a_sdk_tool(t) for t in in_process_tools],
            )
            opciones["mcp_servers"] = {_MCP_SERVER_NAME: servidor}
            opciones["allowed_tools"] = list(tools_base) + [
                _mcp_tool_name(t.name) for t in in_process_tools
            ]
        if cwd is not None:
            opciones["cwd"] = cwd
        if modelo is not None:
            opciones["model"] = modelo
        if esfuerzo is not None:
            opciones["effort"] = esfuerzo

        return ClaudeSDKSession(ClaudeAgentOptions(**opciones))
