"""Contrato de proveedor de modelos: ``Provider``, la fábrica de sesiones.

Un ``Provider`` es lo único que sabe cómo fabricar una ``Session`` concreta. Es
agnóstico del SDK: la implementación real (p. ej. ``ClaudeSDKProvider``) vive en
``sda.providers`` y es la única que importa ``claude_agent_sdk`` (ver D-009, D-010).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from sda.core.session import Session
from sda.core.tool import InProcessTool


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
        builtin_tools: list[str] | None = None,
        model: str | None = None,
        effort: str | None = None,
        in_process_tools: list[InProcessTool] | None = None,
    ) -> Session:
        """Crea (aún sin conectar) una ``Session`` lista para usarse.

        Todos los parámetros son opcionales y agnósticos del proveedor; las
        subclases los traducen a lo que su SDK requiera:

        - ``system_prompt``: rol/instrucciones de la sesión.
        - ``cwd``: carpeta de trabajo del agente (p. ej. el proyecto que debe
          explorar el bucle interno). Si es ``None``, hereda el del proceso.
        - ``allowed_tools``: herramientas que se **auto-aprueban** sin pedir permiso.
          NO restringe el conjunto disponible (ver ``builtin_tools``); bajo modo no
          interactivo su efecto es marginal. Si es ``None``, la subclase aplica su
          política por defecto.
        - ``builtin_tools``: **conjunto base real** de herramientas nativas que la
          sesión puede usar (mapea al ``tools`` del SDK). Este sí es un límite duro:
          una herramienta que no esté aquí no existe para el agente. Es el mecanismo
          de sandbox de verdad (p. ej. dar al líder solo lectura ``["Read","Glob",
          "Grep"]`` para que no pueda escribir estado ni entregables por fuera de sus
          herramientas en-proceso). Si es ``None``, hereda el toolset completo.
        - ``model``: modelo a usar para esta sesión (p. ej. ``"sonnet"``). Permite
          fijar el modelo por agente. Si es ``None``, cae al default del proveedor.
        - ``effort``: nivel de esfuerzo de razonamiento (``low|medium|high|xhigh|max``).
          Fija el esfuerzo por agente. Si es ``None``, cae al default del proveedor.
        - ``in_process_tools``: herramientas en-proceso (código Python nuestro) que
          esta sesión puede invocar. La subclase las registra como corresponda a su
          SDK (para el Agent SDK, un servidor MCP en-proceso) y añade sus nombres a
          las herramientas permitidas. Es el mecanismo que hace del líder un agente
          sin perder el control determinista de los efectos (D-026, D-027).
        """
        raise NotImplementedError
