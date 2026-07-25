"""Verificación headless del indicador de trabajo en curso (T-036).

Ejecutar con ``python spikes/t036_indicador_trabajo.py``. No abre ninguna terminal
real: comprueba la lógica que decide **qué** se dibuja y **cuándo**, que es lo único
determinista. Que el spinner se vea bien girando es cosa de mirar ``sda start``.

Cubre:

- La barra inferior solo existe mientras hay trabajo: ``bottom_toolbar`` pasa de
  ``None`` a callable al entrar y vuelve a ``None`` al salir. prompt_toolkit consulta
  ese atributo en cada repintado (``Condition(lambda: self.bottom_toolbar is not None)``
  en ``shortcuts/prompt.py``), así que ponerlo en ``None`` la hace desaparecer.
- Los trabajos se **anidan**: el subagente tapa al líder mientras dura, y al terminar
  reaparece el del líder en vez de quedar la barra en blanco.
- El spinner avanza con el reloj, no con el número de repintados.
- El indicador mudo (fuera de la terminal) no estorba a nadie.
"""

import time
from collections.abc import Iterator
from contextlib import contextmanager

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from sda.repl import _FOTOGRAMAS, TerminalUI, indicador_mudo


@contextmanager
def _ui() -> Iterator[TerminalUI]:
    """``TerminalUI`` sobre entrada/salida ficticias, sin consola de verdad.

    ``PromptSession`` busca una consola real al construirse y aquí no hay ninguna
    (en Windows falla con ``NoConsoleScreenBufferError``). ``create_app_session`` con
    una tubería y un ``DummyOutput`` es la vía que prompt_toolkit ofrece para esto:
    la lógica es la misma, solo que nadie dibuja al otro lado.
    """
    with create_pipe_input() as entrada:
        with create_app_session(input=entrada, output=DummyOutput()):
            yield TerminalUI("> ")


def _barra_apagada(ui: TerminalUI) -> bool:
    """La barra está apagada cuando prompt_toolkit no encuentra qué dibujar."""
    return ui._session.bottom_toolbar is None


def _encendido_y_apagado() -> None:
    with _ui() as ui:
        assert _barra_apagada(ui), "no debería haber barra antes de trabajar"

        with ui.trabajando("Pensando…"):
            assert not _barra_apagada(ui), "la barra no se encendió"
            assert "Pensando…" in ui._texto_barra()

        assert _barra_apagada(ui), "la barra siguió puesta al terminar el trabajo"
    print("OK — T-036: la barra aparece al empezar y desaparece al terminar")


def _anidamiento() -> None:
    with _ui() as ui:
        with ui.trabajando("Pensando…"):
            with ui.trabajando("[onboarding-reader] Actualizando extract…"):
                texto = ui._texto_barra()
                assert "Actualizando" in texto, f"el interior no tapó: {texto}"
                assert "Pensando" not in texto, texto
            # Al cerrarse el interior reaparece el exterior, que sigue vivo.
            assert "Pensando…" in ui._texto_barra(), ui._texto_barra()
            assert not _barra_apagada(ui), "el interior apagó la barra del exterior"

        assert _barra_apagada(ui)
    print("OK — T-036: el trabajo del subagente tapa al del líder y luego lo devuelve")


def _spinner_gira() -> None:
    """El fotograma se calcula por tiempo: dos instantes distintos, fotogramas distintos."""
    with _ui() as ui:
        with ui.trabajando("Pensando…"):
            vistos = set()
            # Muestrea a lo largo de varios periodos completos del ciclo.
            for _ in range(len(_FOTOGRAMAS) * 2):
                vistos.add(ui._texto_barra().strip()[0])
                time.sleep(0.06)
            assert len(vistos) > 1, f"el spinner no se movió: siempre {vistos}"
    print(f"OK — T-036: el spinner gira solo ({len(vistos)} fotogramas distintos)")


def _mudo_no_estorba() -> None:
    """Sin terminal (spikes, tests) el indicador se usa igual y no hace nada."""
    with indicador_mudo("lo que sea"):
        pass
    print("OK — T-036: el indicador mudo funciona fuera de la terminal")


def main() -> None:
    _encendido_y_apagado()
    _anidamiento()
    _spinner_gira()
    _mudo_no_estorba()
    print("\nTodo en verde.")


if __name__ == "__main__":
    main()
