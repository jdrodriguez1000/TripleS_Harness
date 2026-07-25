"""Bucle interactivo de conversación (REPL) sobre una ``Session``.

Lee turnos del teclado, los manda a la sesión y muestra la respuesta, todo dentro
de una única sesión de larga vida para que el contexto se conserve entre turnos
(el mecanismo verificado en el spike T-016, ahora manejado por un humano).

Vive fuera de ``sda.core`` porque es un adaptador de entrada/salida, no dominio.
Recibe un ``Provider`` (no un proveedor concreto) para respetar la abstracción.
"""

from __future__ import annotations

import math
import sys
import time
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import AbstractContextManager, asynccontextmanager, contextmanager

import anyio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

from sda.core.provider import Provider

# Palabras que terminan la sesión (se comparan en minúsculas y sin espacios).
_COMANDOS_SALIDA = frozenset({"salir", "exit", "quit"})

# Un "indicador" es lo que devuelve :meth:`TerminalUI.trabajando`: se le pasa el texto
# a mostrar y se usa como ``with``. Existe como tipo para que quien reporte trabajo en
# curso (p. ej. ``LeaderTools``) dependa de esta firma y no de la terminal entera.
Indicador = Callable[[str], AbstractContextManager[None]]


@contextmanager
def indicador_mudo(texto: str) -> Iterator[None]:
    """Indicador que no muestra nada, para cuando no hay terminal (spikes, tests)."""
    yield


# Tenue (dim) en vez de un color fijo: se adapta al esquema de la terminal
# (claro/oscuro) en vez de imponer un gris que podría desentonar. Windows
# Terminal y PowerShell 7+ interpretan estos códigos de forma nativa.
_DIM = "\x1b[2m"
_RESET = "\x1b[0m"

# Fotogramas del spinner (braille): giran en el sitio sin cambiar de ancho, así que
# la línea no "salta" al repintarse.
_FOTOGRAMAS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

# Segundos entre repintados automáticos de la UI. ~10 fps: el giro se ve continuo y
# el coste es despreciable. También marca el ritmo del spinner, que se calcula por
# tiempo (no por número de repintados) para que gire parejo aunque se salte alguno.
_REFRESCO = 0.1

# El estilo por omisión de la barra inferior es ``reverse``: una franja invertida de
# ancho completo, demasiado ruidosa para un aviso de fondo. Se baja al mismo tono
# tenue que usa :func:`subagent_line`, para que ambos se lean como "trabajo de fondo".
_ESTILO = Style.from_dict(
    {
        "bottom-toolbar": "noreverse",
        "bottom-toolbar.text": "noreverse fg:ansibrightblack",
    }
)


def subagent_line(nombre: str, texto: str) -> str:
    """Formatea una línea de estado de un subagente, distinguible del líder.

    Indentada, marcada con ``⎿`` (el mismo símbolo que esta terminal usa para
    resultados subordinados de una herramienta) y en tono tenue, para que se lea
    como "trabajo de fondo" y no como si el humano estuviera hablando con otro
    interlocutor. Incluye el salto de línea que la separa del bloque anterior.
    """
    return f"\n  {_DIM}⎿ [{nombre}] {texto}{_RESET}"


def _forzar_utf8() -> None:
    """Reconfigura la consola a UTF-8 para no romper con acentos ni emojis.

    En Windows la consola suele usar cp1252, que no puede codificar caracteres
    que el modelo devuelve con frecuencia (emojis, comillas tipográficas). Sin
    esto, imprimir la respuesta lanzaría ``UnicodeEncodeError``. ``errors=replace``
    degrada con elegancia cualquier carácter que aun así no se pueda representar.
    """
    for flujo in (sys.stdout, sys.stdin):
        reconfigure = getattr(flujo, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


class TerminalUI:
    """Terminal con área de entrada fija abajo y área de salida encima (T-030).

    Con ``input()`` plano, el eco del teclado y los ``print()`` del streaming del
    agente comparten el mismo cursor: si el humano escribe mientras el modelo emite
    texto, ambos flujos se entrelazan visualmente (no se corrompe nada, pero se lee
    fatal). ``prompt_toolkit`` resuelve eso repintando: la línea que el humano teclea
    vive siempre al pie de la terminal y la salida se inserta *encima* de ella.

    Para que ese repintado exista también mientras el agente trabaja, el prompt se
    mantiene **siempre abierto** en una tarea de fondo que empuja cada línea a una
    cola. El bucle de conversación consume de la cola con :meth:`leer`, así que lo
    que el humano escriba durante un turno no se pierde ni se mezcla: queda encolado
    y se procesa cuando el turno en curso termina.

    El prompt es fijo y mudo a propósito: un texto que cambie según el estado (un
    "trabajando…") se queda escrito en el historial de la terminal cada vez que se
    repinta, y ensucia la transcripción de la conversación. Lo que sí cambia vive en
    la **barra inferior** (:meth:`trabajando`), que se repinta en el sitio y nunca
    entra al historial: mientras algo trabaja se ve una línea viva, y al terminar
    desaparece sin dejar rastro. En la transcripción solo queda el resultado.
    """

    def __init__(self, prompt: str) -> None:
        # ``bottom_toolbar=None`` arranca sin barra; ``trabajando`` la enciende y la
        # apaga asignando este mismo atributo, que prompt_toolkit consulta en cada
        # repintado. ``refresh_interval`` es lo que hace que la UI se repinte sola
        # aunque el humano no toque el teclado: sin él, el spinner no giraría.
        self._session: PromptSession[str] = PromptSession(
            prompt,
            bottom_toolbar=None,
            refresh_interval=_REFRESCO,
            style=_ESTILO,
        )
        # Pila, no un solo texto: los trabajos se anidan (el líder piensa *mientras*
        # el subagente trabaja). Se muestra el más reciente y, al cerrarse, reaparece
        # el que lo envolvía en vez de quedar la barra en blanco.
        self._trabajos: list[str] = []
        # Buffer infinito: encolar nunca debe bloquear al humano que escribe.
        self._envio, self._recepcion = anyio.create_memory_object_stream[str | None](
            max_buffer_size=math.inf
        )

    def _texto_barra(self) -> str:
        """Contenido de la barra inferior. prompt_toolkit la llama en cada repintado."""
        fotograma = _FOTOGRAMAS[int(time.monotonic() / _REFRESCO) % len(_FOTOGRAMAS)]
        return f"  {fotograma} {self._trabajos[-1]}"

    @contextmanager
    def trabajando(self, texto: str) -> Iterator[None]:
        """Muestra ``texto`` con un spinner mientras dure el bloque ``with``.

        Anidable: si ya había un trabajo en curso, este lo tapa y al salir se vuelve
        a ver el anterior. La barra solo se apaga cuando no queda ninguno.
        """
        self._trabajos.append(texto)
        self._session.bottom_toolbar = self._texto_barra
        try:
            yield
        finally:
            # Por valor: dos trabajos con el mismo texto son intercambiables, así que
            # basta con quitar uno cualquiera de ellos.
            self._trabajos.remove(texto)
            if not self._trabajos:
                self._session.bottom_toolbar = None

    async def leer(self) -> str | None:
        """Devuelve la siguiente línea del humano, o ``None`` si pidió terminar.

        ``None`` corresponde a Ctrl+C / Ctrl+D (fin de la entrada), no a una línea
        vacía: una línea vacía se devuelve tal cual y la decide quien llama.
        """
        return await self._recepcion.receive()

    async def _leer_en_bucle(self) -> None:
        """Mantiene el prompt abierto sin pausa y encola cada línea que el humano envía."""
        while True:
            try:
                linea = await self._session.prompt_async()
            except (EOFError, KeyboardInterrupt):
                await self._envio.send(None)
                return
            await self._envio.send(linea)


@asynccontextmanager
async def terminal_ui(prompt: str) -> AsyncIterator[TerminalUI]:
    """Abre la terminal de doble área y la cierra al salir del bloque.

    ``patch_stdout`` redirige ``print()`` (el nuestro y el de cualquier dependencia)
    para que se dibuje encima del área de entrada en vez de pisarla. ``raw=True``
    deja pasar las secuencias ANSI que ya usamos —el tono tenue de
    :func:`subagent_line`— en vez de escaparlas como texto literal.
    """
    _forzar_utf8()
    ui = TerminalUI(prompt)
    with patch_stdout(raw=True):
        async with anyio.create_task_group() as tg:
            tg.start_soon(ui._leer_en_bucle)
            try:
                yield ui
            finally:
                # El prompt de fondo no termina solo: se cancela al cerrar el bloque.
                tg.cancel_scope.cancel()


async def run_repl(provider: Provider) -> int:
    """Abre una sesión y conversa por teclado hasta que el humano termine.

    Devuelve el código de salida (``0`` en una terminación normal).
    """
    print("[sda] sesión interactiva — escribe 'salir' para terminar")

    async with provider.create_session() as session, terminal_ui("[User] > ") as ui:
        while True:
            linea = await ui.leer()
            if linea is None:
                break

            linea = linea.strip()
            if not linea:
                continue
            if linea.lower() in _COMANDOS_SALIDA:
                break

            resultado = await session.send(linea)
            print(f"sda> {resultado.text}")

    return 0
