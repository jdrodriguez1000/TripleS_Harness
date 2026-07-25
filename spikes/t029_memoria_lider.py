"""Verificación headless de la memoria del proyecto destino (T-029).

Ejecutar con ``python spikes/t029_memoria_lider.py``. No necesita credenciales ni red:
ejercita el módulo determinista ``sda.memory`` y los handlers de ``MemoryTools`` sobre
un proyecto temporal, que es exactamente la parte que el LLM **no** controla.

Cubre: siembra idempotente (incluida la reparación de un proyecto anterior a T-029),
numeración correlativa, sincronía entre la tabla-índice y el detalle de tareas, rechazo
de entradas inválidas, y que el digest muestre lo abierto, oculte lo cerrado y respete
su tope de tamaño.

Lo que NO cubre: que el líder-agente decida bien *cuándo* registrar cada cosa. Eso es
juicio del modelo y se valida a ojo con ``sda start``.
"""

import tempfile
from pathlib import Path

import anyio

from sda import bootstrap, memory, state
from sda.tools import MemoryTools


def _siembra(raiz: Path) -> None:
    """La siembra crea los cuatro archivos, es idempotente y no pisa contenido."""
    creados = memory.seed(raiz)
    assert sorted(creados) == [
        "decisions.md",
        "lessons.md",
        "progress.md",
        "tasks.md",
    ], creados

    marca = memory.dir_memoria(raiz) / memory.TASKS_FILE
    marca.write_text(marca.read_text(encoding="utf-8") + "\nEDITADO A MANO\n", encoding="utf-8")

    assert memory.seed(raiz) == [], "la segunda siembra no debería crear nada"
    assert "EDITADO A MANO" in marca.read_text(encoding="utf-8"), "la siembra pisó contenido"
    print("OK — siembra idempotente y respetuosa con lo editado a mano")


def _reparacion_de_proyecto_viejo() -> None:
    """Un proyecto anterior a T-029 (con ``_persistence/`` vacía) se repara al arrancar."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        # Simula el estado previo: ya inicializado, pero con la carpeta vacía.
        (raiz / memory.PERSISTENCE_DIR).mkdir()
        state.save(raiz, state.HarnessState(current_phase=state.PHASE_READY_FOR_WORK))

        assert bootstrap.bootstrap(raiz) is False, "debería reportarse como reanudación"
        for archivo in (memory.PROGRESS_FILE, memory.TASKS_FILE, memory.DECISIONS_FILE):
            assert (raiz / memory.PERSISTENCE_DIR / archivo).is_file(), archivo
    print("OK — un proyecto anterior a T-029 recupera su memoria sin perder el estado")


def _escritores(raiz: Path) -> None:
    """Numeración correlativa, formato garantizado y tabla sincronizada con el detalle."""
    assert memory.add_task(raiz, "Definir el modelo de datos") == "T-001"
    assert memory.add_task(raiz, "Elegir framework de frontend", "Con SSR.") == "T-002"
    assert memory.add_task(raiz, "Montar CI") == "T-003"

    assert memory.add_decision(raiz, "Base de datos", "PostgreSQL.", "Ya lo conocen.") == "D-001"
    assert memory.add_decision(raiz, "Sin auth en v1", "Se pospone.") == "D-002"
    assert memory.add_lesson(raiz, "Preferencia del humano", "Decide el stack antes.") == "L-001"
    memory.append_progress(raiz, "Onboarding completado", "El extracto quedó APPROVED.")

    memory.update_task(raiz, "T-001", "Completada", "Cerrada en la sesión de hoy.")
    memory.update_task(raiz, "t-003", "en curso")  # código y estado laxos: se normalizan

    tareas = (memory.dir_memoria(raiz) / memory.TASKS_FILE).read_text(encoding="utf-8")
    assert "| T-001 | Definir el modelo de datos | Completada |" in tareas, tareas
    assert "| T-003 | Montar CI | En curso |" in tareas, tareas
    assert "**Estado:** Completada" in tareas
    assert "Cerrada en la sesión de hoy." in tareas
    assert tareas.count("| T-001 |") == 1, "la fila del índice se duplicó"
    print("OK — numeración correlativa y tabla-índice sincronizada con el detalle")


def _rechazos(raiz: Path) -> None:
    """Lo inválido se rechaza en Python, no queda a criterio del modelo."""
    for llamada, motivo in (
        (lambda: memory.update_task(raiz, "T-999", "Completada"), "tarea inexistente"),
        (lambda: memory.update_task(raiz, "T-002", "Terminadísima"), "estado inválido"),
        (lambda: memory.add_task(raiz, "   "), "título vacío"),
        (lambda: memory.add_decision(raiz, "Título", "  "), "decisión sin contenido"),
    ):
        try:
            llamada()
        except memory.MemoriaError:
            continue
        raise AssertionError(f"no se rechazó: {motivo}")
    print("OK — entradas inválidas rechazadas (tarea inexistente, estado, campos vacíos)")


def _digest(raiz: Path) -> None:
    """El digest muestra lo abierto, oculta lo cerrado y respeta su tope."""
    digest = memory.build_digest(raiz)

    assert "T-002" in digest and "T-003" in digest, "faltan tareas abiertas"
    assert "T-001" not in digest, "una tarea Completada no debería ocupar el digest"
    assert "D-002" in digest and "L-001" in digest, "faltan decisiones/lecciones"
    assert "Onboarding completado" in digest, "falta el progreso"
    assert "2 abiertas de 3 registradas" in digest, digest

    # El tope es la garantía de que el costo del arranque no crece con el proyecto.
    for i in range(60):
        memory.add_decision(raiz, f"Decisión de relleno {i}", "x" * 300)
    recortado = memory.build_digest(raiz, max_chars=600)
    assert len(recortado) <= 700, len(recortado)
    assert "recortado" in recortado.lower(), recortado
    print("OK — digest acotado: muestra lo abierto, oculta lo cerrado y respeta el tope")


def _proyecto_sin_memoria() -> None:
    """Sin memoria con contenido, el digest es vacío (no arrastra secciones huecas)."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        assert memory.build_digest(raiz) == "", "sin carpeta debería ser vacío"
        memory.seed(raiz)
        assert memory.build_digest(raiz) == "", "recién sembrado debería ser vacío"
    print("OK — un proyecto nuevo no arrastra un digest vacío al mensaje de apertura")


async def _herramientas(raiz: Path) -> None:
    """Los handlers que ve el líder devuelven texto accionable, también al rechazar."""
    tools = MemoryTools(raiz)
    por_nombre = {t.name: t for t in tools.as_in_process_tools()}
    assert set(por_nombre) == {
        "record_progress",
        "record_task",
        "update_task",
        "record_decision",
        "record_lesson",
    }, sorted(por_nombre)

    creada = await por_nombre["record_task"].handler({"title": "Tarea vía herramienta", "detail": ""})
    assert creada.startswith("REGISTRADA:") and "T-0" in creada, creada

    rechazo = await por_nombre["update_task"].handler(
        {"code": "T-404", "status": "Completada", "note": ""}
    )
    assert rechazo.startswith("RECHAZADO:"), rechazo
    print("OK — las herramientas del líder devuelven confirmación y rechazo legibles")


async def main() -> None:
    _reparacion_de_proyecto_viejo()
    _proyecto_sin_memoria()
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        _siembra(raiz)
        _escritores(raiz)
        _rechazos(raiz)
        # El digest se comprueba antes de que las herramientas añadan más entradas.
        _digest(raiz)
        await _herramientas(raiz)
    print("\nTodo en verde.")


if __name__ == "__main__":
    anyio.run(main)
