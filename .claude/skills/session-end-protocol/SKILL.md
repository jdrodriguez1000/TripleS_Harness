---
name: session-end-protocol
description: Protocolo obligatorio de cierre de sesión. Se debe invocar siempre que se vaya a cerrar, terminar o pausar una sesión de trabajo en este proyecto. Actualiza de forma obligatoria progress.md y tasks.md, y a demanda los demás archivos de 900_persistence (lessons.md, decisions.md, assumptions.md, constraints.md) según lo ocurrido durante la sesión.
---

# Session End Protocol

Protocolo que garantiza que el estado del proyecto en `900_persistence/` quede al día antes de cerrar una sesión de trabajo, para que la siguiente sesión pueda retomar el contexto sin pérdida de información.

## Actualización obligatoria (siempre, en todo cierre)

1. `900_persistence/progress.md`
   - Actualizar **Última actualización** y **Estado general**.
   - Actualizar **Resumen actual**.
   - Mover ítems de "En progreso" a "Hecho" si se completaron en la sesión.
   - Registrar nuevos ítems en "Hecho", "En progreso", "Próximo" o "Bloqueos" según lo ocurrido.

2. `900_persistence/tasks.md`
   - Para cada tarea trabajada en la sesión: crear entrada nueva (`T-XXX` siguiente disponible) o actualizar el estado de una existente (Implementada / No implementada / Cancelada-Suspendida).
   - Mantener sincronizada la tabla índice con el detalle de cada tarea.

Estos dos archivos se actualizan SIEMPRE al cerrar sesión, incluso si el avance fue mínimo o solo se descartó una idea.

## Actualización a demanda (solo si ocurrió durante la sesión)

- `lessons.md` — si se aprendió algo no obvio (un enfoque que falló, una causa raíz sorprendente, algo que evitar o repetir a futuro).
- `decisions.md` — si se tomó una decisión de diseño, arquitectura o alcance, con su razón y alternativas descartadas.
- `assumptions.md` — si se asumió algo no verificado que condiciona trabajo futuro, o si un supuesto previo quedó invalidado.
- `constraints.md` — si se descubrió o impuso una restricción nueva (técnica, de negocio, tiempo, recursos o legal).

No actualizar estos cuatro archivos si nada relevante ocurrió en la sesión que amerite registrarlos: evitar entradas vacías o redundantes.

## Reglas de edición

- Usar fecha real (formato `YYYY-MM-DD`) en cada entrada nueva.
- No reescribir ni borrar el historial existente; añadir, no eliminar salvo corrección de un error.
- Mantener el índice de cada archivo (tabla o lista de enlaces) sincronizado con el detalle, para que la próxima sesión pueda ubicar información sin leer el archivo completo.
- Ser conciso: registrar el qué y el porqué, no una transcripción completa de la sesión.

## Commit y push obligatorios (siempre, al final del cierre)

Después de actualizar los archivos de `900_persistence/` (y cualquier otro cambio de la sesión), es OBLIGATORIO dejar el trabajo respaldado en el repositorio remoto de GitHub:

1. Repositorio remoto de este proyecto: `https://github.com/jdrodriguez1000/TripleS_Harness.git` (remote `origin`).
2. Verificar `git status` para revisar qué cambió antes de agregar archivos (nunca usar `git add -A` a ciegas; revisar que no se incluyan secretos o archivos que no correspondan).
3. `git add` de los archivos relevantes de la sesión (código, `900_persistence/`, configuración de `.claude/`, etc.).
4. Crear un commit con mensaje breve que resuma qué se hizo en la sesión (qué, no cómo), en español, siguiendo el estilo de commits ya usado en el repo si existe.
5. `git push` al remoto `origin` en la rama actual.

Este paso es obligatorio en todo cierre de sesión donde haya cambios para confirmar (staged o sin trackear), sin excepción, salvo que el usuario indique explícitamente lo contrario para esa sesión puntual. Si no hay ningún cambio pendiente, se omite el commit (no crear commits vacíos) pero se debe informar explícitamente que no había nada que respaldar.
