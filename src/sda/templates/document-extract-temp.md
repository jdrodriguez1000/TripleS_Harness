<!-- =========================================================================
document-extract-temp.md — PLANTILLA del EXTRACTO del scope del cliente
---------------------------------------------------------------------------
Artefacto de TRABAJO (intermedio) de la fase de Prototipado. Lo PRODUCE el
onboarding-reader a partir de _context/scope.md (el documento donde el humano
describe, en ideas generales, lo que quiere construir), ANTES de la entrevista.

PARA QUÉ SIRVE: es el insumo del siguiente agente, el ENTREVISTADOR. La tabla de
COBERTURA le dice qué áreas ya tienen material para que pregunte SOLO los huecos
y NO repregunte lo que el cliente ya escribió en scope.md.

REGLA DE ORO: se CITA, no se interpreta. Cada área se rellena con extractos
TEXTUALES de scope.md (entre comillas, con su localización). Clasificar actores,
redactar el camino feliz o formalizar el Gatekeeper es trabajo de agentes
posteriores, NO de este artefacto. La única inferencia permitida aquí es binaria:
"¿esta área tiene material en scope.md, sí o no?".

Se instancia en _prototype/document-extract.md. Sustituye los <marcadores> y
BORRA estos comentarios al instanciar.
========================================================================= -->

---
estado: DRAFT                       # DRAFT | PENDING_REVIEW | APPROVED
documento_origen: _context/scope.md
extraido_por: onboarding-reader
fecha: <YYYY-MM-DD>
confirmado_por_humano: no           # no -> si (escritura POSTERIOR, solo tras aprobacion humana)
---

# Extracto del scope del cliente — <nombre-del-proyecto | no declarado>

## Cobertura

<!-- TABLA DE CONTROL. Es lo primero que lee el entrevistador: le dice qué
     preguntar y qué NO repreguntar. Estado de cada área:
       - cubierta — scope.md trae material suficiente; el entrevistador NO pregunta.
       - parcial  — hay material pero incompleto; pregunta SOLO lo que falta
                    (detállalo en "Qué falta").
       - ausente  — scope.md no dice nada Y DEBERÍA decirlo; el entrevistador
                    pregunta el área completa.
       - n/a      — el área NO se le pide al cliente por diseño; no se pregunta.
     Ante la duda, marca PARCIAL o AUSENTE: repreguntar de más cuesta una
     pregunta; dar por cubierto de menos mete un hueco silencioso. -->

| Área | Tema                                   | Estado                              | Qué falta (si parcial) |
|------|----------------------------------------|-------------------------------------|------------------------|
| §1   | Objetivo y contexto                    | <cubierta \| parcial \| ausente>    | <… o —>                |
| §2   | Hipótesis de valor central             | <…>                                 | <…>                    |
| §3   | Tipo de prototipo dominante            | n/a                                 | lo deduce el sistema, no el cliente |
| §4   | Stakeholders                           | <…>                                 | <…>                    |
| §5   | Actores                                | <…>                                 | <…>                    |
| §6   | Camino feliz + medio por actor         | <…>                                 | <…>                    |
| §7   | Gatekeeper (métrica+umbral+medición)   | <…>                                 | <…>                    |
| §8   | Timebox                                | <…>                                 | <…>                    |
| §9   | Exclusiones                            | <…>                                 | <…>                    |
| §10  | Split por audiencia (opcional)         | <…>                                 | <…>                    |

## Extractos por área

<!-- Una subsección por cada área con estado "cubierta" o "parcial". Las áreas
     "ausente" o "n/a" se OMITEN aquí (ya constan en la tabla). Cada extracto es
     una CITA TEXTUAL de scope.md con su localización, para que el dato sea
     trazable hasta la fuente. Si un área tiene varias citas, añádelas todas:
     sobre-citar es preferible a resumir (resumir = interpretar). -->

### §1 — Objetivo y contexto

> "<cita textual de scope.md>"
> — <localización, p. ej. párrafo 2>

### §2 — Hipótesis de valor central

> "<cita textual>"
> — <localización>

<!-- ...continuar con las áreas que tengan material (§4 … §10). -->

## Ambigüedades y contradicciones detectadas

<!-- Puntos donde scope.md dice algo CONTRADICTORIO, VAGO o AMBIGUO. NO los
     resuelvas: se pasan al entrevistador para que los aclare con el humano. -->

| #  | Área | Qué dice el scope           | Por qué es problemático                    |
|----|------|-----------------------------|--------------------------------------------|
| A1 | <§n> | <cita o paráfrasis mínima>  | <contradicción / vaguedad / doble lectura> |

## Fuera del alcance del extracto

<!-- Material de scope.md que NO mapea a ninguna área §1–§10 (p. ej. presupuesto,
     calendario comercial, cláusulas, anexos). Se lista para dejar constancia de
     que se leyó y se descartó CONSCIENTEMENTE. Si no hay nada, escribe "ninguno". -->

- <tema de scope.md que no alimenta el descubrimiento, o "ninguno">
