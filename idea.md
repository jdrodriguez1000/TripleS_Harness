La idea es construir un Harness siguiendo dos flujos REPL.

El primer flujo REPL es asociado al orquestador, llamado también flujo externo
El segundo flujo REPL o mas interno es al subagente para poder observarlo y evaluarlo.

El objetivo es construir este harness utilizando el SDK de Anthropic pero pagando suscripción, es decir no con API.

Este flujo será reutilizable en otras carpetas y en otras terminales, es decir en una carpeta constuimos el harness básico y en otra carpeta de un proyecto lo utilizamos.

Este flujo hoy funciona con Claude Code pero la idea es que en el futuro podamos conectar con Codex o con otros.



Flujo Completo Rediseñado (End-to-End)[HUMANO] ──(Inicia)──► [ORCHESTRATOR-LEADER (REPL Ext)] ──(Supervisa)──► [ONBOARDING-READER (REPL Int)]
    ▲                              │                                              │
    │                              ▼                                              ▼
 [Aprueba/Rechaza] ◄─── (Pide Aprobación)                                [Evalúa y Crea Draft]


Fase 1: Bootstrapping & Validación de Estado
1. Inicialización Limpia: El humano crea una carpeta vacía, la vincula opcionalmente con Git/GitHub e invoca el comando global de tu Harness desde su terminal.
2. Auto-Diagnóstico de Persistencia: El orchestrator-leader toma el control de la sesión REPL externa, inspecciona el entorno y, al detectar que es un proyecto nuevo, genera automáticamente la estructura base en _persistence/ (archivos vacíos de tareas, progreso, lecciones y decisiones).

Fase 2: Ejecución del REPL Interno (Sandbox de Lectura y Extracción)
1. Invocación del Subagente: El orchestrator-leader lanza el bucle REPL interno e instruye al onboarding-reader para explorar la carpeta del proyecto y leer todos los documentos de contexto existentes.
2. Construcción en Borrador: El onboarding-reader procesa la información y escribe la primera versión del archivo document-extract.md marcándolo explícitamente en el encabezado con el estado: DRAFT.
3. Evaluación de Calidad Interna (Auditoría Ciega): En el REPL interno, el orchestrator-leader (o un módulo evaluador) audita el borrador antes de mostrárselo al humano.
	* Si el borrador es ambiguo o incompleto: El REPL interno exige correcciones al onboarding-reader de forma transparente sin molestar al usuario.
	* Si el borrador supera el umbral de calidad: Se da por finalizado el REPL interno.

Fase 3: Puerta de Aprobación Humana (REPL Externo)
1. Notificación y Cambio de Estado: El orchestrator-leader cambia el estado del archivo a PENDING_HUMAN_REVIEW y le presenta un resumen ejecutivo al humano en el REPL externo solicitando su validación.
2. Punto de Decisión Humana: El humano revisa el archivo document-extract.md en su editor y responde en la terminal con una de dos opciones:
	* Opción A (Aprobado): El humano da luz verde.
	* Opción B (Rechazado con Feedback): El humano explica qué falta o qué está mal (ej. "Falta incluir el alcance del módulo de autenticación").

Fase 4: Manejo de Ramificaciones y Cierre de Sesión
1. Manejo de Rechazo (Bucle de Corrección): Si el humano rechaza, el orchestrator-leader reactiva el REPL interno devolviendo el onboarding-reader al paso 4 con las observaciones fijadas por el usuario, repitiendo el ciclo hasta obtener aprobación.
2. Promoción y Cierre de Documento: Ante la aprobación del humano, el orchestrator-leader cambia formalmente el estado de document-extract.md a APPROVED y bloquea el archivo contra modificaciones accidentales de lectura.
3. Sincronización de la Memoria Persistente: Con el contexto base aprobado, el orchestrator-leader actualiza automáticamente progress.md (marcando la fase de Onboarding como completada) y pobla tasks.json con las primeras tareas operativas del proyecto.
4. Rendición de Cuentas y Estado de Espera: El orchestrator-leader imprime en la terminal el resumen de la arquitectura aprobada, las tareas iniciales registradas y queda en modo de espera listo para la jornada de trabajo.


# Arquitectura del Harness: Flujo Completo Rediseñado con Gestión de Estado

Este documento define la arquitectura operacional del Harness basado en un **Doble Bucle REPL** (Controlador Externo + Sandbox Interno de Subagentes) y respaldado por una **Máquina de Estados Persistente en Disco** (`_harness_state.json`).

---

## Diagrama de la Arquitectura

```text
[HUMANO] ──(Comando Harness)──► [ORCHESTRATOR-LEADER (REPL Ext)]
                                      │
                         Escribe / Lee _harness_state.json
                                      │
                                      ▼
             ┌─────────────────────────────────────────────────┐
             │       REPL INTERNO (Sandbox Subagentes)         │
             │   Orchestrator ──(Supervisa)──► Subagente      │
             └─────────────────────────────────────────────────┘

Flujo Paso a Paso (End-to-End)

Fase 1: Bootstrapping & Diagnóstico de Estado

Step 1: Invocación e Inspección de Disco
	* Acción: El humano abre la terminal en una carpeta de proyecto y ejecuta el comando global del Harness.
	* Mecanismo: El orchestrator-leader toma el control de la sesión e inspecciona inmediatamente el sistema de archivos buscando _harness_state.json.

Step 2: Diagnóstico de Escenario y Creación Base
* Escenario A (Proyecto Nuevo): Si _harness_state.json no existe, el Orquestador lo crea en disco marcando:
	* "current_phase": "BOOTSTRAPPING"
	* "transaction_lock": false
	*"active_repl": "EXTERNAL"
	A continuación, genera las plantillas iniciales en la carpeta _persistence/ (progress.md, tasks.json, etc.).

* Escenario B (Proyecto Existente / Reanudación): Si _harness_state.json ya existe, el Orquestador lee el archivo en memoria.
	* Si lee "transaction_lock": true, comprende que la sesión anterior se interrumpió de forma abrupta (apagón/corte de luz) mientras un subagente trabajaba.
	* Si lee "pending_approval_file": "document-extract.md", entiende que estaba esperando la decisión del humano antes de cerrarse.	


Fase 2: Ejecución del REPL Interno (Sandbox de Lectura y Extracción)

Step 3: Bloqueo de Transacción y Delegación
	* Acción: El Orquestador decide lanzar la tarea de extracción de contexto.
	* Escritura en _harness_state.json:
		* "active_repl": "INTERNAL"
		* "active_subagent": "onboarding-reader"
		* "active_task_id": "TASK-001"
		* "transaction_lock": true (Avisa que hay un proceso en marcha que no debe ser alterado)
	* Efecto: Se activa el bucle REPL interno. El onboarding-reader comienza a explorar y leer los archivos del proyecto.

Step 4: Construcción Atómica con Checkpointing
	* Acción: El onboarding-reader procesa la información y escribe progresivamente el archivo temporal document-extract.md.tmp.
	* Escritura en _harness_state.json: A medida que procesa archivos pesados, el subagente actualiza la sección de checkpoints:
		* "checkpoint": { "last_processed_file": "arquitectura.pdf", "progress": "70%" }

Step 5: Evaluación de Calidad Interna (Evals Audit)
	* Acción: El onboarding-reader termina de redactar el borrador. El orchestrator-leader (o el módulo evaluador) audita la calidad de document-extract.md.tmp en el REPL interno.
	* Resultado:
		* Si no supera el umbral (Score < 4.0): El REPL interno exige correcciones al subagente sin molestar al humano.
		* Si aprueba: El Orquestador promociona el archivo borrador renunciando a document-extract.md.tmp para convertirlo en document-extract.md, marcando en su encabezado el estado PENDING_REVIEW.


Fase 3: Puerta de Aprobación Humana (REPL Externo)

Step 6: Liberación de Transacción y Notificación
	* Acción: El REPL interno finaliza su ciclo. El Orquestador regresa al REPL externo para hablar con el usuario.
	* Escritura en _harness_state.json:
		* "active_repl": "EXTERNAL"
		* "active_subagent": null
		* "transaction_lock": false
		* "pending_approval_file": "document-extract.md"
		* "current_phase": "HUMAN_REVIEW"
	* Efecto: El Orquestador le presenta un resumen ejecutivo al humano en la terminal y solicita su validación.

Step 7: Punto de Decisión Humana
	* Acción: El humano revisa el borrador en su editor y responde en la terminal con una de dos opciones:
		* Aprobado: Da luz verde al documento.
		* Rechazado: Explica las observaciones o información faltante.


Fase 4: Manejo de Ramificaciones y Cierre de Sesión

Step 8: Manejo de Rechazo (Si el Humano Rechaza)
	* Acción: Si el humano rechaza, el Orquestador captura las observaciones del usuario.
	* Escritura en _harness_state.json: Se reactiva el REPL interno ("active_repl": "INTERNAL", "transaction_lock": true).
	* Efecto: Se devuelve al onboarding-reader al Step 4 inyectándole el feedback del humano para ajustar el documento.

Step 9: Promoción y Cierre del Documento (Si el Humano Aprueba)
	* Acción: El humano aprueba. El Orquestador cambia formalmente el encabezado de document-extract.md a estado APPROVED.
	* Escritura en _harness_state.json:
		* "pending_approval_file": null
		* "current_phase": "CONTEXT_APPROVED"
		* "last_completed_task_id": "TASK-001"

Step 10: Sincronización de la Memoria Persistente
	* Acción: Con el contexto base aprobado, el orchestrator-leader actualiza automáticamente los archivos de _persistence/:
		* En progress.md: Registra que la fase de Onboarding ha finalizado con éxito.
		* En tasks.json: Cambia TASK-001 a estado COMPLETED y habilita la siguiente micro-tarea (TASK-002).

Step 11: Rendición de Cuentas y Estado Listo
	* Acción: El Orquestador imprime en la terminal el resumen del contexto aprobado y la lista de tareas operativas desbloqueadas.
	* Escritura Final en _harness_state.json:
		* "active_repl": "EXTERNAL"
		* "transaction_lock": false
		* "current_phase": "READY_FOR_WORK"
	* Efecto: El Harness queda en modo de espera interactivo, listo para comenzar la jornada de desarrollo con el agente-trabajador.


Matriz de Sincronización entre Archivos
Evento del Flujo		_harness_state.json					_persistence/					Archivos Temporales
Inicio de Extracción		"transaction_lock": true				No cambia					Se crea document-extract.md.tmp
Avance parcial (50%)		"checkpoint": {"progress": "50%"}			No cambia					Se actualiza .tmp
Paso a Revisión			"pending_approval_file": "document-extract.md"		Nace document-extract.md (DRAFT)		Se elimina .tmp
Aprobación Humana		"current_phase": "READY_FOR_WORK"			progress.md y tasks.json actualizados		Sin temporales