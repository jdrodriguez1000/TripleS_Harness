"""Verificación headless de la recuperación tras un reinicio (T-033 y T-034).

Ejecutar con ``python spikes/t033_t034_recuperacion_reinicio.py``. No necesita
credenciales ni red: usa un ``Provider`` falso que registra literalmente el turno que
recibiría cada subagente, que es justo donde vivían los dos defectos.

Cubre:

- **T-033** — con el proceso recién arrancado (``self._inner is None``) pero un
  borrador esperando en disco (``phase=HUMAN_REVIEW``), ``run_inner_loop`` manda una
  **corrección** con el feedback del humano, no la instrucción de arranque que
  regeneraba el borrador desde cero en silencio.
- **T-034** — un ``transaction_lock`` puesto por una sesión que murió a mitad del bucle
  interno se **lee** al arrancar: el líder recibe un aviso de sesión interrumpida en
  vez del "proyecto nuevo, pide el scope", y el lock queda saldado en disco.

Lo que NO cubre: que el líder-agente reaccione bien a esos textos. Eso es juicio del
modelo y se valida a ojo con ``sda start``.
"""

import tempfile
from pathlib import Path

import anyio

from sda import bootstrap, state
from sda.core.provider import Provider
from sda.core.session import Session, TurnResult
from sda.core.tool import InProcessTool
from sda.orchestrator import _mensaje_apertura, _recuperar_transaccion
from sda.tools import LeaderTools


class SesionFalsa(Session):
    """Sesión que no habla con ningún modelo: solo apunta los turnos recibidos."""

    def __init__(self, turnos: list[str]) -> None:
        self._turnos = turnos

    async def send(self, prompt: str, *, on_text=None) -> TurnResult:
        self._turnos.append(prompt)
        return TurnResult(text="(resumen ejecutivo falso)")

    async def close(self) -> None:
        return None


class ProviderFalso(Provider):
    """Fábrica de ``SesionFalsa`` que acumula todos los turnos en una sola lista."""

    def __init__(self) -> None:
        self.turnos: list[str] = []

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
        return SesionFalsa(self.turnos)


def _proyecto(tmp: str) -> Path:
    """Carpeta de proyecto recién inicializada por el bootstrap real."""
    raiz = Path(tmp)
    bootstrap.bootstrap(raiz)
    return raiz


def _en_fase(raiz: Path, fase: str, *, lock: bool = False) -> None:
    """Deja el estado en disco tal como lo dejaría el flujo real en ese punto."""
    st = state.load(raiz)
    st.current_phase = fase
    st.transaction_lock = lock
    if fase == state.PHASE_HUMAN_REVIEW:
        st.pending_approval_file = "document-extract.md"
    state.save(raiz, st)


# --- T-033 -------------------------------------------------------------------

_FEEDBACK = "Corrige la sección de usuarios: los externos NO llevan login."


async def _correccion_tras_reinicio() -> None:
    """El caso del defecto: proceso nuevo, borrador viejo en disco."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = _proyecto(tmp)
        _en_fase(raiz, state.PHASE_HUMAN_REVIEW)

        provider = ProviderFalso()
        tools = LeaderTools(
            provider, raiz
        )  # ``_inner`` nace en None, como al reiniciar
        respuesta = await tools._tool_run_inner_loop({"instruction": _FEEDBACK})
        await tools.cerrar()

        assert len(provider.turnos) == 1, provider.turnos
        turno = provider.turnos[0]
        assert _FEEDBACK in turno, f"se perdió la corrección del humano:\n{turno}"
        assert (
            "instanciando la plantilla" not in turno
        ), f"se mandó la instrucción de arranque en vez de la corrección:\n{turno}"
        assert (
            "no está en tu contexto" in turno.lower()
        ), f"no se le avisó al subagente que debe leer el borrador primero:\n{turno}"
        assert respuesta == "(resumen ejecutivo falso)", respuesta
        # La puerta humana vuelve a quedar armada tras la corrección.
        assert state.load(raiz).current_phase == state.PHASE_HUMAN_REVIEW
    print("OK — T-033: tras un reinicio, la corrección del humano llega al subagente")


async def _arranque_de_verdad() -> None:
    """Sin borrador en disco sigue siendo un arranque, no una corrección."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = _proyecto(tmp)
        _en_fase(raiz, state.PHASE_ONBOARDING)

        provider = ProviderFalso()
        tools = LeaderTools(provider, raiz)
        await tools._tool_run_inner_loop({"instruction": "Arranca cuando quieras."})
        await tools.cerrar()

        assert "instanciando la plantilla" in provider.turnos[0], provider.turnos
    print("OK — T-033: un arranque real sigue recibiendo la instrucción de arranque")


async def _correccion_en_caliente() -> None:
    """Con la sesión interna viva, la corrección no arrastra el preámbulo de relectura."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = _proyecto(tmp)
        _en_fase(raiz, state.PHASE_ONBOARDING)

        provider = ProviderFalso()
        tools = LeaderTools(provider, raiz)
        await tools._tool_run_inner_loop({"instruction": ""})  # arranque
        await tools._tool_run_inner_loop({"instruction": _FEEDBACK})  # rechazo
        await tools.cerrar()

        segundo = provider.turnos[1]
        assert _FEEDBACK in segundo, segundo
        assert (
            "no está en tu contexto" not in segundo.lower()
        ), f"el borrador SÍ está en su contexto; sobra el preámbulo:\n{segundo}"
    print("OK — T-033: la corrección en caliente conserva su turno breve de siempre")


async def _correccion_sin_feedback() -> None:
    """Una corrección sin feedback se rechaza en Python, sin molestar al subagente."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = _proyecto(tmp)
        _en_fase(raiz, state.PHASE_HUMAN_REVIEW)

        provider = ProviderFalso()
        tools = LeaderTools(provider, raiz)
        respuesta = await tools._tool_run_inner_loop({"instruction": "   "})
        await tools.cerrar()

        assert respuesta.startswith("RECHAZADO:"), respuesta
        assert provider.turnos == [], "no debió lanzarse el bucle interno"
    print("OK — T-033: sin feedback, la corrección se rechaza y no se regenera nada")


# --- T-034 -------------------------------------------------------------------


def _sesion_interrumpida() -> None:
    """Un lock huérfano se detecta, se salda y cambia el mensaje de apertura."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = _proyecto(tmp)
        # Estado exacto que deja un apagón a mitad del bucle interno.
        st = state.load(raiz)
        st.current_phase = state.PHASE_ONBOARDING
        st.active_repl = state.REPL_INTERNAL
        st.active_subagent = "onboarding-reader"
        st.transaction_lock = True
        state.save(raiz, st)

        st = state.load(raiz)
        assert _recuperar_transaccion(raiz, st) is True, "no se detectó la interrupción"

        mensaje = _mensaje_apertura(raiz, st, recien_creado=False, interrumpido=True)
        assert "interrumpi" in mensaje.lower() or "cortó" in mensaje, mensaje
        assert (
            "pídele que edite" not in mensaje
        ), f"sigue tratando el proyecto como nuevo:\n{mensaje}"

        # El lock queda saldado en disco: el siguiente arranque ya no reincide.
        en_disco = state.load(raiz)
        assert en_disco.transaction_lock is False, "el lock siguió puesto"
        assert en_disco.active_repl == state.REPL_EXTERNAL
        assert en_disco.active_subagent is None
        assert en_disco.current_phase == state.PHASE_ONBOARDING, "la fase no se toca"
        assert _recuperar_transaccion(raiz, en_disco) is False, "el aviso se repitió"
    print("OK — T-034: el lock huérfano se lee, avisa de la interrupción y se salda")


def _arranque_limpio_intacto() -> None:
    """Sin lock, la apertura es exactamente la de antes del arreglo."""
    with tempfile.TemporaryDirectory() as tmp:
        raiz = _proyecto(tmp)
        st = state.load(raiz)
        assert _recuperar_transaccion(raiz, st) is False

        nuevo = _mensaje_apertura(raiz, st, recien_creado=True, interrumpido=False)
        assert "proyecto nuevo" in nuevo, nuevo

        _en_fase(raiz, state.PHASE_HUMAN_REVIEW)
        st = state.load(raiz)
        revision = _mensaje_apertura(raiz, st, recien_creado=False, interrumpido=False)
        assert "esperando la decisión del humano" in revision, revision
    print("OK — T-034: los arranques sin interrupción conservan su mensaje de siempre")


async def main() -> None:
    await _correccion_tras_reinicio()
    await _arranque_de_verdad()
    await _correccion_en_caliente()
    await _correccion_sin_feedback()
    _sesion_interrumpida()
    _arranque_limpio_intacto()
    print("\nTodo en verde.")


if __name__ == "__main__":
    anyio.run(main)
