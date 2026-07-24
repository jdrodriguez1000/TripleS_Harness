"""Contrato de conversación con un modelo: ``Session`` y su resultado ``TurnResult``.

Estas abstracciones son agnósticas del proveedor: no importan ningún SDK. La
implementación concreta (p. ej. sobre ``claude_agent_sdk``) vive en ``sda.providers``
y debe respetar este contrato (ver D-009, D-010).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TurnResult:
    """Resultado de un turno de conversación.

    Por ahora solo lleva el texto de la respuesta. Es extensible sin romper el
    contrato: más adelante puede incorporar metadata para la observabilidad y la
    evaluación del bucle interno (p. ej. uso de tokens, mensajes crudos del SDK).
    """

    text: str


class Session(ABC):
    """Conversación multi-turno con un modelo.

    Un disparo de un solo turno es simplemente una sesión que se usa una vez
    (D-009). El contrato es asíncrono porque los proveedores reales (el Agent SDK)
    lo son y porque una sesión persistente con contexto entre turnos requiere un
    cliente async de larga vida.

    Las subclases obtienen soporte de ``async with`` gratis: ``__aexit__`` cierra
    la sesión llamando a ``close()``.
    """

    @abstractmethod
    async def send(self, prompt: str) -> TurnResult:
        """Envía un turno con ``prompt`` y devuelve su ``TurnResult``."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Libera los recursos de la sesión (cierra la conexión subyacente)."""
        raise NotImplementedError

    async def __aenter__(self) -> Session:
        """Entra al contexto asíncrono devolviendo la propia sesión."""
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Sale del contexto asíncrono cerrando la sesión."""
        await self.close()
