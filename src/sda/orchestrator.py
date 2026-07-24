"""Orquestador del doble bucle REPL (el corazón del harness).

Implementa, sobre una carpeta de proyecto, el flujo de ``idea.md`` para esta
primera rebanada:

    Fase 1  Bootstrapping  -> crea la estructura y espera que el humano llene el scope.
    Fase 2  REPL interno   -> el onboarding-reader produce _prototype/document-extract.md.
    Fase 3  Puerta humana  -> el humano aprueba o rechaza (con feedback).
    Fase 4  Cierre         -> al aprobar, promueve el documento y sincroniza _persistence.

Sigue la **Forma A**: es *nuestro código* quien conduce dos ``Session`` separadas
—la externa (este bucle, cara al humano) y la interna (el onboarding-reader)— para
poder observar y, más adelante, evaluar el bucle interno. El bucle de rechazo
reutiliza la misma sesión interna viva, que conserva el contexto entre correcciones.
"""

from __future__ import annotations

import re
from pathlib import Path

from sda import bootstrap, state
from sda.core.provider import Provider
from sda.core.session import Session
from sda.evaluator import evaluate_draft
from sda.repl import forzar_utf8, prompt_line
from sda.resources import load_prompt

_COMANDOS_SALIDA = frozenset({"salir", "exit", "quit"})
_COMANDOS_CONTINUAR = frozenset({"listo", "continuar"})

# Herramientas que puede usar el onboarding-reader: solo lectura del proyecto y
# escritura de su único entregable (sandbox deliberadamente acotado).
_ONBOARDING_TOOLS = ["Read", "Glob", "Grep", "Write"]
_ONBOARDING_PROMPT_FILE = "onboarding_reader.md"

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


class Orchestrator:
    """Conduce el doble bucle sobre una carpeta de proyecto."""

    def __init__(self, provider: Provider, project_dir: Path) -> None:
        self._provider = provider
        self._project_dir = project_dir
        # Sesión interna (onboarding-reader). Se mantiene viva durante la revisión
        # humana para poder re-conducirla con feedback si el humano rechaza.
        self._inner: Session | None = None

    # --- Bucle interno (onboarding-reader) -----------------------------------

    async def _abrir_onboarding(self) -> None:
        """Abre la sesión interna del onboarding-reader (si no está abierta)."""
        if self._inner is not None:
            return
        self._inner = self._provider.create_session(
            system_prompt=load_prompt(_ONBOARDING_PROMPT_FILE),
            cwd=str(self._project_dir),
            allowed_tools=_ONBOARDING_TOOLS,
        )

    async def _cerrar_onboarding(self) -> None:
        """Cierra la sesión interna si sigue abierta."""
        if self._inner is not None:
            await self._inner.close()
            self._inner = None

    async def _conducir_onboarding(self, instruccion: str) -> str:
        """Manda un turno al onboarding-reader y devuelve su resumen (texto)."""
        assert self._inner is not None
        st = state.load(self._project_dir)
        st.active_repl = state.REPL_INTERNAL
        st.active_subagent = "onboarding-reader"
        st.transaction_lock = True
        st.current_phase = state.PHASE_ONBOARDING
        state.save(self._project_dir, st)

        print("[sda] bucle interno: onboarding-reader trabajando…")
        resultado = await self._inner.send(instruccion)

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

    # --- Cierre del documento (aprobación) -----------------------------------

    async def _aprobar(self) -> None:
        """Promueve el documento a APPROVED y deja el harness listo para trabajar."""
        _set_frontmatter(self._project_dir, "estado", "APPROVED")
        _set_frontmatter(self._project_dir, "confirmado_por_humano", "si")
        _sincronizar_persistencia(self._project_dir)
        await self._cerrar_onboarding()

        st = state.load(self._project_dir)
        st.pending_approval_file = None
        st.current_phase = state.PHASE_READY_FOR_WORK
        st.active_repl = state.REPL_EXTERNAL
        st.transaction_lock = False
        state.save(self._project_dir, st)

    # --- Presentación --------------------------------------------------------

    def _pedir_scope(self) -> None:
        print(
            f"[sda] Proyecto nuevo inicializado.\n"
            f"      Edita {bootstrap.SCOPE_FILE} con las ideas de tu proyecto y,\n"
            f"      cuando termines, escribe 'listo' aquí para continuar."
        )

    def _presentar_borrador(self, resumen: str) -> None:
        print(
            f"\n[sda] Borrador listo para tu revisión: {bootstrap.EXTRACT_FILE}\n"
            f"----- resumen del onboarding-reader -----\n{resumen}\n"
            f"-----------------------------------------\n"
            f"      Revísalo en tu editor y responde:\n"
            f"        aprobar                 -> lo doy por bueno\n"
            f"        rechazar <observación>  -> pido correcciones"
        )

    # --- Bucle externo (orquestador) -----------------------------------------

    async def run(self) -> int:
        """Ejecuta el bucle externo hasta que el humano salga. Devuelve el exit code."""
        forzar_utf8()
        recien_creado = bootstrap.bootstrap(self._project_dir)
        st = state.load(self._project_dir)

        print("[sda] orquestador — escribe 'salir' para terminar")
        if recien_creado or st.current_phase == state.PHASE_BOOTSTRAPPING:
            self._pedir_scope()
        elif st.current_phase == state.PHASE_HUMAN_REVIEW:
            print(
                f"[sda] Hay un borrador esperando tu decisión: "
                f"{bootstrap.EXTRACT_FILE}. Responde 'aprobar' o "
                f"'rechazar <observación>'."
            )
        elif st.current_phase == state.PHASE_READY_FOR_WORK:
            print("[sda] Onboarding ya aprobado. Proyecto listo para trabajar.")

        try:
            while True:
                try:
                    linea = (await prompt_line("tú> ")).strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not linea:
                    continue
                if linea.lower() in _COMANDOS_SALIDA:
                    break

                if not await self._despachar(linea):
                    break
        finally:
            await self._cerrar_onboarding()
        return 0

    async def _despachar(self, linea: str) -> bool:
        """Procesa una línea según la fase actual. Devuelve ``False`` para salir."""
        st = state.load(self._project_dir)
        fase = st.current_phase

        if fase in (state.PHASE_BOOTSTRAPPING, state.PHASE_ONBOARDING):
            if linea.lower() in _COMANDOS_CONTINUAR:
                if not _scope_esta_lleno(self._project_dir):
                    print(
                        f"[sda] {bootstrap.SCOPE_FILE} sigue vacío. Escribe tus "
                        f"ideas y vuelve a intentarlo."
                    )
                    return True
                await self._abrir_onboarding()
                resumen = await self._conducir_onboarding(_INSTRUCCION_INICIAL)
                self._presentar_borrador(resumen)
            else:
                self._pedir_scope()
            return True

        if fase == state.PHASE_HUMAN_REVIEW:
            return await self._despachar_revision(linea)

        if fase == state.PHASE_READY_FOR_WORK:
            print("[sda] Onboarding aprobado. (Las fases siguientes aún no existen.)")
            return True

        print(f"[sda] Fase '{fase}' no manejada en esta versión.")
        return True

    async def _despachar_revision(self, linea: str) -> bool:
        """Maneja la puerta humana: aprobar / rechazar <feedback>."""
        palabras = linea.split(maxsplit=1)
        comando = palabras[0].lower()

        if comando in {"aprobar", "aprobado", "approve"}:
            await self._aprobar()
            print(
                f"[sda] Documento APROBADO. {bootstrap.EXTRACT_FILE} bloqueado.\n"
                f"      Proyecto listo para la jornada de trabajo."
            )
            return True

        if comando in {"rechazar", "rechazado", "reject"}:
            feedback = palabras[1] if len(palabras) > 1 else ""
            if not feedback:
                print("[sda] Indica qué corregir: 'rechazar <observación>'.")
                return True
            await self._abrir_onboarding()  # sigue viva; garantía por si acaso
            resumen = await self._conducir_onboarding(
                f"El humano rechazó el borrador con esta observación: {feedback}\n"
                f"Ajusta SOLO lo señalado en _prototype/document-extract.md y "
                f"responde con tu resumen ejecutivo actualizado."
            )
            self._presentar_borrador(resumen)
            return True

        print("[sda] Responde 'aprobar' o 'rechazar <observación>'.")
        return True


async def run_orchestrator(provider: Provider, project_dir: Path) -> int:
    """Punto de entrada del orquestador para el CLI."""
    return await Orchestrator(provider, project_dir).run()
