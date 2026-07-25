"""Verificación headless de la terminal de doble área (T-030).

Ejecutar con ``python spikes/t030_terminal_doble_area.py``. No necesita credenciales
ni una terminal real: usa la entrada simulada de prompt_toolkit para reproducir el
escenario del bug —el humano teclea MIENTRAS el agente emite streaming— y comprobar
que el harness encola sus turnos en vez de mezclarlos con la salida.

Lo que NO cubre: el aspecto visual en una terminal real (que la línea tecleada quede
fija al pie y la salida se inserte encima). Eso se valida a ojo con ``sda start``.
"""

import anyio
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from sda.repl import terminal_ui


async def _tecleo_durante_streaming() -> None:
    """El humano escribe dos turnos mientras el agente trabaja: no se pierde ninguno."""
    with create_pipe_input() as pipe, create_app_session(pipe, DummyOutput()):
        async with terminal_ui("\n> ") as ui:
            await anyio.sleep(0.2)  # deja arrancar el prompt de fondo

            # El humano teclea dos turnos mientras el agente emite su streaming.
            pipe.send_text("hola\r")
            await anyio.sleep(0.1)
            pipe.send_text("segundo turno\r")
            await anyio.sleep(0.3)
            print("\n[streaming del agente]")

            with anyio.fail_after(2):
                recibidas = [await ui.leer(), await ui.leer()]

    assert recibidas == ["hola", "segundo turno"], recibidas
    print("OK — nada se perdió y el orden se preservó:", recibidas)


async def _salida_por_eof() -> None:
    """Ctrl+D devuelve ``None`` y el bloque cierra sin dejar la tarea de fondo colgada."""
    with create_pipe_input() as pipe, create_app_session(pipe, DummyOutput()):
        async with terminal_ui("\n> ") as ui:
            await anyio.sleep(0.2)
            pipe.send_text("\x04")
            with anyio.fail_after(2):
                assert await ui.leer() is None
    print("OK — Ctrl+D devuelve None y el bloque cierra limpio")


async def main() -> None:
    await _tecleo_durante_streaming()
    await _salida_por_eof()


if __name__ == "__main__":
    anyio.run(main)
