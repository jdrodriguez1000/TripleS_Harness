"""Bucle interactivo de conversación (REPL) sobre una ``Session``.

Lee turnos del teclado, los manda a la sesión y muestra la respuesta, todo dentro
de una única sesión de larga vida para que el contexto se conserve entre turnos
(el mecanismo verificado en el spike T-016, ahora manejado por un humano).

Vive fuera de ``sda.core`` porque es un adaptador de entrada/salida, no dominio.
Recibe un ``Provider`` (no un proveedor concreto) para respetar la abstracción.
"""

from __future__ import annotations

import sys

import anyio

from sda.core.provider import Provider

# Palabras que terminan la sesión (se comparan en minúsculas y sin espacios).
_COMANDOS_SALIDA = frozenset({"salir", "exit", "quit"})


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


async def run_repl(provider: Provider) -> int:
    """Abre una sesión y conversa por teclado hasta que el humano termine.

    Devuelve el código de salida (``0`` en una terminación normal).
    """
    _forzar_utf8()
    print("[sda] sesión interactiva — escribe 'salir' para terminar")

    async with provider.create_session() as session:
        while True:
            try:
                # input() es bloqueante: se corre en un hilo para no bloquear el
                # event loop asíncrono de la sesión.
                linea = await anyio.to_thread.run_sync(input, "tú> ")
            except (EOFError, KeyboardInterrupt):
                # Ctrl+Z/Ctrl+D o Ctrl+C: salir limpiamente con un salto de línea.
                print()
                break

            linea = linea.strip()
            if not linea:
                continue
            if linea.lower() in _COMANDOS_SALIDA:
                break

            resultado = await session.send(linea)
            print(f"sda> {resultado.text}")

    return 0
