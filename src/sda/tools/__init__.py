"""Herramientas en-proceso del harness (el límite de seguridad del líder).

Este paquete aloja las funciones Python que el ``orchestrator-leader`` invoca como
herramientas (D-016). Son el **límite determinista** entre el juicio del LLM y los
efectos peligrosos: el líder solo puede tocar el estado del harness, conducir el
bucle interno, promover un entregable o escribir la memoria del proyecto **a través
de ellas** (D-026).

Se agrupan por responsabilidad: ``LeaderTools`` conduce el flujo (scope, bucle
interno, puerta de aprobación) y ``MemoryTools`` mantiene la bitácora del proyecto
destino (T-029). El orquestador registra ambos conjuntos en la misma sesión.

No importa el SDK (D-010) ni conoce la lógica de agentes (D-012): usa las
abstracciones ``Provider``/``Session``/``InProcessTool`` de ``sda.core``.
"""

from __future__ import annotations

from sda.tools.leader_tools import LeaderTools
from sda.tools.memory_tools import MemoryTools

__all__ = ["LeaderTools", "MemoryTools"]
