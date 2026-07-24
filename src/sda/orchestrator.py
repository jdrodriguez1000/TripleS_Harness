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

from sda import bootstrap, state
from sda.core.provider import Provider
from sda.repl import forzar_utf8, prompt_line
from sda.resources import load_prompt
from sda.tools import LeaderTools

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


def _mensaje_apertura(st: state.HarnessState, recien_creado: bool) -> str:
    """Primer turno que se le da al líder para que salude según el estado.

    No lo ve el humano: es la instrucción interna que orienta al líder sobre en qué
    punto del flujo arranca (proyecto nuevo, borrador esperando revisión, o ya
    aprobado), para que su saludo sea coherente al reanudar.
    """
    fase = st.current_phase
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


class Orchestrator:
    """Conduce el doble bucle sobre una carpeta de proyecto, liderado por el agente."""

    def __init__(self, provider: Provider, project_dir: Path) -> None:
        self._provider = provider
        self._project_dir = project_dir
        self._tools = LeaderTools(provider, project_dir)

    async def run(self) -> int:
        """Ejecuta el bucle externo hasta que el humano salga. Devuelve el exit code."""
        forzar_utf8()
        recien_creado = bootstrap.bootstrap(self._project_dir)
        st = state.load(self._project_dir)

        leader = self._provider.create_session(
            system_prompt=load_prompt(_LEADER_PROMPT_FILE),
            cwd=str(self._project_dir),
            builtin_tools=_LEADER_TOOLS,
            model=_LEADER_MODEL,
            effort=_LEADER_EFFORT,
            in_process_tools=self._tools.as_in_process_tools(),
        )

        print("[sda] orquestador (líder-agente) — escribe 'salir' para terminar\n")

        try:
            # El líder abre saludando, orientado por el estado actual del proyecto.
            apertura = await leader.send(_mensaje_apertura(st, recien_creado))
            print(f"[líder] {apertura.text}\n")

            while True:
                try:
                    linea = (await prompt_line("[User] > ")).strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not linea:
                    continue
                if linea.lower() in _COMANDOS_SALIDA:
                    break

                resultado = await leader.send(linea)
                print(f"\n[líder] {resultado.text}\n")
        finally:
            await self._tools.cerrar()
            await leader.close()
        return 0


async def run_orchestrator(provider: Provider, project_dir: Path) -> int:
    """Punto de entrada del orquestador para el CLI."""
    return await Orchestrator(provider, project_dir).run()
