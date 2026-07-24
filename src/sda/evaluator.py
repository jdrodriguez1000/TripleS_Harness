"""Evaluación de calidad interna del borrador (Step 5 de ``idea.md``).

En el flujo definitivo, el bucle interno audita el ``document-extract.md`` contra
una rúbrica y solo lo deja pasar a la puerta humana si supera el umbral 4.0,
exigiendo correcciones al subagente sin molestar al humano.

Por ahora es un **stub deliberado que siempre aprueba**: mantiene el punto de
enganche (el "seam") para conectar la rúbrica real más adelante (T-011) sin
reescribir el orquestador. No borrar: define el contrato que la eval real deberá
cumplir.
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass

# Umbral de calidad objetivo (origen y rúbrica pendientes de definir — T-011).
QUALITY_THRESHOLD = 4.0


@dataclass
class Evaluation:
    """Resultado de auditar un borrador.

    ``passed`` decide si el borrador va a la puerta humana o vuelve al subagente.
    ``feedback`` lleva las correcciones a inyectar cuando ``passed`` es ``False``.
    """

    passed: bool
    score: float | None = None
    feedback: str | None = None


def evaluate_draft(draft_path: Path) -> Evaluation:
    """Audita el borrador. STUB: por ahora siempre aprueba.

    Cuando se implemente la rúbrica real, esta función leerá ``draft_path``,
    puntuará contra ``QUALITY_THRESHOLD`` y devolverá ``feedback`` accionable si
    no lo supera.
    """
    return Evaluation(passed=True, score=None, feedback=None)
