# Arquitectura de módulos

Este documento describe el contrato que hace que el sistema sea un **producto vivo**: añadir,
quitar o modificar funcionalidad sin tocar el núcleo.

## El principio

Solo tres cosas viven en `packages/core`:

1. **Registro de módulos** — sabe qué módulos hay y qué aporta cada uno.
2. **Bus de eventos** — transporta hechos consumados entre módulos.
3. **Motor de reglas** — evalúa condiciones y ejecuta acciones, sin saber de negocio.

Todo lo demás es un plugin. Un módulo **nunca** importa a otro módulo: se comunican por
eventos o por puertos declarados en `packages/contracts`.

## Anatomía de un módulo

```
packages/module-X/
├── src/
│   ├── manifest.ts        el contrato: qué aporta el módulo al sistema
│   ├── X.service.ts       la lógica de negocio
│   ├── domain/            (si aplica) entidades e invariantes, sin framework
│   ├── actions/           acciones que aporta al motor de reglas
│   └── subscribers/       handlers de eventos de otros módulos
└── migrations/            su propio esquema SQL (si tiene tablas)
```

## El manifiesto

Es la pieza central. Declara todo lo que el módulo aporta, y el núcleo lo consume **sin
conocer el módulo**:

| Campo | Qué es | Quién lo consume |
|---|---|---|
| `id`, `name`, `version` | Identidad y versionado independiente | el registro |
| `permissions` | Permisos granulares por acción | RBAC y el guard de rutas |
| `publishes` | Eventos que emite (en pasado) | el bus y la auditoría |
| `consumes` | Eventos que escucha | el registro (para avisar de huérfanos) |
| `facts` | Variables que aporta al motor de reglas | el editor de reglas y el evaluador |
| `actions` | Acciones que aporta al motor de reglas | el motor |
| `uiRoutes` | Entradas de navegación y qué roles las ven | la shell web |
| `featureFlags` | Interruptores sin desplegar | el host |
| `migrationsPath` | Ruta a su SQL. **Opcional**: sin tablas, no se declara | el runner de migraciones |

## Catálogo de eventos (real, extraído de los manifiestos)

| Módulo | Publica | Consume |
|---|---|---|
| `tasks` | `task.created`, `task.assigned`, `task.reassigned`, `task.started`, `task.blocked`, `task.completed`, `task.cancelled`, `task.overdue` | `stock.below_minimum`, `lot.expiring_soon` |
| `inventory` | `stock.below_minimum`, `lot.expiring_soon`, `wastage.registered` | `sale.completed`, `reception.completed` |
| `pos` | `cash_session.opened`, `cash_session.closed`, `cash_session.discrepancy`, `sale.completed` | — |
| `notify` | `notification.sent` | — |
| `store-context` | — | — |
| `healthcheck` | — | — |

**Convención:** los eventos se nombran en **pasado** y en formato `modulo.entidad_accion`.
Nunca se emite una intención (`task.assign`), se emite el hecho (`task.assigned`): así un
módulo nuevo puede suscribirse a la historia sin pedir permiso a nadie.

**Huérfano conocido y aceptado:** `inventory` consume `reception.completed`, que todavía no
publica nadie porque el módulo de pedidos no existe en el Bloque 0. Un test lo comprueba
explícitamente, de modo que cualquier otro huérfano hace fallar la build.

## Variables y acciones del motor de reglas

El motor no conoce ningún módulo: solo resuelve claves y ejecuta tipos.

| Módulo | Facts que aporta |
|---|---|
| `inventory` | `inventory.stock_ratio`, `inventory.days_to_expiry`, `inventory.lot_qty` |
| `tasks` | `tasks.open_by_user`, `tasks.minutes_overdue`, `tasks.status` |
| `pos` | `pos.cash_difference_abs`, `pos.affluence` |
| `store-context` | `calendar.weekday`, `calendar.time_window`, `store.affluence`, `store.affluence_forecast` |
| `healthcheck` | `healthcheck.uptime_seconds` |

| Módulo | Actions que aporta |
|---|---|
| `tasks` | `CREATE_TASK`, `REASSIGN_TASK`, `CANCEL_TASK` |
| `notify` | `NOTIFY` |

### Contrato de un `FactResolver` (importante)

```ts
type FactResolver = (params, ctx) => unknown | Promise<unknown>;
```

**El resolver devuelve el valor crudo.** El sobre `{ found, value }` lo pone `FactRegistry`
en un único sitio.

- Si no hay dato: devuelve **`null`** (el evaluador lo trata como no coincidente).
- Si el fact no lo registra nadie, el registro devuelve `found: false` por su cuenta. Esa
  distinción permite avisar de un error de configuración sin confundirlo con una ausencia
  temporal de dato.

Si un resolver devuelve el sobre ya formado, se envuelve dos veces, **ninguna comparación
coincide y el motor entero queda muerto en silencio**. `FactRegistry` detecta ese caso y
lanza `MiswrappedFactError` en lugar de fallar sin avisar.

## Formato de una regla ECA

Las reglas viven en `rules.rules` como JSONB (ver `db/README.md`). Ejemplo real del seed:

```json
{
  "all": [
    { "fact": "calendar.weekday", "op": "eq", "value": "MONDAY" },
    { "fact": "store.affluence", "op": "eq", "value": "LOW" },
    { "fact": "inventory.stock_ratio", "op": "lt", "value": 0.30,
      "params": { "categoryPath": "lacteos" } }
  ]
}
```

```json
[
  { "type": "CREATE_TASK", "params": {
      "template_code": "REPOSICION_PRIORITARIA",
      "assignee_strategy": "LEAST_LOADED",
      "role": "OPERADORA", "priority": "ALTA", "due_in_minutes": 30 } },
  { "type": "NOTIFY", "params": {
      "target": "ROLE", "role": "COORDINADORA", "severity": "AVISO" } }
]
```

Por qué **JSONB y no EAV**: la condición es un documento anidado. Con EAV habría que
reconstruir el árbol con N joins en cada evaluación; con JSONB se valida contra un esquema,
se versiona entero y se evalúa en memoria. `rule_executions` guarda la **versión** de la
regla usada, para poder auditar decisiones históricas aunque la regla haya cambiado.

**Atención a `"role"` en las acciones: es el rol MÍNIMO, no el exclusivo.** Los roles son
jerárquicos (`core.roles.level`: GERENCIA 30 > COORDINADORA 20 > OPERADORA 10), y `LEAST_LOADED`
reparte entre todas las personas **asignables** de la tienda cuyo nivel sea mayor o igual. En el
ejemplo, `"role": "OPERADORA"` no significa «solo operadoras»: son las **5 personas de sala**
—2 operadoras y 3 coordinadoras—, porque quien coordina también repone y cobra. Gerencia queda
fuera del reparto (`assignable: false`): no opera en tienda y, al tener el nivel más alto,
entraría en todas las tareas.

Grupos soportados: `all`, `any`, `not`. Operadores: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`,
`in`, `nin`, `contains`, `exists`, `is_null`.

La traza de cada evaluación explica **por qué** coincidió o no cada variable. Sin esa traza,
una regla que no dispara es un misterio irresoluble para gerencia.

## Garantías del bus de eventos

```
[Comando] → transacción: escribe estado + inserta en outbox → COMMIT
                                  ↓
                        [Relay] lee el outbox
                  ┌───────────────┴───────────────┐
                  ↓                               ↓
          Motor de reglas                 Suscriptores de otros módulos
          (facts + evaluación)            (idempotentes por eventId)
```

- **Atomicidad:** nunca hay cambio de estado sin evento, ni evento sin cambio.
- **Entrega al menos una vez** → los handlers **deben** ser idempotentes (clave: `eventId`).
- **Reintentos con backoff** y dead-letter queue.
- **Reprocesable:** las proyecciones (KPIs) se pueden reconstruir reproduciendo el outbox.

## Las 6 reglas de frontera

Codificadas en `tools/check-boundaries.mjs`, rompen la build si se violan:

| # | Regla |
|---|---|
| R1 | Un `module-*` no importa de otro `module-*` |
| R2 | Un módulo solo importa de `contracts`, `core`, `ui` y lo suyo |
| R3 | `domain/` no importa `infrastructure/`, `api/` ni frameworks |
| R4 | Nada importa de `apps/` |
| R5 | `packages/core` no importa de ningún `module-*` |
| R6 | `apps/api/src` solo contiene `main.ts`, `composition-root.ts`, `http/`, `controllers/` y `adapters/` |

R6 es la que impide que el host absorba el dominio por acumulación. Sin ella, la forma
natural de trabajar es meter lógica en el host "solo por esta vez", y en seis meses los
manifiestos son decorativos.

## Cómo añadir un módulo, paso a paso

1. `packages/module-loyalty/src/manifest.ts` con el manifiesto completo.
2. `packages/module-loyalty/src/loyalty.service.ts` con la lógica.
3. `packages/module-loyalty/migrations/001_init.sql` si tiene tablas (y entonces sí,
   declara `migrationsPath`).
4. Una entrada en `apps/api/src/composition-root.ts`.
5. `node tools/check-boundaries.mjs` y `node tools/run-tests.mjs`.

**Ningún fichero de `packages/core` se modifica.** Si al añadir un módulo hay que tocar el
núcleo, la arquitectura ha fallado y hay que arreglarla entonces, no dentro de dos años.

`module-healthcheck` es la prueba viva de esto, y un test comprueba que la palabra
`healthcheck` no aparece en `packages/core`.
