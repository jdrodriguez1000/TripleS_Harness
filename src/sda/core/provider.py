"""Contrato de proveedor de modelos: ``Provider``, la fábrica de sesiones.

Un ``Provider`` es lo único que sabe cómo fabricar una ``Session`` concreta. Es
agnóstico del SDK: la implementación real (p. ej. ``ClaudeSDKProvider``) vive en
``sda.providers`` y es la única que importa ``claude_agent_sdk`` (ver D-009, D-010).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from sda.core.session import Session


class Provider(ABC):
    """Fábrica de sesiones de conversación.

    Mantiene una sola cadena de abstracción: ``Provider`` crea ``Session`` (D-009).
    Las subclases pueden recibir configuración propia del proveedor en su
    ``__init__`` (credenciales, modelo, opciones del SDK, etc.).
    """

    @abstractmethod
    def create_session(self, *, system_prompt: str | None = None) -> Session:
        """Crea (aún sin conectar) una ``Session`` lista para usarse.

        ``system_prompt`` es un parámetro opcional y agnóstico del proveedor; las
        subclases lo traducen a lo que su SDK requiera.
        """
        raise NotImplementedError
