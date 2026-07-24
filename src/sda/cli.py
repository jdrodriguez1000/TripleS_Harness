"""Punto de entrada de línea de comandos del harness sda.

Define el parser de argumentos y la función ``main()`` que el console script
``sda`` (declarado en pyproject.toml) invoca. Por ahora solo expone un esqueleto:
``--version`` y un subcomando ``start`` que todavía no arranca el harness real.
"""

from __future__ import annotations

import argparse
from importlib.metadata import version


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
        help="Arranca el harness en la carpeta actual (aún no implementado).",
    )

    return parser


def _cmd_start(_args: argparse.Namespace) -> int:
    """Placeholder del subcomando ``start``; la lógica real llega en T-014+."""
    print("[sda] 'start' aún no implementado (T-014+)")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parsea los argumentos, despacha al subcomando y devuelve el código de salida."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "start":
        return _cmd_start(args)

    # Sin subcomando: mostrar la ayuda y salir sin error.
    parser.print_help()
    return 0
