"""Contrato de herramienta en-proceso: ``InProcessTool``.

Una **herramienta en-proceso** es una función Python nuestra que un agente LLM
puede invocar. El modelo solo decide *cuándo* llamarla y *con qué* argumentos; la
ejecución es 100% nuestra (D-027). Es la "puerta de vuelta a nuestro código" que
permite que el ``orchestrator-leader`` lidere el bucle externo sin sacrificar la
observabilidad del bucle interno (D-021).

Esta abstracción es **agnóstica del proveedor**: no importa ningún SDK (D-010). El
``Provider`` concreto (``sda.providers``) la traduce a lo que su SDK requiera (para
``claude_agent_sdk``: ``@tool`` + ``create_sdk_mcp_server``). Así ``sda.tools`` puede
implementar la lógica de dominio de las herramientas sin conocer el SDK ni la lógica
de agentes (D-012).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

# Un handler recibe los argumentos ya deserializados (dict) y devuelve el **texto**
# que verá el agente que la invocó. La forma cruda que exija el SDK (p. ej.
# ``{"content": [{"type": "text", ...}]}``) la arma el proveedor, no el dominio.
InProcessToolHandler = Callable[[dict[str, Any]], Awaitable[str]]


@dataclass
class InProcessTool:
    """Descriptor SDK-agnóstico de una herramienta en-proceso del líder.

    - ``name``: nombre corto (p. ej. ``"run_inner_loop"``). El proveedor lo expone
      al modelo con el prefijo que su SDK dicte (para el Agent SDK,
      ``mcp__<server>__<name>``).
    - ``description``: qué hace, en lenguaje natural, para que el modelo sepa cuándo
      llamarla.
    - ``parameters``: esquema de entrada como ``{nombre: tipo}`` (p. ej.
      ``{"instruction": str}``); ``{}`` para herramientas sin argumentos.
    - ``handler``: la función Python asíncrona que se ejecuta al invocarla.
    """

    name: str
    description: str
    handler: InProcessToolHandler
    parameters: dict[str, type] = field(default_factory=dict)
