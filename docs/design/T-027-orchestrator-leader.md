# Diseño T-027 — El `orchestrator-leader` como agente líder del bucle externo

> **Estado del documento:** DRAFT — análisis y diseño, sin implementación.
> **Fecha:** 2026-07-24
> **Rama de trabajo:** `t-027-sesion-lider`
> **Tarea:** T-027 — Analizar el agente como sesión principal/líder (Opus + effort high).
> **Alcance:** definir cómo un agente LLM (`orchestrator-leader`) reemplaza el bucle
> externo de Python que hoy vive en `src/sda/orchestrator.py::Orchestrator.run()`,
> **preservando** la observabilidad del bucle interno (D-021) y las garantías
> deterministas de la máquina de estados y la puerta de aprobación humana.
>
> Este documento es también la **base arquitectónica de los agentes que se sumen
> después** al doble bucle (entrevistador, planificador, trabajador, etc.): el
> patrón "el LLM decide / las herramientas hacen cumplir" y el contrato de
> herramientas en-proceso se definen aquí una sola vez.

---

## 1. Contexto y problema

### 1.1 Qué existe hoy

El bucle externo del harness es **código Python puro**: `Orchestrator.run()` lee el
teclado, despacha según `current_phase` con `if/elif`, detecta el scope lleno con
una regex, conduce la sesión interna del `onboarding-reader`, corre la evaluación
(stub), muta `_harness_state.json` y el frontmatter del entregable, y arbitra la
puerta de aprobación humana. Hoy **no hay ninguna sesión LLM cara al humano**: la
única sesión real contra el modelo es la interna del `onboarding-reader`
(Sonnet + high, D-025).

Esto contradice la visión de `idea.md` y D-002/D-005, donde el `orchestrator-leader`
es un **agente** que "toma el control de la sesión externa" y es el único que habla
con el humano.

### 1.2 Qué se quiere

Que el `orchestrator-leader` sea un **agente LLM real** (Opus + effort `high`,
D-025) que reemplace **por completo** el bucle externo de Python: que sea él quien
conversa con el humano, decide cuándo lanzar el bucle interno, presenta el borrador
y gestiona la aprobación.

### 1.3 La tensión central

D-021 estableció la **Forma A**: es *nuestro código Python* quien conduce las dos
sesiones separadas, precisamente para poder **observar y evaluar el bucle interno
turno a turno** (exigencia de `idea.md`, líneas 3-4). Si el líder-agente lanzara al
`onboarding-reader` con el **mecanismo nativo de subagentes del SDK** (Task /
`AgentDefinition`), el bucle interno se volvería una **caja negra dentro del
agente** y perderíamos esa observabilidad — justo lo que D-021 rechazó.

**El problema de diseño de T-027 es, por tanto:** ¿cómo hacer que un agente lidere
el bucle externo sin sacrificar (a) la observabilidad del bucle interno, (b) el
determinismo de la máquina de estados y la recuperación ante caída, y (c) la
seguridad de la puerta de aprobación humana?

---

## 2. Principio rector: **el LLM decide, las herramientas hacen cumplir**

La decisión de fondo es **no** mover las siete responsabilidades del bucle externo
al juicio del LLM. Se reparten según su naturaleza:

| # | Responsabilidad actual | ¿Quién manda tras T-027? | Por qué |
|---|---|---|---|
| 1 | Poseer la conversación con el humano | **LLM (líder)** | Es su fortaleza: lenguaje natural, resúmenes ejecutivos ricos. |
| 2 | Decidir la transición de fase | **LLM (líder)**, acotado por herramientas | El líder decide *cuándo* avanzar; la herramienta valida la precondición. |
| 3 | Detectar que el scope está lleno | **Herramienta determinista** invocada por el líder | La verdad la da `scope_esta_lleno()` (Python), no la impresión del LLM. |
| 4 | Lanzar y conducir el bucle interno | **LLM decide invocar / herramienta ejecuta y observa** | El líder elige *cuándo* y *con qué instrucción*; Python conduce y observa (D-021). |
| 5 | Evaluar el borrador (auditoría ciega) | **Herramienta / agente evaluador aparte** (D-005) | Quien escribe no debe juzgarse; la eval es una llamada separada. |
| 6 | Mutar estado / frontmatter atómicamente | **Herramienta determinista (efecto lateral)** | El `transaction_lock` y la promoción atómica no pueden depender de que el LLM "se acuerde". |
| 7 | La puerta de aprobación humana | **Herramienta determinista, forzada** | Es un límite de seguridad: el LLM no puede auto-aprobar. |

La regla operativa: **el LLM nunca escribe `_harness_state.json` ni promueve el
documento con un `Write` genérico.** Solo puede hacerlo llamando a herramientas
nuestras que aplican el cambio de forma determinista y atómica como **efecto
lateral** de la operación. Así el líder queda "con las manos atadas" en lo peligroso
(estado, lock, gate) y libre en lo conversacional.

---

## 3. Mecanismo de observabilidad: la herramienta en-proceso

### 3.1 La distinción que lo hace posible

Una **herramienta en-proceso** (in-process `@tool` / servidor MCP en el mismo
proceso Python del harness) **no es una instrucción que el modelo ejecuta por su
cuenta: es una llamada a una función Python nuestra.** El modelo solo decide
*cuándo* llamarla y *con qué argumentos*; la ejecución es 100% nuestra.

Por eso, la herramienta es **una puerta de vuelta a nuestro código**. Dentro de la
implementación de `run_inner_loop(...)` va exactamente el código que hoy vive en
`Orchestrator._conducir_onboarding`: abrir/reutilizar la `Session` interna,
`await inner.send(...)`, iterar, observar cada turno, correr la evaluación, mutar el
estado. La sesión interna **sigue siendo una `Session` separada conducida por
nosotros**, tal como en la Forma A. Lo único que cambia respecto a hoy es **quién
decide invocarla**: antes un `if fase == BOOTSTRAPPING`; ahora el juicio del líder
llamando a la herramienta.

### 3.2 Contraste explícito

```
Subagente NATIVO del SDK (RECHAZADO — rompe D-021)
  líder --(Task tool del SDK)--> [SDK abre y corre otra sesión, fuera de nuestro
                                  alcance] --> devuelve SOLO el resultado final
  Nosotros NO vemos: turnos intermedios, archivos leídos, tokens, razonamiento.

Herramienta EN-PROCESO (ELEGIDO — conserva D-021)
  líder --(tool run_inner_loop)--> NUESTRA función Python -->
      conduce la Session interna, observa cada turno, muta estado --> devuelve resumen
  Nosotros vemos TODO: la observabilidad vive en código nuestro, no depende del líder.
```

La observabilidad no depende del líder para nada: vive en la implementación Python
de la herramienta, que es casi literalmente `_conducir_onboarding` de hoy envuelto
como función-herramienta.

---

## 4. Flujo end-to-end rediseñado (la prueba real, paso a paso)

Mapea 1:1 con la prueba que hoy se corre con `sda start`. Se marca **quién actúa**,
**qué escribe el humano**, y **qué toca en disco**.

### Paso 0 — Arranque
- **Humano (terminal):** `sda start` en la carpeta del proyecto.
- **Python determinista (antes del LLM):** `bootstrap()` crea `_context/`,
  `_templates/`, `_prototype/`, `_persistence/`, el stub `_context/scope.md`, la
  plantilla, y `_harness_state.json` con `phase=BOOTSTRAPPING`.
- **Líder (Opus+high) se despierta:** lee el estado y saluda en lenguaje natural,
  pidiéndole al humano que edite `_context/scope.md` y avise al terminar.

### Paso 1 — El humano llena el scope
- **Humano (en su editor, no en la terminal):** escribe sus ideas en
  `_context/scope.md` y guarda.
- **Humano (terminal):** avisa en lenguaje natural (p. ej. *"ya terminé, sigue"*).
  No requiere la palabra exacta `listo` (mejora sobre D-022; ver §7).
- **Líder:** antes de lanzar nada, llama a la herramienta determinista
  `scope_esta_lleno()`. Si está vacío, lo dice y espera; si está lleno, avanza.

### Paso 2 — El líder invoca el bucle interno (trabaja el `onboarding-reader`)
- **Líder:** llama a `run_inner_loop(instruction=…)`.
- **Herramienta (Python, observable):**
  1. Pone `transaction_lock=true`, `active_repl=INTERNAL`,
     `active_subagent=onboarding-reader` (determinista, no lo decide el LLM).
  2. Abre/reutiliza la `Session` interna del `onboarding-reader` (Sonnet+high) y le
     manda la instrucción. **Observamos cada turno.**
- **`onboarding-reader`:** lee `_context/scope.md` y la plantilla, explora el
  proyecto, escribe `_prototype/document-extract.md`, devuelve resumen ejecutivo.
- **Herramienta (Python):** corre `evaluate_draft()` (auditoría ciega, D-005; hoy
  stub, T-011). Si no pasa, re-conduce al `onboarding-reader` con el feedback **sin
  molestar al humano**. Al pasar: frontmatter `estado=PENDING_REVIEW`,
  `transaction_lock=false`, `active_repl=EXTERNAL`, `phase=HUMAN_REVIEW`; devuelve el
  resumen al líder.
- **Humano:** no escribe nada; solo ve mensajes de progreso.

### Paso 3 — Puerta de aprobación humana
- **Líder:** presenta el borrador al humano con su propia redacción.
- **Humano (editor):** revisa `_prototype/document-extract.md`.
- **Humano (terminal):** responde en lenguaje natural:
  - **Camino A (rechaza con feedback):** el líder vuelve a llamar
    `run_inner_loop(instruction="ajusta SOLO: …")`. La **misma sesión interna sigue
    viva** y conserva el contexto. Se repite el Paso 3.
  - **Camino B (aprueba):** el líder llama `promote_to_approved()`.
- **Herramienta `promote_to_approved()` (determinista, el gate):** **solo puede
  ejecutarse tras input humano real**; el líder no puede auto-aprobar. Marca
  frontmatter `estado=APPROVED`, `confirmado_por_humano=si`, bloquea el archivo,
  sincroniza `_persistence/progress.md`, cierra la sesión interna, pone
  `phase=READY_FOR_WORK`.

### Paso 4 — Cierre y documento final
- **Líder:** rinde cuentas al humano (documento aprobado, proyecto listo).
- **Disco:** `_prototype/document-extract.md` (APPROVED) · `_persistence/progress.md`
  (onboarding completado) · `_harness_state.json` (`READY_FOR_WORK`, lock=false).

### Resumen "quién escribe qué"

| Momento | Humano escribe (terminal) | Líder (Opus) | `onboarding-reader` (Sonnet) |
|---|---|---|---|
| 0 | `sda start` | saluda, pide scope | — |
| 1 | *"ya terminé"* (natural) | verifica scope vía tool | — |
| 2 | *(nada)* | `run_inner_loop` | **lee y escribe el extract** |
| 3A | *"falta X…"* | re-`run_inner_loop` | **corrige el extract** |
| 3B | *"apruébalo"* | `promote_to_approved` | — |
| 4 | *(nada)* | rinde cuentas | — |

Las **dos únicas** cosas que el humano teclea en la terminal son: un "ya terminé"
tras llenar el scope, y un "apruebo"/"corrige esto" en la puerta.

---

## 5. Contrato de las herramientas del líder

Las herramientas son el **límite de seguridad** entre el juicio del LLM y los
efectos deterministas. El líder solo puede afectar el estado del harness a través de
ellas. Contrato propuesto (nombres provisionales):

| Herramienta | Entrada | Efecto determinista (Python) | Devuelve al líder |
|---|---|---|---|
| `scope_esta_lleno` | — | ninguno (solo lee) | `true`/`false` |
| `run_inner_loop` | `instruction: str` | pone lock/estado INTERNAL; conduce y **observa** la sesión interna; corre eval; al terminar deja `PENDING_REVIEW`, libera lock, `phase=HUMAN_REVIEW` | resumen ejecutivo del `onboarding-reader` |
| `promote_to_approved` | — (solo válida en `phase=HUMAN_REVIEW` tras turno humano) | frontmatter `APPROVED`, bloqueo del archivo, sync `_persistence/`, cierra sesión interna, `phase=READY_FOR_WORK` | confirmación |
| `leer_estado` (opcional) | — | ninguno | snapshot del `_harness_state.json` |

Invariantes que las herramientas garantizan **independientemente de lo que el LLM
haga o diga**:

1. **El `transaction_lock` se pone antes de la operación larga y se libera después**,
   siempre por la herramienta. Base de la recuperación del Escenario B de `idea.md`.
2. **La promoción del documento es atómica y solo ocurre en `promote_to_approved`.**
   No hay otro camino a `APPROVED`.
3. **`promote_to_approved` rechaza ejecutarse si la fase no es `HUMAN_REVIEW`**, de
   modo que el gate no se puede saltar aunque el líder lo intente.
4. **El SDK solo se importa en `providers/`** (D-010); las herramientas viven en
   `tools/` y no conocen el SDK ni implementan lógica de agentes (D-012).

---

## 6. Impacto en la arquitectura y el código

### 6.1 Módulos afectados

- **`src/sda/orchestrator.py`** — se transforma: de contener el `if/elif` de fases,
  pasa a (a) construir la sesión del líder (system prompt + herramientas + Opus/high),
  (b) exponer el bucle de conversación humano↔líder, y (c) delegar los efectos a las
  herramientas. El grueso de `_conducir_onboarding` **se mueve** a la implementación
  de la herramienta `run_inner_loop`.
- **`src/sda/tools/`** (nuevo, previsto en D-016) — aloja las herramientas en-proceso
  del líder (`run_inner_loop`, `promote_to_approved`, `scope_esta_lleno`). No conoce
  `agents/` (D-012).
- **`src/sda/prompts/`** — nuevo `orchestrator_leader.md`: system prompt del líder
  (rol, cuándo llamar cada herramienta, tono, que **nunca** invente aprobación ni
  toque el estado por fuera de las herramientas).
- **`src/sda/providers/claude_sdk.py`** — debe soportar **registrar herramientas
  en-proceso** en `ClaudeAgentOptions` (además de los `allowed_tools` por nombre que
  ya maneja). Es la principal capacidad nueva a verificar en el SDK.
- **`src/sda/core/`** — el contrato `Provider.create_session` puede necesitar un
  parámetro para pasar herramientas en-proceso (hoy solo acepta `allowed_tools` por
  nombre). A confirmar contra la API del SDK.
- **`src/sda/state.py`** — sin cambios de fondo; sigue siendo el punto único de
  mutación atómica que las herramientas usan.

### 6.2 Riesgo técnico — VERIFICADO en vivo (spike T-027)

El punto no trivial era **cómo el SDK registra y ejecuta herramientas en-proceso**
(`@tool` / servidor MCP en-proceso) manteniendo la autenticación por suscripción
(A-001) y el modo no interactivo (`bypassPermissions`, C-002).

**Resultado (2026-07-24, `spikes/t027_herramienta_en_proceso.py`, verde):** bajo
suscripción + `bypassPermissions`, un líder **Opus+high** invocó una herramienta
en-proceso cuya implementación Python **condujo una segunda `Session`** (bucle
interno, **Sonnet+high**) de forma **observable turno a turno**, y su resultado
regresó al líder. La prueba usó un **token aleatorio** producido por el bucle
interno: como el líder solo pudo reportarlo llamando la herramienta, queda
descartado que lo adivinara. Se confirma así el mecanismo de D-027 (la herramienta
como puerta de vuelta a nuestro código) preservando la observabilidad de D-021.

**API confirmado del SDK** (`claude_agent_sdk` 0.2.126):

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("run_inner_loop", "…", {"instruction": str})
async def run_inner_loop(args: dict) -> dict:
    # ← código Python nuestro: aquí se conduce y observa la Session interna
    return {"content": [{"type": "text", "text": "…resumen…"}]}

server = create_sdk_mcp_server("harness", tools=[run_inner_loop])
options = ClaudeAgentOptions(
    mcp_servers={"harness": server},
    allowed_tools=["mcp__harness__run_inner_loop"],   # naming: mcp__<server>__<tool>
    # + model="opus", effort="high", permission_mode="bypassPermissions", env=_subscription_env()
)
```

Hallazgo adicional verificado: **es seguro abrir y conducir un `ClaudeSDKClient`
anidado (el bucle interno) desde dentro del callback de la herramienta del líder** —
el subproceso anidado del CLI convive con el del líder sin conflicto. Este era el
riesgo más fino y quedó despejado.

**Nota de nomenclatura del contrato (§5):** el nombre real de la herramienta ante el
modelo es `mcp__harness__<tool>` (p. ej. `mcp__harness__run_inner_loop`). Los nombres
cortos de §5 son la referencia conceptual.

---

## 7. Decisiones que este diseño propone (para registrar en `decisions.md`)

> Se listan como **propuestas**; su registro formal (numeración D-026+) lo hará el
> `session-closer`.

- **D-026 (propuesta) — El `orchestrator-leader` es un agente LLM (Opus+high) que
  lidera el bucle externo, bajo el principio "el LLM decide / las herramientas hacen
  cumplir".** El LLM conduce la conversación y las decisiones de orquestación; los
  efectos peligrosos (estado, lock, gate) son efectos laterales deterministas de
  herramientas en-proceso. Reemplaza el `if/elif` de fases de `orchestrator.py`.
- **D-027 (propuesta) — El bucle interno se invoca vía herramienta en-proceso
  (`run_inner_loop`), no vía subagente nativo del SDK.** Es la forma de reconciliar
  "agente que lidera" con la observabilidad turno-a-turno de D-021: la herramienta es
  una puerta de vuelta a nuestro código, que conduce y observa la `Session` interna.
- **D-028 (propuesta) — La puerta de aprobación es un límite forzado por
  herramienta.** Solo `promote_to_approved` lleva a `APPROVED`, solo es válida en
  `phase=HUMAN_REVIEW` y solo tras un turno humano; el líder no puede auto-aprobar.
- **D-029 (propuesta) — La señal humana de "continuar" pasa de palabra exacta a
  intención en lenguaje natural, validada por herramienta.** Matiza D-022: el líder
  interpreta la intención ("ya terminé"), pero la precondición real la verifica
  `scope_esta_lleno()` (Python). Se conserva el espíritu de D-022 (no adivinar por
  watcher de archivo) trasladando la verificación dura a una herramienta determinista.

---

## 8. Cómo esto generaliza a los agentes futuros

Este diseño es la **plantilla** para sumar agentes al doble bucle (entrevistador,
planificador, trabajador, etc.). El patrón reutilizable:

1. **Un solo líder conversacional** (el `orchestrator-leader`) es el único que habla
   con el humano (D-002). Los demás agentes son **bucles internos** que el líder
   invoca vía herramientas en-proceso.
2. **Cada agente nuevo = una `Session` interna conducida por una herramienta
   `run_*_loop`** análoga a `run_inner_loop`. Se hereda gratis la observabilidad
   (D-021) y la asignación de modelo/effort por-agente (T-026: `model`/`effort` en
   `create_session`).
3. **Todo efecto sobre el estado o los entregables pasa por una herramienta
   determinista.** Ningún agente escribe `_harness_state.json` ni promueve archivos
   con un `Write` genérico. Las fases nuevas (`INTERVIEW`, `PLANNING`, …) se agregan
   en `state.py` y se protegen con precondiciones en las herramientas, igual que
   `promote_to_approved` protege el gate.
4. **La evaluación sigue siendo un agente/juez aparte** (D-005), invocado dentro de
   cada `run_*_loop`, no fusionado con el agente que produce el trabajo.
5. **El costo se gobierna por-agente:** Opus+high solo para el líder; Sonnet u otros
   para los bucles internos según la tarea (D-025). El líder es el único componente
   Opus persistente, así que su costo por turno (§9) es el que hay que vigilar.

En una frase: **el líder + sus herramientas son un chasis; cada agente futuro se
enchufa como un bucle interno detrás de una herramienta, sin volver a decidir la
arquitectura.**

---

## 9. Riesgos y trade-offs abiertos

- **Costo/latencia:** hoy teclear `listo`/`aprobar` es gratis (regex en Python). Con
  el líder-agente, **cada turno del humano es una inferencia Opus+high**. Un
  onboarding con varios rechazos se encarece. Mitigación a decidir: cortocircuitar en
  Python comandos triviales, o usar un modelo más barato para el "routing" del turno.
- **No determinismo en la capa de control:** se acota manteniendo estado, lock y gate
  como efectos deterministas de herramientas (§2, §5), pero la *decisión* de cuándo
  avanzar queda en el LLM. Aceptable porque las precondiciones duras las validan las
  herramientas.
- ~~**Dependencia de una capacidad del SDK aún no verificada**~~ **Resuelto:** el
  spike de §6.2 (T-027) verificó en vivo herramientas en-proceso bajo suscripción +
  modo no interactivo, incluida la conducción de una `Session` anidada. Ya no es un
  riesgo abierto.

---

## 10. Próximos pasos sugeridos (no incluidos en este análisis)

1. ~~**Spike** de herramienta en-proceso bajo el SDK con suscripción (§6.2)~~
   **HECHO (2026-07-24, verde):** `spikes/t027_herramienta_en_proceso.py`. El
   mecanismo quedó verificado; la implementación del rediseño ya no tiene bloqueo
   técnico conocido.
2. Implementar `tools/` + `prompts/orchestrator_leader.md` + refactor de
   `orchestrator.py` (mover `_conducir_onboarding` a la herramienta `run_inner_loop`).
3. Prueba end-to-end en vivo del flujo de §4, análoga a T-025.
4. Registrar D-026…D-029 (o su forma final) en `decisions.md` vía `session-closer`.

Si el diseño o el spike no convencen, la rama `t-027-sesion-lider` se descarta sin
tocar `master`.
