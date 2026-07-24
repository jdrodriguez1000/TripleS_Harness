"""Punto de entrada de línea de comandos del harness sda.

Define el parser de argumentos y la función ``main()`` que el console script
``sda`` (declarado en pyproject.toml) invoca. Por ahora solo expone un esqueleto:
``--version`` y un subcomando ``start`` que todavía no arranca el harness real.
"""

from __future__ import annotations

import argparse
from importlib.metadata import version

import anyio

from sda.providers.claude_sdk import ClaudeSDKProvider
from sda.repl import run_repl


def build_parser() -> argparse.ArgumentParser:
    """Construye y devuelve el parser de argumentos del CLI ``sda``."""
    parser = argparse.ArgumentParser(
        prog="sda",
        description="Harness agéntico de desarrollo de software (sda).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"sda {version('sda')}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="<comando>",
    )
    subparsers.add_parser(
        "start",
        help="Abre una sesión interactiva en la carpeta actual.",
    )

    return parser


def _cmd_start(_args: argparse.Namespace) -> int:
    """Arranca una sesión interactiva (REPL) sobre el proveedor de suscripción."""
    provider = ClaudeSDKProvider()
    return anyio.run(run_repl, provider)


def main(argv: list[str] | None = None) -> int:
    """Parsea los argumentos, despacha al subcomando y devuelve el código de salida."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "start":
        return _cmd_start(args)

    # Sin subcomando: mostrar la ayuda y salir sin error.
    parser.print_help()
    return 0
