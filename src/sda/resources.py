"""Acceso a los recursos de datos empaquetados con ``sda`` (prompts, plantillas).

Estos ``.md`` viajan dentro del paquete (ver ``pyproject.toml``) para que el
harness funcione instalado y desde cualquier carpeta, sin depender de rutas
relativas al código fuente. Se leen con ``importlib.resources`` (D-016/D-019).
"""

from __future__ import annotations

from importlib.resources import files


def load_prompt(name: str) -> str:
    """Devuelve el texto del prompt ``src/sda/prompts/<name>``."""
    return (files("sda") / "prompts" / name).read_text(encoding="utf-8")


def load_template(name: str) -> str:
    """Devuelve el texto de la plantilla ``src/sda/templates/<name>``."""
    return (files("sda") / "templates" / name).read_text(encoding="utf-8")
