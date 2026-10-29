# Base de datos — APP Malato

Esquema PostgreSQL 15+ del sistema de gestión de la tienda: **monolito modular**, un
esquema por módulo, comunicación entre módulos por eventos (nunca por FK cruzada).

## Requisitos

- PostgreSQL **15 o superior** (`ltree`, `citext`, `pgcrypto` vienen con el servidor).
- Un usuario con permiso para crear esquemas, tipos, tablas, índices y triggers.
- Codificación UTF-8 (los comentarios y datos están en castellano).

## Estructura

```
db/
  init/
    000_extensions_and_schemas.sql   extensiones + esquemas (idempotente)
    001_util_functions.sql           funciones de trigger compartidas
  seed/
    001_demo_store.sql               datos de demostración (idempotente)
packages/
  core/migrations/001_core_init.sql               core
  module-catalog/migrations/001_catalog_init.sql  catalog
  module-inventory/…/001_inventory_init.sql       inventory
  module-orders/…/001_orders_init.sql             orders
  module-tasks/…/001_tasks_init.sql               tasks + rules
  module-pos/…/001_pos_init.sql                   pos
  module-notify/…/001_notify_init.sql             notify
  module-analytics/…/001_analytics_init.sql       analytics
```

Esquemas: `util`, `core`, `catalog`, `inventory`, `orders`, `tasks`, `rules`, `pos`,
`notify`, `analytics`. El esquema `rules` (motor ECA) es un subesquema del módulo de
tareas, que es su propietario.

## Orden exacto de ejecución

El orden importa: los esquemas y las funciones de trigger deben existir antes de las
migraciones, y las migraciones antes del seed.

```bash
createdb malato

psql -v ON_ERROR_STOP=1 -d malato -f db/init/000_extensions_and_schemas.sql
psql -v ON_ERROR_STOP=1 -d malato -f db/init/001_util_functions.sql

psql -v ON_ERROR_STOP=1 -d malato -f packages/core/migrations/001_core_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-catalog/migrations/001_catalog_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-inventory/migrations/001_inventory_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-orders/migrations/001_orders_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-tasks/migrations/001_tasks_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-pos/migrations/001_pos_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-notify/migrations/001_notify_init.sql
psql -v ON_ERROR_STOP=1 -d malato -f packages/module-analytics/migrations/001_analytics_init.sql

psql -v ON_ERROR_STOP=1 -d malato -f db/seed/001_demo_store.sql
```

En una sola pasada, respetando ese orden (el `sort` mantiene `db/init` antes de
`db/seed`, y `core` antes que el resto por orden alfabético de `packages/`):

```bash
find db/init packages db/seed -name '*.sql' | sort | xargs -I{} psql -v ON_ERROR_STOP=1 -d malato -f {}
```

Comprobar el resultado:

```bash
psql -d malato -c "\dn"                                     # esquemas
psql -d malato -c "\dt core.*"                              # tablas del núcleo
psql -d malato -c "select count(*) from catalog.products"   # 30 productos
psql -d malato -c "select code, is_active from rules.rules order by priority"
```

## Idempotencia

- `db/init/*` usa `CREATE ... IF NOT EXISTS`.
- El seed se puede ejecutar varias veces sin duplicar datos: combina
  `ON CONFLICT DO NOTHING` (donde hay índice único de negocio) con guardas
  `WHERE NOT EXISTS` (donde la unicidad sería una regla de negocio falsa, como los
  lotes o los cobros). Está envuelto en una única transacción.

## Cómo añadir un módulo nuevo

**Sin tocar el núcleo.** Estos son todos los pasos:

1. Crear la carpeta `packages/module-<nombre>/migrations/`.
2. En la primera migración, `CREATE SCHEMA IF NOT EXISTS <nombre>;` y a continuación
   sus tablas. Nunca crear FK hacia otro esquema: usar `uuid` suelto con un comentario
   `-- referencia blanda a <esquema>.<tabla>`.
3. Añadir `store_id uuid NOT NULL` a toda tabla operativa, y `created_at`/`updated_at`
   con `CREATE TRIGGER ... EXECUTE FUNCTION util.set_updated_at();` en cada tabla con
   `updated_at`.
4. Si la tabla es un histórico, hacerla *append-only*:
   `REVOKE UPDATE, DELETE ON <esquema>.<tabla> FROM PUBLIC;` más un trigger
   `BEFORE UPDATE OR DELETE ... EXECUTE FUNCTION util.forbid_mutation();`.
5. Escribir su `manifest.ts` (permisos, eventos que publica y consume, `facts` y
   `actions` que aporta al motor de reglas, rutas de UI y feature flags). El motor de
   reglas descubre las nuevas variables y acciones por ese manifiesto, sin cambios en
   el núcleo.
6. Registrar el esquema nuevo en `db/init/000_extensions_and_schemas.sql` (solo el
   `CREATE SCHEMA IF NOT EXISTS`, para que las instalaciones nuevas lo tengan).
7. Añadir la ruta del fichero al orden de ejecución de este README y al script de
   despliegue.

Prohibido: importar código de otro módulo desde `domain/`, o leer tablas de otro
esquema directamente. La comunicación es por eventos de dominio (`core.outbox_events`)
o por puertos declarados en `packages/contracts`.

## Aviso importante sobre el hash del PIN del seed

`db/seed/001_demo_store.sql` inserta `core.users.pin_caja` con un valor **simbólico**
del tipo `$argon2id$SEED_PLACEHOLDER$operadora1-4567`. Es deliberado:

- El seed **no permite iniciar sesión**. Es un marcador de posición para que el modelo
  de datos sea legible.
- El hash real debe generarlo la aplicación con **argon2id** (recomendado) o bcrypt en
  el alta de usuario, y **nunca** se almacena el PIN en claro.
- Antes de cualquier entorno real hay que regenerar los PIN de los 6 usuarios:

```sql
-- Ejemplo de sustitución (el hash debe venir de la app, no de SQL)
UPDATE core.users
   SET pin_caja = '<hash argon2id generado por la aplicación>'
 WHERE email = 'sala1@malato.es';
```

- `core.users.pin_caja` **no tiene índice único**: argon2 incorpora salt aleatorio, así
  que el mismo PIN produce hashes distintos y la unicidad no es verificable en la base
  de datos. Si el negocio exige PIN único por tienda, hay que validarlo en la aplicación
  o guardar además un HMAC determinista del PIN.

## Validación de los scripts

`.tools/validate-sql.mjs` comprueba la sintaxis con el parser oficial de PostgreSQL
(libpg-query, compilado a WASM, versión 18). `.tools/validate-semantics.mjs` construye
el catálogo de objetos recorriendo el árbol sintáctico y verifica referencias entre
ficheros en el orden real de ejecución: esquemas y tipos creados antes de usarse, FK a
tablas y columnas existentes, índices y CHECK sobre columnas existentes, tablas citadas
en `FROM`/`JOIN`, y columnas `NOT NULL` sin `DEFAULT` cubiertas en cada `INSERT`.

```bash
node .tools/validate-sql.mjs
node .tools/validate-semantics.mjs
```

## Convenciones del modelo

| Convención | Detalle |
|---|---|
| PK | `uuid DEFAULT gen_random_uuid()`; PK compuesta en tablas de unión |
| Timestamps | `created_at` / `updated_at` `timestamptz NOT NULL DEFAULT now()` |
| Estados | `ENUM` nativo cuando la lista es estable; tabla catálogo si va a crecer |
| FK | Solo dentro del mismo esquema; entre módulos, `uuid` sin FK |
| Borrado | Lógico con `deleted_at`; los históricos son append-only |
| JSONB | Configuración variable (condiciones y acciones de reglas, atributos de producto). Índices GIN donde se consulta |
