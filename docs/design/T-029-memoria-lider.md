# Diseño T-029 — Memoria del proyecto destino e identidad del líder

**Estado:** implementado y verificado headless (spike `spikes/t029_memoria_lider.py`).
**Fecha:** 2026-07-25
**Rama:** `t-027-sesion-lider`

Este documento cubre dos cosas que llegaron juntas por pedido del usuario y que
resultaron ser una sola: darle al `orchestrator-leader` **memoria del proyecto sobre
el que trabaja** (T-029) y darle **identidad, tono y reglas invariantes**. Un rol de
Project Manager sin bitácora es decorativo; una bitácora sin dueño narrativo no se
mantiene. Se diseñaron y se implementaron a la vez.

---

## 1. Contexto y problema

### 1.1 Qué existía

- `bootstrap.py` creaba la carpeta `_persistence/` **vacía**, contradiciendo `idea.md`
  (Fase 1, Step 2: *"genera las plantillas iniciales en la carpeta `_persistence/`"*).
- El único escritor era `_sincronizar_persistencia()` en `leader_tools.py`: un
  `append` de una línea fija a `progress.md`, que además **creaba** el archivo sin
  cabecera ni estructura.
- El líder tenía `Read/Glob/Grep` sobre el proyecto, pero su system prompt nunca le
  decía que leyera `_persistence/`, y `_mensaje_apertura()` solo le informaba la fase.
- El prompt mezclaba identidad, reglas y el flujo concreto de onboarding en un bloque
  único, sin persona ni rol definidos.

Resultado: el líder arrancaba **amnésico** en cada ejecución. Sabía en qué fase
estaba, nada más.

### 1.2 Qué se quiere

Que el líder, al reanudar días después, sepa qué se hizo, qué se decidió, qué quedó
pendiente y qué se aprendió — y que mantenga eso al día mientras conversa. Y que se
comporte como un rol reconocible y estable, no como un asistente genérico.

### 1.3 Las tensiones centrales

1. **Garantía vs. costo.** Si el líder lee la memoria por su cuenta, la garantía
   depende del modelo y el costo es impredecible. Si se le empuja todo, el costo crece
   sin techo en el componente más caro del sistema (Opus + effort high).
2. **Escritura vs. sandbox.** El líder necesita escribir su bitácora, pero su sandbox
   duro es de solo lectura — y lo es por una razón ya pagada en sangre (T-028/L-013).
3. **Libertad vs. formato.** Un LLM escribiendo Markdown libre produce una bitácora
   que otro LLM no puede volver a parsear de forma fiable.

---

## 2. Decisión de formato: Markdown, superseando D-004

**D-004** decía literalmente: *"no deben unificarse, **ni siquiera en formato**
(900_persistence usa .md, `_persistence` del harness usaría .json)"*. `idea.md`
refuerza con `tasks.json`. La nota de análisis de T-029 recomendaba lo contrario.

**Decisión (usuario, 2026-07-25): Markdown**, con supersesión explícita de D-004 en
lo relativo al formato.

Razones:

- Quien escribe y quien lee son LLMs. Un JSON con esquema rígido es exactamente lo
  que un modelo rompe; el Markdown degrada con elegancia.
- El humano tiene que poder **auditar y corregir la bitácora a mano**, igual que hace
  con `_context/scope.md`. Ese patrón ya está validado en el producto.
- El esquema de `900_persistence/` lleva días funcionando en este mismo repo: tabla
  de índice + bloques de detalle da estructura suficiente sin rigidez.

Lo que D-004 protegía de verdad —que la memoria de **construcción del harness** y la
memoria del **producto** son planos distintos que no se mezclan— se preserva íntegro.
Lo que cambia es solo el formato, que era un detalle de implementación anticipado
antes de tener el producto en la mano.

---

## 3. Lectura: se empuja un digest acotado

**Decisión: híbrido con push acotado.** En cada arranque, Python construye un resumen
determinista de `_persistence/` y lo **pega en el mensaje de apertura** del líder.
`Read` sigue disponible para profundizar.

Las tres opciones evaluadas:

| Opción | Garantía | Costo | Veredicto |
|--------|----------|-------|-----------|
| Pull (el líder lee con `Read`) | Ninguna: puede no leer | 3-4 turnos de Opus antes del primer saludo, archivos enteros | Descartada |
| Push completo | Total | Crece sin techo; acaba desbordando el contexto | Descartada |
| **Push acotado + `Read`** | **Total: el modelo no puede saltárselo** | **Techo fijo (`DIGEST_MAX_CHARS = 4000`)** | **Elegida** |

Composición del digest (`memory.build_digest`):

- **Progreso:** últimas 3 entradas, con el cuerpo aplanado y recortado a 240 caracteres.
- **Tareas:** solo las **abiertas** (`Pendiente`/`En curso`), hasta 10, más el conteo
  total. Una tarea cerrada no gasta espacio del arranque.
- **Decisiones:** últimas 5, solo título y fecha.
- **Lecciones:** últimas 3, solo título y fecha.

Dos propiedades deliberadas:

- **Secciones ausentes, no vacías.** Un proyecto recién sembrado devuelve digest
  vacío (`""`) y el mensaje de apertura no arrastra encabezados huecos. Esto surgió
  como fallo real del spike y se corrigió en el diseño, no en el test.
- **El digest envejece durante la sesión, y no importa:** lo que el líder registra
  después lo conoce por la confirmación que le devuelve cada herramienta.

---

## 4. Escritura: herramientas en-proceso, obligatoriamente

**No es una preferencia de estilo.** El sandbox del líder es
`builtin_tools=["Read","Glob","Grep"]` (`orchestrator.py`), y lo es porque en T-028 se
descubrió en vivo que `allowed_tools` no restringe nada bajo `bypassPermissions`
(L-013). Darle un `Write` genérico para su bitácora **reabriría ese agujero**: podría
escribir `_harness_state.json` o forzar un `APPROVED` saltándose la puerta de
aprobación.

Por tanto la escritura va por `MemoryTools` (`sda/tools/memory_tools.py`), cinco
herramientas que envuelven a `sda/memory.py`:

| Herramienta | Efecto | Cuándo la llama el líder |
|---|---|---|
| `record_progress` | Entrada fechada en `progress.md` | Algo queda terminado o el proyecto cambia de estado |
| `record_task` | Tarea nueva `Pendiente`, código `T-XXX` | Aparece trabajo concreto que no se hace ahora |
| `update_task` | Cambia estado en tabla **y** detalle | En cuanto la tarea cambia, no al final |
| `record_decision` | Entrada `D-XXX` con decisión y razón | Se acuerda algo que cambia el rumbo |
| `record_lesson` | Entrada `L-XXX` con lección y contexto | Algo sale mal, sorprende o revela una preferencia |

Lo que Python garantiza y el modelo no puede alterar:

- **La numeración.** `_siguiente_codigo()` toma el máximo existente **+1** —no la
  cantidad de entradas, para no reutilizar un código ya citado en otro documento si
  alguien borra una a mano. Continuar una secuencia es justo lo que un LLM hace mal.
- **La ruta.** El líder nunca pasa un path: no puede escribir fuera de `_persistence/`.
- **El formato.** Cabeceras, fechas y estructura de bloque las pone la función. Los
  títulos se normalizan a una línea y se les neutralizan las barras verticales, que
  romperían la tabla-índice que el digest vuelve a parsear.
- **La sincronía tabla↔detalle** de `tasks.md`. El índice es lo que el digest lee al
  arrancar; una tabla desfasada dejaría al líder trabajando sobre tareas ya cerradas.
- **La atomicidad.** Mismo criterio que `state.save`: temp + `os.replace`.
- **El rechazo legible.** `MemoriaError` se traduce a `RECHAZADO: <motivo>`, texto
  accionable para el modelo, no una excepción cruda.

Es D-026 aplicado a la memoria: **el LLM decide *qué* merece registrarse; la
herramienta hace cumplir *cómo* se registra.**

---

## 5. Siembra: idempotente y reparadora

`memory.seed()` copia cuatro plantillas empaquetadas
(`src/sda/templates/persistence/*.md`) a `_persistence/`, sin pisar nada existente.

Se invoca desde `bootstrap()` **antes** del corte por reanudación, no después. Esto es
intencional: así también repara los proyectos creados antes de T-029, cuya carpeta
`_persistence/` nació vacía, sin tocar su estado ni su contenido. El contrato de
retorno de `bootstrap()` (`True` = arranque inicial) no cambia.

---

## 6. Identidad, tono y reglas invariantes

### 6.1 Dos capas de nombre

El componente técnico **sigue llamándose `orchestrator-leader`**. Aparece en D-025,
D-026, D-027, D-032, en `docs/design/T-027-*.md`, en `leader_tools.py` y en toda la
bitácora de `900_persistence/`: renombrarlo es un refactor caro y sin beneficio.

Lo que se añade es la **persona de cara al humano**: se presenta como su **Project
Manager**, sin nombre propio (decisión del usuario). Un nombre de pila habría añadido
riesgo de sobre-actuación e invención sin ganancia proporcional.

### 6.2 Estructura del prompt

`prompts/orchestrator_leader.md` pasó de un bloque mezclado a seis secciones, en
orden deliberado:

1. **Identidad** — quién es, a quién sirve, que dirige y no ejecuta.
2. **Reglas que nunca rompes** — siete reglas numeradas e invariantes.
3. **Tono** — cálido, ejecutivo, sin relleno ni adulación; recomienda en vez de
   listar opciones neutras.
4. **La memoria del proyecto** — cómo la recibe al arrancar y con qué criterios la
   escribe.
5. **Tus herramientas** — flujo y memoria.
6. **El flujo que diriges ahora: el onboarding** — la fase concreta.

La clave es que **solo la sección 6 crece** cuando el líder gane fases nuevas
(arquitectura, construcción de features). Identidad, reglas, tono y memoria son
estables. Antes, todo estaba entrelazado y cada fase nueva habría arrastrado lo demás.

### 6.3 Las reglas como contrapeso

Dar identidad a un modelo aumenta el riesgo de que rolee y de que invente para
sostener el personaje. Las reglas 1-3 son el contrapeso explícito: *la verdad la dan
las herramientas, no tu impresión*; *nunca inventas una aprobación*; *nunca inventas
hechos del proyecto*. Las dos primeras ya existían en germen en el prompt anterior; la
tercera es nueva y apunta directamente al riesgo que introduce la bitácora — un dato
inventado ahí contamina **todas** las sesiones futuras, no solo la actual.

---

## 7. Impacto en el código

| Archivo | Cambio |
|---|---|
| `src/sda/memory.py` | **Nuevo.** Siembra, escritores y digest. Todo determinista. |
| `src/sda/tools/memory_tools.py` | **Nuevo.** Las cinco herramientas del líder. |
| `src/sda/templates/persistence/*.md` | **Nuevas.** Cuatro plantillas empaquetadas. |
| `src/sda/tools/__init__.py` | Exporta `MemoryTools`. |
| `src/sda/bootstrap.py` | Siembra la memoria (también en reanudación); `PERSISTENCE_DIR` pasa a definirse en `memory`. |
| `src/sda/tools/leader_tools.py` | `_sincronizar_persistencia()` usa `memory.append_progress` en vez de un `append` crudo. |
| `src/sda/orchestrator.py` | Registra `MemoryTools`; `_mensaje_apertura()` inyecta el digest. |
| `src/sda/prompts/orchestrator_leader.md` | Reescrito con las seis secciones. |
| `pyproject.toml` | `package-data` incluye `templates/persistence/*.md`. |
| `spikes/t029_memoria_lider.py` | **Nuevo.** Verificación headless. |

El apunte automático del hito de onboarding se conserva: ocurre al cruzar la puerta de
aprobación **sí o sí**, sin depender de que el líder decida registrarlo.

---

## 8. Verificación

`spikes/t029_memoria_lider.py`, sin credenciales ni red. Siete comprobaciones, todas
en verde:

1. Un proyecto anterior a T-029 recupera su memoria sin perder su estado.
2. Un proyecto nuevo no arrastra un digest vacío al mensaje de apertura.
3. La siembra es idempotente y respeta lo editado a mano.
4. Numeración correlativa y tabla-índice sincronizada con el detalle.
5. Entradas inválidas rechazadas (tarea inexistente, estado inválido, campos vacíos).
6. El digest muestra lo abierto, oculta lo cerrado y respeta su tope.
7. Las herramientas devuelven confirmación y rechazo legibles.

**Pendiente:** verificación en vivo con `sda start` en una carpeta real. Lo que el
spike no puede cubrir es lo único que queda en manos del modelo: si el líder decide
bien *cuándo* registrar cada cosa, y si el tono nuevo se siente como se pretende.

---

## 9. Decisiones que este diseño propone registrar

- **La memoria del proyecto destino es Markdown**, replicando el esquema de
  `900_persistence/`. Supersede a D-004 **solo en cuanto al formato**; la separación
  de planos que D-004 establece se mantiene intacta. Deja también una desviación
  consciente frente a `idea.md`, que hablaba de `tasks.json`.
- **El conocimiento de la memoria se empuja como digest acotado** en el mensaje de
  apertura, en vez de dejarse a la iniciativa del líder. Garantía total y costo con
  techo fijo en el componente más caro.
- **La escritura de la memoria va por herramientas en-proceso**, nunca por `Write`.
  Consecuencia directa de L-013: el sandbox de solo lectura del líder no es
  negociable.
- **El líder tiene identidad de rol (Project Manager) sin nombre propio**, y su prompt
  se estructura separando lo estable (identidad, reglas, tono, memoria) de lo que
  crece con cada fase (el flujo).

---

## 10. Riesgos y trade-offs abiertos

- **No hay protocolo de cierre en el producto.** Se sale con `salir`/Ctrl+C y no hay
  momento de consolidación. En este repo, `900_persistence/` se mantiene viva porque
  existe un cierre obligatorio; el producto `sda` no tiene equivalente, así que la
  bitácora depende de que el líder registre **durante** la conversación. Se dejó
  explícitamente fuera de alcance por decisión del usuario; queda como tarea aparte y
  es el complemento natural de este diseño.
- **Calibración del "cuándo registrar".** El prompt da criterios, pero el volumen real
  —¿registra de más? ¿de menos?— solo se sabe con uso real. Es lo primero a observar
  en la verificación en vivo.
- **El digest puede quedarse corto en proyectos largos.** Los topes (3/10/5/3) son un
  punto de partida razonable, no un óptimo medido. Si el líder empieza a pedir `Read`
  de forma sistemática al arrancar, es señal de que hay que subirlos.
- **Relación con T-020** (persistir la sesión del SDK, pausada): son complementarias.
  Esta bitácora no depende de garantías del proveedor, sobrevive a cambios de modelo y
  es auditable a mano; T-020 resolvería la memoria conversacional fina, que es otra
  cosa.
