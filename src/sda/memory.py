"""Memoria persistente del **proyecto destino**: la carpeta ``_persistence/``.

Es la bitácora del producto que el harness construye —avance, tareas, decisiones y
lecciones—, no la memoria de la construcción del harness (esa es ``900_persistence/``
de este repo; la separación de propósito la fija D-004). Vive en la carpeta del
proyecto destino y sobrevive entre ejecuciones: es lo que permite que el líder
arranque cada sesión sabiendo todo lo que ya pasó (T-029).

Tres responsabilidades, todas deterministas y todas en Python:

1. **Sembrar** (``seed``) los cuatro archivos desde plantillas empaquetadas, de forma
   idempotente. ``idea.md`` (Fase 1, Step 2) lo pide desde el arranque.
2. **Escribir** (``append_progress``, ``add_task``, ``update_task``, ``add_decision``,
   ``add_lesson``) con formato y numeración garantizados. El LLM nunca escribe aquí
   directamente: solo invoca las herramientas que llaman a estas funciones (D-026).
   En particular **la numeración se calcula aquí**, no la elige el modelo: continuar
   una secuencia es justo lo que un LLM hace mal.
3. **Resumir** (``build_digest``) la memoria en un texto acotado que se le empuja al
   líder en su mensaje de apertura. Empujar un resumen con tope, en vez de dejar que
   el líder lea los archivos enteros bajo demanda, garantiza que **siempre** arranque
   informado y mantiene predecible el costo del componente más caro del sistema
   (Opus + effort high).

Formato Markdown, no JSON: quien escribe y quien lee son LLMs, y el humano tiene que
poder auditar y corregir la bitácora a mano (mismo patrón que ``_context/scope.md``).
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

from sda.resources import load_template

# --- Rutas y archivos convenidos ---------------------------------------------
PERSISTENCE_DIR = "_persistence"

PROGRESS_FILE = "progress.md"
TASKS_FILE = "tasks.md"
DECISIONS_FILE = "decisions.md"
LESSONS_FILE = "lessons.md"

# Archivo de la memoria → plantilla empaquetada que lo siembra.
_SEMILLA = {
    PROGRESS_FILE: "persistence/progress.md",
    TASKS_FILE: "persistence/tasks.md",
    DECISIONS_FILE: "persistence/decisions.md",
    LESSONS_FILE: "persistence/lessons.md",
}

# --- Estados de tarea ---------------------------------------------------------
ESTADO_PENDIENTE = "Pendiente"
ESTADO_EN_CURSO = "En curso"
ESTADO_COMPLETADA = "Completada"
ESTADO_CANCELADA = "Cancelada"

ESTADOS = (ESTADO_PENDIENTE, ESTADO_EN_CURSO, ESTADO_COMPLETADA, ESTADO_CANCELADA)
# Las que siguen vivas: son las que el digest le muestra al líder al arrancar.
ESTADOS_ABIERTOS = (ESTADO_PENDIENTE, ESTADO_EN_CURSO)

# Encabezado bajo el que se insertan los bloques de detalle de cada archivo.
_MARCA_DETALLE_TAREAS = "## Detalle de tareas"

# Topes del digest: cuántas entradas recientes de cada bitácora se empujan.
_DIGEST_PROGRESO = 3
_DIGEST_TAREAS = 10
_DIGEST_DECISIONES = 5
_DIGEST_LECCIONES = 3
# Cuánto texto de cada entrada de progreso se incluye antes de recortar.
_DIGEST_DETALLE_CHARS = 240
# Tope global del digest. Es la garantía de que el costo por arranque no crece con
# el proyecto: el resumen tiene techo aunque la bitácora no lo tenga.
DIGEST_MAX_CHARS = 4000


class MemoriaError(Exception):
    """Operación inválida sobre la memoria (p. ej. actualizar una tarea inexistente).

    La lanzan los escritores y la traducen a texto las herramientas del líder, para
    que el modelo reciba un mensaje accionable en vez de una excepción cruda.
    """


# --- Utilidades internas ------------------------------------------------------


def dir_memoria(project_dir: Path) -> Path:
    """Ruta de la carpeta de memoria dentro del proyecto destino."""
    return project_dir / PERSISTENCE_DIR


def _ruta(project_dir: Path, archivo: str) -> Path:
    return dir_memoria(project_dir) / archivo


def _hoy() -> str:
    """Fecha de hoy en ISO. Aislada para poder fijarla en las pruebas."""
    return date.today().isoformat()


def _leer(project_dir: Path, archivo: str) -> str:
    """Lee un archivo de la memoria, sembrándolo antes si falta."""
    ruta = _ruta(project_dir, archivo)
    if not ruta.is_file():
        seed(project_dir)
    return ruta.read_text(encoding="utf-8")


def _escribir_atomico(ruta: Path, contenido: str) -> None:
    """Escribe el archivo completo de forma atómica (temp + ``os.replace``).

    Mismo criterio que ``state.save``: si el proceso muere en mitad del volcado, la
    bitácora del proyecto no queda a medias.
    """
    tmp = ruta.with_suffix(ruta.suffix + ".tmp")
    tmp.write_text(contenido, encoding="utf-8")
    os.replace(tmp, ruta)


def _normalizar(texto: str) -> str:
    """Colapsa un texto libre del modelo a una sola línea, sin espacios de sobra.

    Se usa para lo que va en títulos y en filas de tabla: un salto de línea suelto
    ahí rompería el Markdown que el resto del módulo vuelve a parsear.
    """
    return " ".join(texto.split()).strip()


def _sin_pipes(texto: str) -> str:
    """Neutraliza las barras verticales para que no partan una fila de tabla."""
    return _normalizar(texto).replace("|", "/")


def _siguiente_codigo(texto: str, prefijo: str) -> str:
    """Devuelve el próximo código libre (``T-001``, ``D-004``…) del archivo.

    Se calcula del máximo existente **+1**, no de la cantidad de entradas: así, si
    alguien borra una entrada a mano, no se reutiliza un código ya citado en otro
    documento.
    """
    numeros = [int(n) for n in re.findall(rf"(?m)^### {prefijo}-(\d+)", texto)]
    return f"{prefijo}-{max(numeros, default=0) + 1:03d}"


def _bloque_tarea(texto: str, codigo: str) -> tuple[int, int] | None:
    """Ubica el bloque de detalle de una tarea: ``(inicio, fin)`` o ``None``.

    El bloque va desde su encabezado ``### T-XXX`` hasta el siguiente ``### `` (o el
    final del archivo).
    """
    encabezado = re.search(rf"(?m)^### {re.escape(codigo)} ", texto)
    if encabezado is None:
        return None
    inicio = encabezado.start()
    siguiente = re.search(r"(?m)^### ", texto[encabezado.end() :])
    fin = encabezado.end() + siguiente.start() if siguiente else len(texto)
    return inicio, fin


def _insertar_fila(texto: str, fila: str) -> str:
    """Inserta una fila al final de la tabla-índice de ``tasks.md``.

    La tabla es todo lo que está antes de ``## Detalle de tareas``; la fila nueva va
    después de la última línea que ya empieza por ``|`` (sea la cabecera o una fila
    previa).
    """
    corte = texto.find(_MARCA_DETALLE_TAREAS)
    cabeza = texto if corte == -1 else texto[:corte]
    cola = "" if corte == -1 else texto[corte:]

    lineas = cabeza.splitlines()
    ultima_fila = max(
        (i for i, ln in enumerate(lineas) if ln.lstrip().startswith("|")),
        default=None,
    )
    if ultima_fila is None:
        # Sin tabla reconocible (alguien la borró a mano): se añade al final.
        return f"{cabeza.rstrip()}\n{fila}\n\n{cola}" if cola else f"{cabeza.rstrip()}\n{fila}\n"

    lineas.insert(ultima_fila + 1, fila)
    cabeza_nueva = "\n".join(lineas).rstrip() + "\n"
    return f"{cabeza_nueva}\n{cola}" if cola else cabeza_nueva


def _anexar_bloque(texto: str, bloque: str) -> str:
    """Añade un bloque de detalle al final del archivo, con una línea en blanco."""
    return f"{texto.rstrip()}\n\n{bloque.strip()}\n"


# --- Siembra ------------------------------------------------------------------


def seed(project_dir: Path) -> list[str]:
    """Crea los archivos de ``_persistence/`` que falten. Devuelve cuáles creó.

    Es **idempotente** y nunca pisa contenido existente, así que también repara un
    proyecto anterior a T-029 (cuya carpeta ``_persistence/`` nació vacía) sin tocar
    lo que ya tuviera escrito.
    """
    destino = dir_memoria(project_dir)
    destino.mkdir(parents=True, exist_ok=True)

    creados: list[str] = []
    for archivo, plantilla in _SEMILLA.items():
        ruta = destino / archivo
        if ruta.exists():
            continue
        ruta.write_text(load_template(plantilla), encoding="utf-8")
        creados.append(archivo)
    return creados


# --- Escritores ---------------------------------------------------------------


def append_progress(project_dir: Path, titulo: str, detalle: str = "") -> str:
    """Añade una entrada fechada a ``progress.md``. Devuelve la fecha usada."""
    titulo_limpio = _normalizar(titulo)
    if not titulo_limpio:
        raise MemoriaError("La entrada de progreso necesita un título.")

    fecha = _hoy()
    cuerpo = detalle.strip()
    bloque = f"### {fecha} — {titulo_limpio}\n"
    if cuerpo:
        bloque += f"\n{cuerpo}\n"

    texto = _anexar_bloque(_leer(project_dir, PROGRESS_FILE), bloque)
    _escribir_atomico(_ruta(project_dir, PROGRESS_FILE), texto)
    return fecha


def add_task(project_dir: Path, titulo: str, detalle: str = "") -> str:
    """Registra una tarea nueva en estado ``Pendiente``. Devuelve su código."""
    titulo_limpio = _sin_pipes(titulo)
    if not titulo_limpio:
        raise MemoriaError("La tarea necesita un título.")

    texto = _leer(project_dir, TASKS_FILE)
    codigo = _siguiente_codigo(texto, "T")

    texto = _insertar_fila(texto, f"| {codigo} | {titulo_limpio} | {ESTADO_PENDIENTE} |")

    bloque = (
        f"### {codigo} — {titulo_limpio}\n"
        f"**Estado:** {ESTADO_PENDIENTE}\n"
        f"**Creada:** {_hoy()}\n"
    )
    cuerpo = detalle.strip()
    if cuerpo:
        bloque += f"\n{cuerpo}\n"

    _escribir_atomico(_ruta(project_dir, TASKS_FILE), _anexar_bloque(texto, bloque))
    return codigo


def update_task(project_dir: Path, codigo: str, estado: str, nota: str = "") -> None:
    """Cambia el estado de una tarea (tabla-índice y bloque de detalle a la vez).

    Mantener sincronizadas las dos representaciones es responsabilidad de esta
    función, no del modelo: el índice es lo que el digest lee al arrancar, así que
    una tabla desfasada dejaría al líder trabajando sobre tareas ya cerradas.
    """
    codigo = _normalizar(codigo).upper()
    estado = _normalizar(estado).capitalize()
    # ``capitalize`` deja "En curso" bien y "Pendiente" igual; se valida abajo.
    coincidencia = next((e for e in ESTADOS if e.lower() == estado.lower()), None)
    if coincidencia is None:
        raise MemoriaError(
            f"Estado '{estado}' inválido. Estados válidos: {', '.join(ESTADOS)}."
        )
    estado = coincidencia

    texto = _leer(project_dir, TASKS_FILE)
    limites = _bloque_tarea(texto, codigo)
    if limites is None:
        raise MemoriaError(f"No existe la tarea {codigo} en {TASKS_FILE}.")

    # 1. Fila de la tabla-índice: se reescribe la última columna.
    texto, cambios = re.subn(
        rf"(?m)^\|\s*{re.escape(codigo)}\s*\|([^|\n]*)\|[^|\n]*\|",
        lambda m: f"| {codigo} |{m.group(1)}| {estado} |",
        texto,
        count=1,
    )
    if cambios:
        # La sustitución movió los índices del bloque: hay que reubicarlo.
        limites = _bloque_tarea(texto, codigo)
        assert limites is not None

    # 2. Bloque de detalle: estado, fecha de actualización y nota opcional.
    inicio, fin = limites
    bloque = texto[inicio:fin]
    bloque, encontrados = re.subn(
        r"(?m)^\*\*Estado:\*\*.*$", f"**Estado:** {estado}", bloque, count=1
    )
    if not encontrados:
        # Detalle editado a mano sin la línea de estado: se añade tras el título.
        bloque = re.sub(r"(?m)^(### .*)$", rf"\1\n**Estado:** {estado}", bloque, count=1)

    bloque, actualizados = re.subn(
        r"(?m)^\*\*Actualizada:\*\*.*$", f"**Actualizada:** {_hoy()}", bloque, count=1
    )
    if not actualizados:
        # Va después de "Creada" para que la cabecera se lea en orden cronológico;
        # si el bloque fue editado a mano y no la tiene, cae tras "Estado".
        ancla = r"(?m)^(\*\*Creada:\*\*.*)$" if "**Creada:**" in bloque else r"(?m)^(\*\*Estado:\*\*.*)$"
        bloque = re.sub(ancla, rf"\1\n**Actualizada:** {_hoy()}", bloque, count=1)

    nota_limpia = nota.strip()
    if nota_limpia:
        bloque = f"{bloque.rstrip()}\n\n{_hoy()} — {nota_limpia}\n"

    texto = f"{texto[:inicio]}{bloque.rstrip()}\n\n{texto[fin:].lstrip()}"
    _escribir_atomico(_ruta(project_dir, TASKS_FILE), texto.rstrip() + "\n")


def add_decision(project_dir: Path, titulo: str, decision: str, razon: str = "") -> str:
    """Registra una decisión en ``decisions.md``. Devuelve su código ``D-XXX``."""
    titulo_limpio = _normalizar(titulo)
    cuerpo = decision.strip()
    if not titulo_limpio or not cuerpo:
        raise MemoriaError("Una decisión necesita título y contenido.")

    texto = _leer(project_dir, DECISIONS_FILE)
    codigo = _siguiente_codigo(texto, "D")

    bloque = (
        f"### {codigo} — {titulo_limpio}\n"
        f"**Fecha:** {_hoy()}\n"
        f"**Decisión:** {cuerpo}\n"
    )
    motivo = razon.strip()
    if motivo:
        bloque += f"**Razón:** {motivo}\n"

    _escribir_atomico(_ruta(project_dir, DECISIONS_FILE), _anexar_bloque(texto, bloque))
    return codigo


def add_lesson(project_dir: Path, titulo: str, leccion: str, contexto: str = "") -> str:
    """Registra una lección en ``lessons.md``. Devuelve su código ``L-XXX``."""
    titulo_limpio = _normalizar(titulo)
    cuerpo = leccion.strip()
    if not titulo_limpio or not cuerpo:
        raise MemoriaError("Una lección necesita título y contenido.")

    texto = _leer(project_dir, LESSONS_FILE)
    codigo = _siguiente_codigo(texto, "L")

    bloque = f"### {codigo} — {titulo_limpio}\n**Fecha:** {_hoy()}\n"
    situacion = contexto.strip()
    if situacion:
        bloque += f"**Contexto:** {situacion}\n"
    bloque += f"**Lección:** {cuerpo}\n"

    _escribir_atomico(_ruta(project_dir, LESSONS_FILE), _anexar_bloque(texto, bloque))
    return codigo


# --- Digest -------------------------------------------------------------------


def _entradas(texto: str, patron: str) -> list[tuple[str, str]]:
    """Extrae los bloques ``### <encabezado>`` de un archivo como (encabezado, cuerpo)."""
    posiciones = list(re.finditer(patron, texto))
    salida: list[tuple[str, str]] = []
    for i, m in enumerate(posiciones):
        fin = posiciones[i + 1].start() if i + 1 < len(posiciones) else len(texto)
        salida.append((m.group(1).strip(), texto[m.end() : fin].strip()))
    return salida


def _resumir(cuerpo: str, limite: int = _DIGEST_DETALLE_CHARS) -> str:
    """Aplana un cuerpo a una línea y lo recorta al límite de caracteres."""
    plano = _normalizar(re.sub(r"\*\*(.+?):\*\*", r"\1:", cuerpo))
    if len(plano) <= limite:
        return plano
    return plano[:limite].rstrip() + "…"


def _digest_progreso(project_dir: Path) -> list[str]:
    ruta = _ruta(project_dir, PROGRESS_FILE)
    if not ruta.is_file():
        return []
    entradas = _entradas(ruta.read_text(encoding="utf-8"), r"(?m)^### (.+)$")
    if not entradas:
        # Sección ausente, no sección vacía: un archivo recién sembrado no tiene por
        # qué gastar espacio del digest para decir que está vacío.
        return []

    # El encabezado de recorte solo aparece si de verdad se está recortando algo.
    lineas = (
        [f"Últimas {_DIGEST_PROGRESO} de {len(entradas)} entradas:"]
        if len(entradas) > _DIGEST_PROGRESO
        else []
    )
    for encabezado, cuerpo in entradas[-_DIGEST_PROGRESO:]:
        resumen = _resumir(cuerpo)
        lineas.append(f"- {encabezado}" + (f": {resumen}" if resumen else ""))
    return lineas


def _digest_tareas(project_dir: Path) -> list[str]:
    ruta = _ruta(project_dir, TASKS_FILE)
    if not ruta.is_file():
        return []
    texto = ruta.read_text(encoding="utf-8")

    filas = [
        (m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
        for m in re.finditer(r"(?m)^\|\s*(T-\d+)\s*\|([^|\n]*)\|([^|\n]*)\|", texto)
    ]
    if not filas:
        return []

    abiertas = [f for f in filas if f[2].lower() in {e.lower() for e in ESTADOS_ABIERTOS}]
    if not abiertas:
        return [f"{len(filas)} tareas registradas, ninguna abierta."]

    plural = "s" if len(abiertas) != 1 else ""
    lineas = [f"{len(abiertas)} abierta{plural} de {len(filas)} registrada{'s' if len(filas) != 1 else ''}:"]
    for codigo, titulo, estado in abiertas[:_DIGEST_TAREAS]:
        lineas.append(f"- {codigo} [{estado}] {titulo.strip()}")
    if len(abiertas) > _DIGEST_TAREAS:
        lineas.append(f"- (…y {len(abiertas) - _DIGEST_TAREAS} más)")
    return lineas


def _digest_codificado(project_dir: Path, archivo: str, patron: str, tope: int) -> list[str]:
    """Resume ``decisions.md``/``lessons.md``: las últimas N entradas, solo títulos."""
    ruta = _ruta(project_dir, archivo)
    if not ruta.is_file():
        return []
    entradas = _entradas(ruta.read_text(encoding="utf-8"), patron)
    if not entradas:
        return []

    lineas = []
    for encabezado, cuerpo in entradas[-tope:]:
        fecha = re.search(r"\*\*Fecha:\*\*\s*(\S+)", cuerpo)
        lineas.append(f"- {encabezado}" + (f" ({fecha.group(1)})" if fecha else ""))
    if len(entradas) > tope:
        lineas.insert(0, f"Últimas {tope} de {len(entradas)}:")
    return lineas


def build_digest(project_dir: Path, *, max_chars: int = DIGEST_MAX_CHARS) -> str:
    """Arma el resumen acotado de la memoria que se le empuja al líder al arrancar.

    Devuelve cadena vacía si el proyecto todavía no tiene memoria con contenido, para
    que el mensaje de apertura no arrastre secciones vacías en un proyecto nuevo.

    El tope de tamaño es deliberado: garantiza que el costo del arranque no crezca
    con la antigüedad del proyecto. Lo que no cabe sigue disponible para el líder vía
    ``Read`` sobre ``_persistence/``.
    """
    if not dir_memoria(project_dir).is_dir():
        return ""

    secciones = [
        ("PROGRESO", _digest_progreso(project_dir)),
        ("TAREAS", _digest_tareas(project_dir)),
        (
            "DECISIONES",
            _digest_codificado(
                project_dir, DECISIONS_FILE, r"(?m)^### (D-\d+ .+)$", _DIGEST_DECISIONES
            ),
        ),
        (
            "LECCIONES",
            _digest_codificado(
                project_dir, LESSONS_FILE, r"(?m)^### (L-\d+ .+)$", _DIGEST_LECCIONES
            ),
        ),
    ]
    con_contenido = [(t, ls) for t, ls in secciones if ls]
    if not con_contenido:
        return ""

    partes = [f"MEMORIA DEL PROYECTO (_persistence/, al {_hoy()})", ""]
    for titulo, lineas in con_contenido:
        partes.append(f"{titulo}:")
        partes.extend(lineas)
        partes.append("")
    partes.append(
        "Este resumen está acotado. Si necesitas el detalle completo de alguna "
        f"entrada, léelo con Read sobre {PERSISTENCE_DIR}/."
    )

    digest = "\n".join(partes)
    if len(digest) > max_chars:
        digest = (
            digest[:max_chars].rstrip()
            + f"\n\n[Resumen recortado. El detalle completo está en {PERSISTENCE_DIR}/.]"
        )
    return digest
