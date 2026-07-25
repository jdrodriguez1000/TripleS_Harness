"""Arranque de un proyecto: crea la estructura de carpetas del harness en disco.

Corresponde a la Fase 1 de ``idea.md`` (Bootstrapping). Cuando el humano ejecuta
el harness en una carpeta nueva, aquí se genera toda la estructura base para que
el doble bucle pueda operar. Es **idempotente**: no pisa nada que ya exista.

El humano no crea carpetas a mano; solo edita ``_context/scope.md`` después.
"""

from __future__ import annotations

from pathlib import Path

from sda import memory, state
from sda.resources import load_template

# --- Rutas convenidas dentro de la carpeta del proyecto destino --------------
CONTEXT_DIR = "_context"
TEMPLATES_DIR = "_templates"
PROTOTYPE_DIR = "_prototype"
# La memoria del proyecto la define y siembra ``sda.memory``; se reexporta aquí
# porque este módulo es el que describe la estructura del proyecto destino.
PERSISTENCE_DIR = memory.PERSISTENCE_DIR

SCOPE_FILE = f"{CONTEXT_DIR}/scope.md"
EXTRACT_TEMPLATE_FILE = f"{TEMPLATES_DIR}/document-extract-temp.md"
EXTRACT_FILE = f"{PROTOTYPE_DIR}/document-extract.md"

# Nombre de la plantilla empaquetada que se copia a ``_templates/``.
_EXTRACT_TEMPLATE_NAME = "document-extract-temp.md"

# Contenido inicial de ``_context/scope.md`` que el humano debe rellenar.
_SCOPE_STUB = """\
# Scope del proyecto

<!-- Describe aquí, con tus palabras y sin formalismos, qué quieres construir.
     Ideas generales: el problema, para quién es, qué debería hacer, cualquier
     restricción o preferencia. No te preocupes por el orden ni por que quede
     perfecto: el harness se encarga de ordenarlo y de preguntarte los huecos.

     Cuando termines de escribir, vuelve a la terminal y avísale al harness
     (con tus propias palabras) que ya terminaste. -->
"""


def _write_if_absent(path: Path, content: str) -> bool:
    """Escribe ``content`` en ``path`` solo si no existe. Devuelve si lo creó."""
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def bootstrap(project_dir: Path) -> bool:
    """Crea la estructura base del harness en ``project_dir`` si falta.

    Devuelve ``True`` si realizó el arranque inicial (no existía estado previo) y
    ``False`` si el proyecto ya estaba inicializado (reanudación).
    """
    ya_inicializado = state.exists(project_dir)

    # La memoria se siembra SIEMPRE, no solo en proyectos nuevos: es idempotente y
    # nunca pisa contenido, así que además repara los proyectos anteriores a T-029,
    # cuya carpeta ``_persistence/`` se creaba vacía. Va antes del corte por
    # reanudación justo para poder alcanzarlos (``idea.md``, Fase 1 Step 2).
    memory.seed(project_dir)

    if ya_inicializado:
        return False

    # Carpetas base.
    for sub in (CONTEXT_DIR, TEMPLATES_DIR, PROTOTYPE_DIR):
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    # Stub del scope (insumo del humano) y plantilla del entregable.
    _write_if_absent(project_dir / SCOPE_FILE, _SCOPE_STUB)
    _write_if_absent(
        project_dir / EXTRACT_TEMPLATE_FILE,
        load_template(_EXTRACT_TEMPLATE_NAME),
    )

    # Estado inicial: recién arrancado, a la espera de que el humano llene el scope.
    state.save(
        project_dir,
        state.HarnessState(
            current_phase=state.PHASE_BOOTSTRAPPING,
            active_repl=state.REPL_EXTERNAL,
        ),
    )
    return True
