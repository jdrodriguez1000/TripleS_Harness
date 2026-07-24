"""Herramientas en-proceso del harness (el límite de seguridad del líder).

Este paquete aloja las funciones Python que el ``orchestrator-leader`` invoca como
herramientas (D-016). Son el **límite determinista** entre el juicio del LLM y los
efectos peligrosos: el líder solo puede tocar el estado del harness, conducir el
bucle interno o promover un entregable **a través de ellas** (D-026).

No importa el SDK (D-010) ni conoce la lógica de agentes (D-012): usa las
abstracciones ``Provider``/``Session``/``InProcessTool`` de ``sda.core``.
"""

from __future__ import annotations

from sda.tools.leader_tools import LeaderTools

__all__ = ["LeaderTools"]
