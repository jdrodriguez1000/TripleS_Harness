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
    def create_session(
        self,
        *,
        system_prompt: str | None = None,
        cwd: str | None = None,
        allowed_tools: list[str] | None = None,
        model: str | None = None,
        effort: str | None = None,
    ) -> Session:
        """Crea (aún sin conectar) una ``Session`` lista para usarse.

        Todos los parámetros son opcionales y agnósticos del proveedor; las
        subclases los traducen a lo que su SDK requiera:

        - ``system_prompt``: rol/instrucciones de la sesión.
        - ``cwd``: carpeta de trabajo del agente (p. ej. el proyecto que debe
          explorar el bucle interno). Si es ``None``, hereda el del proceso.
        - ``allowed_tools``: herramientas que la sesión puede usar. Si es ``None``,
          la subclase aplica su política por defecto.
        - ``model``: modelo a usar para esta sesión (p. ej. ``"sonnet"``). Permite
          fijar el modelo por agente. Si es ``None``, cae al default del proveedor.
        - ``effort``: nivel de esfuerzo de razonamiento (``low|medium|high|xhigh|max``).
          Fija el esfuerzo por agente. Si es ``None``, cae al default del proveedor.
        """
        raise NotImplementedError
