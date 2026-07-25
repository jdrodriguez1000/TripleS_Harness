"""Herramientas en-proceso con las que el líder escribe la memoria del proyecto (T-029).

Son el **único** camino por el que el ``orchestrator-leader`` puede tocar
``_persistence/``. No es una preferencia de estilo: el sandbox duro del líder es de
solo lectura (``builtin_tools=["Read","Glob","Grep"]`` en ``orchestrator.py``), y darle
un ``Write`` genérico para que llevara su bitácora reabriría el agujero que se cerró
en T-028 —podría escribir ``_harness_state.json`` o forzar un ``APPROVED`` saltándose
la puerta de aprobación (L-013).

Al pasar por aquí, tres cosas quedan garantizadas por Python y no por el juicio del
modelo: el **formato** de cada entrada, la **numeración** correlativa (``T-001``,
``D-004``…) y que la escritura ocurra **dentro de** ``_persistence/`` —el líder nunca
pasa una ruta. Es el principio de D-026 aplicado a la memoria: el LLM decide *qué*
vale la pena registrar; la herramienta hace cumplir *cómo* se registra.
"""

from __future__ import annotations

from pathlib import Path

from sda import memory
from sda.core.tool import InProcessTool


def _texto(args: dict, clave: str) -> str:
    """Lee un argumento de texto del modelo, tolerando ausencias y ``None``.

    Los campos opcionales se declaran igual que los obligatorios en el esquema del
    SDK, así que el modelo los manda como cadena vacía cuando no aplican.
    """
    return (args.get(clave) or "").strip()


class MemoryTools:
    """Herramientas de escritura sobre la memoria del proyecto destino.

    Un objeto por ejecución del orquestador, ligado a la carpeta del proyecto. No
    guarda estado propio: la verdad vive en los archivos de ``_persistence/``, que el
    humano puede editar a mano entre turnos.
    """

    def __init__(self, project_dir: Path) -> None:
        self._project_dir = project_dir

    def as_in_process_tools(self) -> list[InProcessTool]:
        """Devuelve las herramientas de memoria listas para registrar en la sesión."""
        return [
            InProcessTool(
                name="record_progress",
                description=(
                    "Registra un avance en la bitácora del proyecto "
                    "(_persistence/progress.md). Úsala cuando algo quede realmente "
                    "terminado o cambie el estado del proyecto, no para narrar cada "
                    "turno. 'title' es una línea corta; 'detail' amplía (puede ir "
                    "vacío). La fecha la pone el harness."
                ),
                handler=self._record_progress,
                parameters={"title": str, "detail": str},
            ),
            InProcessTool(
                name="record_task",
                description=(
                    "Crea una tarea nueva en _persistence/tasks.md, en estado "
                    "Pendiente. El código (T-XXX) lo asigna el harness: no lo "
                    "inventes ni lo pases. 'detail' puede ir vacío. Devuelve el "
                    "código asignado para que se lo puedas decir al humano."
                ),
                handler=self._record_task,
                parameters={"title": str, "detail": str},
            ),
            InProcessTool(
                name="update_task",
                description=(
                    "Cambia el estado de una tarea existente. 'code' es su código "
                    "(p. ej. T-003) y 'status' uno de: Pendiente, En curso, "
                    "Completada, Cancelada. 'note' es una anotación opcional sobre "
                    "el cambio. Rechazará ejecutarse si la tarea no existe."
                ),
                handler=self._update_task,
                parameters={"code": str, "status": str, "note": str},
            ),
            InProcessTool(
                name="record_decision",
                description=(
                    "Registra una decisión del proyecto en _persistence/decisions.md. "
                    "Úsala cuando el humano y tú acuerden algo que cambia el rumbo "
                    "(alcance, tecnología, prioridad) y que alguien podría "
                    "cuestionar más adelante. 'decision' es qué se decidió y "
                    "'reason' por qué. El código (D-XXX) lo asigna el harness."
                ),
                handler=self._record_decision,
                parameters={"title": str, "decision": str, "reason": str},
            ),
            InProcessTool(
                name="record_lesson",
                description=(
                    "Registra una lección aprendida en _persistence/lessons.md. "
                    "Úsala cuando algo salga mal, sorprenda, o revele una "
                    "preferencia del humano que convenga recordar en futuras "
                    "sesiones. 'lesson' es la conclusión aplicable y 'context' qué "
                    "la originó. El código (L-XXX) lo asigna el harness."
                ),
                handler=self._record_lesson,
                parameters={"title": str, "lesson": str, "context": str},
            ),
        ]

    # --- Implementación de las herramientas ----------------------------------

    async def _record_progress(self, args: dict) -> str:
        try:
            fecha = memory.append_progress(
                self._project_dir, _texto(args, "title"), _texto(args, "detail")
            )
        except memory.MemoriaError as exc:
            return f"RECHAZADO: {exc}"
        return f"REGISTRADO: avance anotado en la bitácora con fecha {fecha}."

    async def _record_task(self, args: dict) -> str:
        try:
            codigo = memory.add_task(
                self._project_dir, _texto(args, "title"), _texto(args, "detail")
            )
        except memory.MemoriaError as exc:
            return f"RECHAZADO: {exc}"
        return f"REGISTRADA: la tarea quedó como {codigo}, en estado Pendiente."

    async def _update_task(self, args: dict) -> str:
        codigo = _texto(args, "code")
        estado = _texto(args, "status")
        try:
            memory.update_task(
                self._project_dir, codigo, estado, _texto(args, "note")
            )
        except memory.MemoriaError as exc:
            return f"RECHAZADO: {exc}"
        return f"ACTUALIZADA: {codigo.upper()} pasó a estado {estado}."

    async def _record_decision(self, args: dict) -> str:
        try:
            codigo = memory.add_decision(
                self._project_dir,
                _texto(args, "title"),
                _texto(args, "decision"),
                _texto(args, "reason"),
            )
        except memory.MemoriaError as exc:
            return f"RECHAZADO: {exc}"
        return f"REGISTRADA: la decisión quedó como {codigo}."

    async def _record_lesson(self, args: dict) -> str:
        try:
            codigo = memory.add_lesson(
                self._project_dir,
                _texto(args, "title"),
                _texto(args, "lesson"),
                _texto(args, "context"),
            )
        except memory.MemoriaError as exc:
            return f"RECHAZADO: {exc}"
        return f"REGISTRADA: la lección quedó como {codigo}."
