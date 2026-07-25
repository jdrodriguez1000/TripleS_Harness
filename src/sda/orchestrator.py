"""Orquestador del doble bucle REPL (el corazón del harness).

Desde T-028, el bucle externo lo lidera un **agente LLM** (el `orchestrator-leader`,
Opus + effort high, D-025/D-026), no un `if/elif` de fases en Python. Este módulo:

1. Hace el arranque determinista (``bootstrap``) antes de que exista el LLM.
2. Construye la sesión del líder con su system prompt y sus **herramientas
   en-proceso** (``sda.tools.LeaderTools``).
3. Expone el bucle de conversación humano↔líder por la terminal.

El líder decide *cuándo* avanzar de fase, lanzar el bucle interno o promover el
borrador; los **efectos peligrosos** (estado, lock, gate) son efectos laterales
deterministas de sus herramientas (principio "el LLM decide / las herramientas hacen
cumplir", D-026). La observabilidad turno-a-turno del bucle interno (D-021) se
conserva dentro de ``run_inner_loop``, que conduce la ``Session`` interna con nuestro
propio código (D-027).
"""

from __future__ import annotations

from pathlib import Path

from sda import bootstrap, memory, state
from sda.core.provider import Provider
from sda.repl import terminal_ui
from sda.resources import load_prompt
from sda.tools import LeaderTools, MemoryTools

_COMANDOS_SALIDA = frozenset({"salir", "exit", "quit"})

# Modelo y esfuerzo del líder, fijados explícitamente (D-025/D-026): es el único
# componente Opus persistente y el más caro por turno, así que se declara aquí.
_LEADER_MODEL = "opus"
_LEADER_EFFORT = "high"
_LEADER_PROMPT_FILE = "orchestrator_leader.md"

# Sandbox DURO del líder: solo lectura. Puede fundamentar sus respuestas leyendo el
# scope y el borrador, pero NO puede escribir `_harness_state.json` ni forzar
# `APPROVED` con un Write genérico. Todo efecto sobre el harness pasa, obligatoriamente,
# por sus herramientas en-proceso (principio "manos atadas", D-026). Cierra el hueco
# detectado en la prueba en vivo de T-028: `allowed_tools` no restringía el toolset.
_LEADER_TOOLS = ["Read", "Glob", "Grep"]

# Lo que se ve en la barra inferior mientras el turno del líder está en vuelo. Sin
# etiqueta de agente: el líder es el interlocutor del humano, no un subordinado.
_PENSANDO = "Pensando…"


def _recuperar_transaccion(project_dir: Path, st: state.HarnessState) -> bool:
    """Detecta y salda una transacción interrumpida. Devuelve si la hubo (T-034).

    ``transaction_lock`` se ponía al lanzar el bucle interno y se liberaba al
    terminarlo, pero **nadie lo leía nunca**: un apagón a mitad del bucle interno
    dejaba el lock puesto y la fase en ``ONBOARDING``, y al reanudar el líder trataba
    el proyecto como recién nacido (le pedía al humano un ``scope.md`` que ya había
    escrito). Este es el lector que faltaba, tal como lo describe ``idea.md``.

    Salda el lock aquí mismo, en el arranque: el proceso que lo puso ya no existe, así
    que dejarlo puesto solo haría que cada reinicio posterior repitiera el aviso. La
    fase NO se toca: sigue siendo la información honesta de hasta dónde se llegó.
    """
    if not st.transaction_lock:
        return False
    st.transaction_lock = False
    st.active_repl = state.REPL_EXTERNAL
    st.active_subagent = None
    state.save(project_dir, st)
    return True


def _instruccion_apertura(
    st: state.HarnessState, recien_creado: bool, interrumpido: bool
) -> str:
    """Instrucción de arranque según el punto del flujo en que se reanuda."""
    fase = st.current_phase
    if interrumpido:
        # Va ANTES que el resto: el lock puesto es información más específica que la
        # fase, que se quedó congelada en el punto donde murió el proceso anterior.
        return (
            "La sesión anterior se cortó de forma abrupta mientras el subagente "
            "onboarding-reader estaba trabajando: quedó una transacción sin cerrar. "
            "Lo que haya en _prototype/document-extract.md puede estar a medias y no "
            "es confiable. El humano YA escribió su _context/scope.md, así que no se "
            "lo pidas de nuevo. Saluda, explícale con franqueza que la sesión previa "
            "se interrumpió y ofrécele relanzar el trabajo del subagente para "
            "rehacer el borrador. No llames a ninguna herramienta hasta que responda."
        )
    if recien_creado or fase in (state.PHASE_BOOTSTRAPPING, state.PHASE_ONBOARDING):
        return (
            "El humano acaba de iniciar el harness en un proyecto nuevo. Estás en el "
            "arranque del flujo de onboarding. Salúdalo y pídele que edite "
            "_context/scope.md con las ideas de su proyecto y te avise cuando termine."
        )
    if fase == state.PHASE_HUMAN_REVIEW:
        return (
            "Se reanuda la sesión. Ya hay un borrador en "
            "_prototype/document-extract.md esperando la decisión del humano. "
            "Salúdalo, recuérdale que lo revise en su editor y dile que te avise si "
            "lo aprueba o qué quiere corregir. No llames a ninguna herramienta hasta "
            "que el humano responda."
        )
    if fase == state.PHASE_READY_FOR_WORK:
        return (
            "Se reanuda la sesión. El onboarding ya fue aprobado y el proyecto está "
            "listo para trabajar. Saluda al humano e infórmaselo brevemente."
        )
    return (
        "Se reanuda la sesión del harness. Saluda al humano y ponte a su disposición "
        f"para continuar (fase actual: {fase})."
    )


def _mensaje_apertura(
    project_dir: Path,
    st: state.HarnessState,
    recien_creado: bool,
    interrumpido: bool,
) -> str:
    """Primer turno que se le da al líder para que salude según el estado.

    No lo ve el humano: es la instrucción interna que orienta al líder sobre en qué
    punto del flujo arranca (proyecto nuevo, borrador esperando revisión, o ya
    aprobado), para que su saludo sea coherente al reanudar.

    Desde T-029 lleva además el **digest de la memoria del proyecto**: un resumen
    acotado de ``_persistence/`` construido en Python. Se *empuja* en vez de dejar
    que el líder lo lea bajo demanda por dos razones: así arranca informado **siempre**
    (no depende de que el modelo decida leer) y el costo del arranque queda con techo
    fijo, en vez de crecer con la antigüedad del proyecto. El detalle completo le
    sigue quedando a un ``Read`` de distancia.

    El digest va primero y la instrucción al final, que es la parte accionable.
    """
    instruccion = _instruccion_apertura(st, recien_creado, interrumpido)
    digest = memory.build_digest(project_dir)
    return f"{digest}\n\n{instruccion}" if digest else instruccion


class Orchestrator:
    """Conduce el doble bucle sobre una carpeta de proyecto, liderado por el agente."""

    def __init__(self, provider: Provider, project_dir: Path) -> None:
        self._provider = provider
        self._project_dir = project_dir
        self._tools = LeaderTools(provider, project_dir)
        self._memory = MemoryTools(project_dir)

    async def run(self) -> int:
        """Ejecuta el bucle externo hasta que el humano salga. Devuelve el exit code."""
        recien_creado = bootstrap.bootstrap(self._project_dir)
        st = state.load(self._project_dir)
        interrumpido = _recuperar_transaccion(self._project_dir, st)

        leader = self._provider.create_session(
            system_prompt=load_prompt(_LEADER_PROMPT_FILE),
            cwd=str(self._project_dir),
            builtin_tools=_LEADER_TOOLS,
            model=_LEADER_MODEL,
            effort=_LEADER_EFFORT,
            in_process_tools=(
                self._tools.as_in_process_tools()
                + self._memory.as_in_process_tools()
            ),
        )

        def _mostrar(texto: str) -> None:
            """Imprime cada bloque de texto del líder según se va generando.

            Un turno puede traer varios bloques (narración antes de invocar una
            herramienta, resumen después): cada uno se muestra en el momento en que
            el modelo lo produce, no todos juntos al final del turno. El salto de
            línea va SIEMPRE antes del bloque (nunca después), para que cada
            elemento —entrada del humano, narración, estado del subagente, prompt—
            quede separado por exactamente una línea en blanco, sin duplicados.

            ``print`` está intervenido por ``terminal_ui``: el texto se inserta encima
            del área de entrada, sin pisar lo que el humano esté tecleando (T-030).
            """
            print(f"\n{texto}")

        try:
            # El prompt lleva un salto de línea delante para que quede separado del
            # bloque anterior por exactamente una línea en blanco, igual que el resto
            # de elementos de la conversación (ver ``_mostrar``).
            async with terminal_ui("\n> ") as ui:
                # Desde aquí las herramientas pueden avisar de su trabajo en curso;
                # antes de existir la terminal no había dónde dibujarlo.
                self._tools.usar_indicador(ui.trabajando)

                # El líder abre saludando, orientado por el estado actual del proyecto.
                # Es el único interlocutor del humano, así que su texto no lleva etiqueta.
                with ui.trabajando(_PENSANDO):
                    await leader.send(
                        _mensaje_apertura(
                            self._project_dir, st, recien_creado, interrumpido
                        ),
                        on_text=_mostrar,
                    )

                while True:
                    linea = await ui.leer()
                    if linea is None:
                        # Ctrl+C / Ctrl+D: fin de la entrada, se cierra la sesión.
                        break
                    linea = linea.strip()
                    if not linea:
                        continue
                    if linea.lower() in _COMANDOS_SALIDA:
                        break

                    # Envuelve el turno entero, no solo el silencio inicial: el líder
                    # sigue vivo mientras invoca herramientas y entre bloque y bloque
                    # de texto. Si una herramienta anuncia lo suyo, tapa a esta y al
                    # terminar vuelve a verse, que es justo lo que está pasando.
                    with ui.trabajando(_PENSANDO):
                        await leader.send(linea, on_text=_mostrar)
        finally:
            await self._tools.cerrar()
            await leader.close()
        return 0


async def run_orchestrator(provider: Provider, project_dir: Path) -> int:
    """Punto de entrada del orquestador para el CLI."""
    return await Orchestrator(provider, project_dir).run()
