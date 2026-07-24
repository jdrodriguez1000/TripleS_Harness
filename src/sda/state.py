"""Máquina de estados persistente del harness: ``_harness_state.json``.

Es la memoria de control del doble bucle (ver ``idea.md``): en qué fase está el
proyecto, cuál REPL tiene el control, si hay una transacción en marcha y qué
archivo espera aprobación del humano. Vive en la raíz de la carpeta del proyecto
destino, no del harness.

Esta rebanada implementa un estado mínimo pero honesto; el checkpointing fino y
la recuperación de una transacción interrumpida quedan para más adelante.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Nombre del archivo de estado dentro de la carpeta del proyecto.
STATE_FILENAME = "_harness_state.json"

# Fases del ciclo de vida (subconjunto usado en esta rebanada).
PHASE_BOOTSTRAPPING = "BOOTSTRAPPING"
PHASE_ONBOARDING = "ONBOARDING"
PHASE_HUMAN_REVIEW = "HUMAN_REVIEW"
PHASE_READY_FOR_WORK = "READY_FOR_WORK"

# Identificadores de cuál REPL tiene el control.
REPL_EXTERNAL = "EXTERNAL"
REPL_INTERNAL = "INTERNAL"


@dataclass
class HarnessState:
    """Estado del harness serializable a ``_harness_state.json``.

    Los campos replican los de ``idea.md``. ``transaction_lock`` avisa que hay un
    proceso interno en marcha que no debe alterarse; ``pending_approval_file``
    recuerda, entre ejecuciones, qué entregable quedó esperando al humano.
    """

    current_phase: str = PHASE_BOOTSTRAPPING
    active_repl: str = REPL_EXTERNAL
    active_subagent: str | None = None
    transaction_lock: bool = False
    pending_approval_file: str | None = None
    # Campos extra ignorados por defecto: se preservan al releer para no perder
    # información escrita por versiones futuras.
    extra: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Aplana el estado a un dict JSON (``extra`` se fusiona al nivel raíz)."""
        data = asdict(self)
        extra = data.pop("extra")
        data.update(extra)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> HarnessState:
        """Reconstruye el estado, guardando campos desconocidos en ``extra``."""
        known = {f for f in cls.__dataclass_fields__ if f != "extra"}
        base = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**base, extra=extra)


def state_path(project_dir: Path) -> Path:
    """Ruta del ``_harness_state.json`` para un proyecto dado."""
    return project_dir / STATE_FILENAME


def exists(project_dir: Path) -> bool:
    """Indica si el proyecto ya tiene un ``_harness_state.json``."""
    return state_path(project_dir).is_file()


def load(project_dir: Path) -> HarnessState:
    """Lee y deserializa el estado del proyecto."""
    raw = state_path(project_dir).read_text(encoding="utf-8")
    return HarnessState.from_dict(json.loads(raw))


def save(project_dir: Path, state: HarnessState) -> None:
    """Escribe el estado de forma atómica (write-to-temp + ``os.replace``).

    La escritura atómica evita dejar un ``_harness_state.json`` a medias si el
    proceso muere en mitad del volcado.
    """
    target = state_path(project_dir)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(
        json.dumps(state.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    os.replace(tmp, target)
