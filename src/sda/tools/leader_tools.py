"""Herramientas en-proceso del ``orchestrator-leader`` (T-028).

Aquí vive el código que antes conducía el bucle externo con ``if/elif`` de fases
(``Orchestrator._conducir_onboarding``, ``_aprobar`` y sus helpers). Ahora es el
**cuerpo determinista** de las herramientas que el líder-agente invoca:

- ``scope_esta_lleno`` — solo lee; le dice al líder si el humano ya llenó el scope.
- ``run_inner_loop`` — pone el lock, conduce y **observa** la ``Session`` interna
  del onboarding-reader (D-021), corre la evaluación y deja el borrador en
  ``PENDING_REVIEW`` / ``phase=HUMAN_REVIEW``.
- ``promote_to_approved`` — la **puerta**: solo válida en ``phase=HUMAN_REVIEW``;
  promueve el documento a ``APPROVED`` de forma atómica y deja ``READY_FOR_WORK``.

El principio (D-026): el LLM decide *cuándo* llamarlas; ellas hacen cumplir los
invariantes (lock, atomicidad, gate) pase lo que pase con el LLM.
"""

from __future__ import annotations

import re
from pathlib import Path

from sda import bootstrap, state
from sda.core.provider import Provider
from sda.core.session import Session
from sda.core.tool import InProcessTool
from sda.evaluator import evaluate_draft
from sda.repl import subagent_line
from sda.resources import load_prompt

# Sandbox DURO del onboarding-reader (vía ``builtin_tools`` → ``tools`` del SDK):
# solo lectura del proyecto y escritura de su único entregable. A diferencia de
# ``allowed_tools`` (que solo auto-aprueba), esto sí le impide usar Bash/Edit/etc.
_ONBOARDING_TOOLS = ["Read", "Glob", "Grep", "Write"]
_ONBOARDING_PROMPT_FILE = "onboarding_reader.md"

# Modelo y esfuerzo fijados explícitamente para el onboarding-reader (T-026, D-025).
_ONBOARDING_MODEL = "sonnet"
_ONBOARDING_EFFORT = "high"

# Instrucción de arranque del bucle interno (primer turno de la sesión interna).
_INSTRUCCION_INICIAL = (
    "Ejecuta tu tarea ahora. Lee _context/scope.md, la plantilla "
    "_templates/document-extract-temp.md y cualquier otro documento del "
    "proyecto, y escribe _prototype/document-extract.md instanciando la "
    "plantilla. Al terminar, responde con tu resumen ejecutivo."
)


def _scope_esta_lleno(project_dir: Path) -> bool:
    """Indica si el humano ya escribió contenido real en ``_context/scope.md``.

    Heurística: se quitan los comentarios HTML y los encabezados markdown; si
    queda texto no vacío, se considera lleno. Así distinguimos el stub (solo
    comentarios y título) de un scope de verdad.
    """
    ruta = project_dir / bootstrap.SCOPE_FILE
    if not ruta.is_file():
        return False
    texto = ruta.read_text(encoding="utf-8")
    sin_comentarios = re.sub(r"<!--.*?-->", "", texto, flags=re.DOTALL)
    lineas_utiles = [
        ln.strip()
        for ln in sin_comentarios.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    return bool(lineas_utiles)


def _set_frontmatter(project_dir: Path, campo: str, valor: str) -> None:
    """Reemplaza ``campo: ...`` en el front-matter de ``document-extract.md``.

    Solo toca la primera aparición (el front-matter) y preserva el resto del
    archivo. Si el archivo o el campo no existen, no hace nada.
    """
    ruta = project_dir / bootstrap.EXTRACT_FILE
    if not ruta.is_file():
        return
    texto = ruta.read_text(encoding="utf-8")
    nuevo = re.sub(
        rf"(?m)^({re.escape(campo)}:)[^\n]*",
        rf"\1 {valor}",
        texto,
        count=1,
    )
    ruta.write_text(nuevo, encoding="utf-8")


def _sincronizar_persistencia(project_dir: Path) -> None:
    """Marca en ``_persistence/progress.md`` que el onboarding se completó.

    Sincronización mínima de esta rebanada (Step 10 de ``idea.md``): deja
    constancia del hito. La gestión rica de tasks/progress llega después.
    """
    progreso = project_dir / bootstrap.PERSISTENCE_DIR / "progress.md"
    progreso.parent.mkdir(parents=True, exist_ok=True)
    linea = "- Onboarding completado: _prototype/document-extract.md APROBADO por el humano.\n"
    with progreso.open("a", encoding="utf-8") as fh:
        fh.write(linea)


class LeaderTools:
    """Conjunto de herramientas en-proceso que el líder puede invocar.

    Mantiene el estado que no puede vivir en el LLM: la ``Session`` interna del
    onboarding-reader, viva entre llamadas para conservar el contexto durante el
    ciclo de rechazo/corrección (Forma A, D-021). Un solo objeto por ejecución del
    orquestador; sus métodos se exponen como ``InProcessTool`` al proveedor.
    """

    def __init__(self, provider: Provider, project_dir: Path) -> None:
        self._provider = provider
        self._project_dir = project_dir
        self._inner: Session | None = None

    # --- Registro de herramientas -------------------------------------------

    def as_in_process_tools(self) -> list[InProcessTool]:
        """Devuelve las herramientas del líder listas para registrar en la sesión."""
        return [
            InProcessTool(
                name="scope_esta_lleno",
                description=(
                    "Comprueba de forma determinista si el humano ya escribió "
                    "contenido real en _context/scope.md (no solo el stub). Llámala "
                    "ANTES de lanzar el bucle interno para no trabajar en vano."
                ),
                handler=self._tool_scope_esta_lleno,
            ),
            InProcessTool(
                name="run_inner_loop",
                description=(
                    "Lanza y conduce el bucle interno (el onboarding-reader) para "
                    "producir o corregir _prototype/document-extract.md. Pásale una "
                    "'instruction' breve: en la primera vez basta un aviso de "
                    "arranque; en un rechazo, el feedback exacto del humano. Devuelve "
                    "el resumen ejecutivo del onboarding-reader y deja el borrador "
                    "listo para revisión humana."
                ),
                handler=self._tool_run_inner_loop,
                parameters={"instruction": str},
            ),
            InProcessTool(
                name="promote_to_approved",
                description=(
                    "Promueve el borrador a APPROVED. Es la PUERTA de aprobación: "
                    "solo llámala cuando el humano haya aprobado explícitamente en "
                    "este turno. Rechazará ejecutarse si no estamos en revisión "
                    "humana. Deja el proyecto listo para trabajar."
                ),
                handler=self._tool_promote_to_approved,
            ),
        ]

    # --- Bucle interno (onboarding-reader) -----------------------------------

    async def _abrir_onboarding(self) -> None:
        """Abre la sesión interna del onboarding-reader (si no está abierta)."""
        if self._inner is not None:
            return
        self._inner = self._provider.create_session(
            system_prompt=load_prompt(_ONBOARDING_PROMPT_FILE),
            cwd=str(self._project_dir),
            builtin_tools=_ONBOARDING_TOOLS,
            model=_ONBOARDING_MODEL,
            effort=_ONBOARDING_EFFORT,
        )

    async def cerrar(self) -> None:
        """Cierra la sesión interna si sigue abierta. Idempotente."""
        if self._inner is not None:
            await self._inner.close()
            self._inner = None

    # --- Implementación de las herramientas ----------------------------------

    async def _tool_scope_esta_lleno(self, args: dict) -> str:
        """Herramienta ``scope_esta_lleno``: solo lee, no muta nada."""
        if _scope_esta_lleno(self._project_dir):
            return (
                "LLENO: _context/scope.md tiene contenido real. Puedes continuar y "
                "lanzar el bucle interno."
            )
        return (
            "VACIO: _context/scope.md sigue con solo el stub. Pide al humano que "
            "escriba sus ideas y las guarde antes de continuar."
        )

    async def _tool_run_inner_loop(self, args: dict) -> str:
        """Herramienta ``run_inner_loop``: conduce y observa el bucle interno.

        Pone el ``transaction_lock`` antes de la operación larga y lo libera al
        terminar (base de la recuperación ante caída). Corre la evaluación (stub,
        T-011) y, al pasar, deja el borrador en ``PENDING_REVIEW`` y la fase en
        ``HUMAN_REVIEW``. Devuelve al líder el resumen ejecutivo del reader.
        """
        instruccion_humano = (args.get("instruction") or "").strip()
        primera_vez = self._inner is None
        await self._abrir_onboarding()

        if primera_vez:
            turno = _INSTRUCCION_INICIAL
        else:
            turno = (
                "El humano pide ajustes sobre el borrador actual: "
                f"{instruccion_humano}\n"
                "Ajusta SOLO lo señalado en _prototype/document-extract.md y "
                "responde con tu resumen ejecutivo actualizado."
            )
        return await self._conducir_onboarding(turno)

    async def _conducir_onboarding(self, instruccion: str) -> str:
        """Manda un turno al onboarding-reader y devuelve su resumen (texto)."""
        assert self._inner is not None
        st = state.load(self._project_dir)
        st.active_repl = state.REPL_INTERNAL
        st.active_subagent = "onboarding-reader"
        st.transaction_lock = True
        st.current_phase = state.PHASE_ONBOARDING
        state.save(self._project_dir, st)

        print(
            subagent_line(
                "onboarding-reader",
                f"Trabajando en la construcción de {bootstrap.EXTRACT_FILE}. "
                "Te aviso cuando termine…",
            )
        )
        resultado = await self._inner.send(instruccion)
        print(subagent_line("onboarding-reader", "Trabajo terminado."))

        # El entregable ya está en disco; se somete a la eval interna (stub por ahora).
        evaluacion = evaluate_draft(self._project_dir / bootstrap.EXTRACT_FILE)
        if not evaluacion.passed and evaluacion.feedback:
            # Cuando la eval real exista, aquí se re-conduce al subagente sin
            # molestar al humano. Con el stub actual esta rama no se toma.
            return await self._conducir_onboarding(
                f"La auditoría interna pide corregir: {evaluacion.feedback}"
            )

        # Borrador listo para el humano.
        _set_frontmatter(self._project_dir, "estado", "PENDING_REVIEW")
        st = state.load(self._project_dir)
        st.active_repl = state.REPL_EXTERNAL
        st.active_subagent = None
        st.transaction_lock = False
        st.pending_approval_file = "document-extract.md"
        st.current_phase = state.PHASE_HUMAN_REVIEW
        state.save(self._project_dir, st)
        return resultado.text

    async def _tool_promote_to_approved(self, args: dict) -> str:
        """Herramienta ``promote_to_approved``: la puerta de aprobación (D-028).

        Rechaza ejecutarse si la fase no es ``HUMAN_REVIEW``, de modo que el gate no
        se pueda saltar aunque el líder lo intente. La promoción a ``APPROVED`` es
        atómica y no existe otro camino a ese estado.
        """
        st = state.load(self._project_dir)
        if st.current_phase != state.PHASE_HUMAN_REVIEW:
            return (
                "RECHAZADO: no hay ningún borrador en revisión humana "
                f"(fase actual: {st.current_phase}). No se puede aprobar nada ahora."
            )

        _set_frontmatter(self._project_dir, "estado", "APPROVED")
        _set_frontmatter(self._project_dir, "confirmado_por_humano", "si")
        _sincronizar_persistencia(self._project_dir)
        await self.cerrar()

        st = state.load(self._project_dir)
        st.pending_approval_file = None
        st.current_phase = state.PHASE_READY_FOR_WORK
        st.active_repl = state.REPL_EXTERNAL
        st.active_subagent = None
        st.transaction_lock = False
        state.save(self._project_dir, st)

        return (
            f"APROBADO: {bootstrap.EXTRACT_FILE} quedó marcado como APPROVED y "
            "bloqueado; _persistence/progress.md sincronizado. El proyecto está "
            "listo para la jornada de trabajo."
        )
