---
name: session-start-protocol
description: Protocolo obligatorio de inicio de sesión. Se debe invocar siempre que comience o se reanude una sesión de trabajo en este proyecto, antes de realizar cualquier otra acción. Lee de forma obligatoria progress.md y tasks.md, y a demanda los demás archivos de 900_persistence (lessons.md, decisions.md, assumptions.md, constraints.md).
---

# Session Start Protocol

Protocolo que garantiza que cualquier agente retome el contexto correcto del proyecto antes de hacer cualquier otra cosa.

## Lectura obligatoria (siempre, en toda sesión)

1. `900_persistence/progress.md` — estado general del proyecto: qué se hizo, qué está en progreso, qué sigue, bloqueos.
2. `900_persistence/tasks.md` — índice de tareas (código `T-XXX`) con su estado: Implementada, No implementada, Cancelada/Suspendida.

Estos dos archivos se leen SIEMPRE, sin excepción, al iniciar o reanudar una sesión. No se debe empezar a trabajar en el proyecto sin haberlos leído primero.

## Lectura a demanda (solo si el contexto la requiere)

Los siguientes archivos de `900_persistence/` NO se leen automáticamente; se leen solo cuando la tarea en curso lo justifique:

- `lessons.md` — antes de repetir un enfoque que pudo haber fallado antes, o al enfrentar un problema que suene ya conocido.
- `decisions.md` — cuando se necesite entender por qué el proyecto está construido de cierta forma, o antes de proponer un cambio que pueda contradecir una decisión previa.
- `assumptions.md` — cuando una tarea dependa de un supuesto no verificado del proyecto.
- `constraints.md` — cuando se esté evaluando una solución que pueda chocar con una restricción técnica, de negocio, tiempo, recursos o legal.

## Salida esperada del protocolo

Al ejecutar este protocolo, se debe producir un resumen breve que incluya:

- Estado general actual del proyecto (de `progress.md`).
- Últimas tareas completadas (de `tasks.md`, estado "Implementada").
- Próximas tareas pendientes (de `tasks.md`, estado "No implementada"), priorizando cuál debería abordarse a continuación según dependencias, bloqueos registrados en `progress.md` y orden lógico.

No se debe leer el archivo completo de `tasks.md` línea por línea si el índice (tabla al inicio del archivo) ya responde la pregunta.
