// =====================================================================
// run-schema.mjs · Ejecuta el esquema COMPLETO sobre PostgreSQL real (PGlite/WASM).
//
// No es un validador de sintaxis: esto es PostgreSQL 17 de verdad, en proceso.
// Ejecuta init + migraciones + seed y despues COMPRUEBA COMPORTAMIENTO:
// los tres bugs de negocio que se corrigieron en la Fase 5.2 y la inmutabilidad
// de las tablas append-only.
//
// Uso:  node .tools/pglite/run-schema.mjs      (desde la raiz del repo)
// =====================================================================
import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { PGlite } from '@electric-sql/pglite';
import { ltree } from '@electric-sql/pglite/contrib/ltree';
import { citext } from '@electric-sql/pglite/contrib/citext';
import { pgcrypto } from '@electric-sql/pglite/contrib/pgcrypto';

const ROOT = resolve(import.meta.dirname, '..', '..');

// Orden de ejecucion real (el mismo que documenta db/README.md).
const FICHEROS = [
  'db/init/000_extensions_and_schemas.sql',
  'db/init/001_util_functions.sql',
  'packages/core/migrations/001_core_init.sql',
  'packages/module-catalog/migrations/001_catalog_init.sql',
  'packages/module-inventory/migrations/001_inventory_init.sql',
  'packages/module-orders/migrations/001_orders_init.sql',
  'packages/module-tasks/migrations/001_tasks_init.sql',
  'packages/module-pos/migrations/001_pos_init.sql',
  'packages/module-notify/migrations/001_notify_init.sql',
  'packages/module-analytics/migrations/001_analytics_init.sql',
  'db/seed/001_demo_store.sql',
];

let fallos = 0;

function titulo(t) {
  console.log(`\n=== ${t} ===`);
}

function check(nombre, condicion, detalle = '') {
  if (condicion) {
    console.log(`  ok   ${nombre}`);
  } else {
    fallos++;
    console.log(`  FALLO ${nombre}${detalle ? ` -> ${detalle}` : ''}`);
  }
}

// Comprueba que una operacion DEBE fallar (restriccion, trigger...).
async function debeFallar(db, nombre, sql) {
  try {
    await db.exec(sql);
    fallos++;
    console.log(`  FALLO ${nombre} -> la operacion fue ACEPTADA y deberia haber sido rechazada`);
  } catch (err) {
    console.log(`  ok   ${nombre} -> rechazada: ${String(err.message).split('\n')[0].slice(0, 90)}`);
  }
}

const db = new PGlite({ extensions: { ltree, citext, pgcrypto } });

// ---------------------------------------------------------------------
// FASE A · Ejecucion del esquema
// ---------------------------------------------------------------------
titulo('A · Ejecucion del esquema sobre PostgreSQL real');

let sentenciasOk = 0;
for (const rel of FICHEROS) {
  const sql = readFileSync(join(ROOT, rel), 'utf8');
  try {
    await db.exec(sql);
    sentenciasOk++;
    const n = (sql.match(/;\s*$/gm) ?? []).length;
    console.log(`  ok   ${rel}  (${n} terminadores)`);
  } catch (err) {
    fallos++;
    console.log(`  FALLO ${rel}`);
    console.log(`        ${String(err.message).split('\n').slice(0, 4).join('\n        ')}`);
  }
}
console.log(`\n  ${sentenciasOk}/${FICHEROS.length} ficheros ejecutados sin error`);
console.log(`  version del servidor: ${(await db.query('select version()')).rows[0].version.slice(0, 40)}`);

// ---------------------------------------------------------------------
// FASE B · El esquema existe de verdad
// ---------------------------------------------------------------------
titulo('B · Objetos creados');

// Lista esperada, tabla por tabla. Mejor que un contador: si falta una tabla,
// el mensaje dice CUAL falta en lugar de "hay 35 en vez de 36".
const ESPERADAS = {
  core: ['stores', 'roles', 'permissions', 'role_permissions', 'user_permissions', 'users', 'audit_log', 'outbox_events', 'settings'],
  catalog: ['categories', 'suppliers', 'products', 'product_suppliers'],
  inventory: ['locations', 'stock', 'lots', 'stock_movements', 'wastage'],
  orders: ['purchase_orders', 'purchase_order_lines', 'receptions', 'reception_lines'],
  tasks: ['task_templates', 'tasks', 'task_events'],
  rules: ['rules', 'rule_executions', 'rule_overrides'],
  pos: ['registers', 'cash_sessions', 'sales', 'sale_lines', 'payments'],
  notify: ['notifications', 'notification_subscriptions', 'notification_reads'],
  analytics: ['kpi_snapshots'],
};
const existentes = new Set(
  (await db.query(`select table_schema || '.' || table_name as t from information_schema.tables
                   where table_schema in ('core','catalog','inventory','orders','tasks','rules','pos','notify','analytics')`))
    .rows.map((r) => r.t),
);
let totalEsperadas = 0;
for (const [esquema, nombres] of Object.entries(ESPERADAS)) {
  totalEsperadas += nombres.length;
  const faltan = nombres.filter((n) => !existentes.has(`${esquema}.${n}`));
  console.log(`  ${esquema.padEnd(12)} ${nombres.length} tablas${faltan.length ? `  FALTAN: ${faltan.join(', ')}` : ''}`);
  check(`esquema ${esquema} completo`, faltan.length === 0, `faltan ${faltan.join(', ')}`);
}
check(`${totalEsperadas} tablas declaradas y todas existen`, existentes.size === totalEsperadas,
  `existen ${existentes.size}, se esperaban ${totalEsperadas}`);

const ext = await db.query(`select extname from pg_extension order by 1`);
check('extensiones ltree, citext y pgcrypto activas',
  ['ltree', 'citext', 'pgcrypto'].every((e) => ext.rows.some((r) => r.extname === e)),
  ext.rows.map((r) => r.extname).join(','));

const idx = await db.query(`select count(*)::int as n from pg_indexes where schemaname in ('core','catalog','inventory','orders','tasks','rules','pos','notify','analytics')`);
console.log(`  ${idx.rows[0].n} indices`);

// ---------------------------------------------------------------------
// FASE C · El seed carga datos reales
// ---------------------------------------------------------------------
titulo('C · Datos del seed');

const conteos = [
  ['core.users', 'select count(*)::int n from core.users'],
  ['core.roles', 'select count(*)::int n from core.roles'],
  ['core.permissions', 'select count(*)::int n from core.permissions'],
  ['catalog.products', 'select count(*)::int n from catalog.products'],
  ['catalog.suppliers', 'select count(*)::int n from catalog.suppliers'],
  ['catalog.categories', 'select count(*)::int n from catalog.categories'],
  ['inventory.stock', 'select count(*)::int n from inventory.stock'],
  ['inventory.lots', 'select count(*)::int n from inventory.lots'],
  ['tasks.task_templates', 'select count(*)::int n from tasks.task_templates'],
  ['tasks.tasks', 'select count(*)::int n from tasks.tasks'],
  ['rules.rules', 'select count(*)::int n from rules.rules'],
  ['pos.sales', 'select count(*)::int n from pos.sales'],
  ['notify.notifications', 'select count(*)::int n from notify.notifications'],
];
for (const [nombre, sql] of conteos) {
  const r = await db.query(sql);
  console.log(`  ${nombre.padEnd(24)} ${r.rows[0].n}`);
  check(`${nombre} tiene datos`, r.rows[0].n > 0, 'esta vacio');
}

// Las reglas del seed deben ser JSON valido y con la forma ECA disenada.
const reglas = await db.query(`select code, event_type, condition, actions from rules.rules order by code`);
check('las 5 reglas del seed tienen condicion objeto y acciones array',
  reglas.rows.length === 5 && reglas.rows.every((r) => typeof r.condition === 'object' && Array.isArray(r.actions)),
  `${reglas.rows.length} reglas`);
for (const r of reglas.rows) {
  const acciones = r.actions.map((a) => a.type).join('+');
  console.log(`  ${r.code.padEnd(8)} ${r.event_type.padEnd(22)} -> ${acciones}`);
}

// ---------------------------------------------------------------------
// FASE D · COMPORTAMIENTO: los bugs corregidos siguen corregidos
// ---------------------------------------------------------------------
titulo('D · Comportamiento de las restricciones (los 3 bugs de la Fase 5.2)');

const venta = (await db.query(`select id, store_id from pos.sales limit 1`)).rows[0];

// BUG 1 · dos cobros con el mismo metodo en una venta DEBEN permitirse
// (pago dividido en dos pasadas de tarjeta). Antes habia un UNIQUE que lo impedia.
const reg = (await db.query(`select id from pos.registers limit 1`)).rows[0];
try {
  await db.exec(`
    insert into pos.payments (sale_id, method, amount) values ('${venta.id}', 'TARJETA', 10.00);
    insert into pos.payments (sale_id, method, amount) values ('${venta.id}', 'TARJETA', 5.00);`);
  console.log('  ok   bug 1: dos cobros con el mismo metodo en una venta -> permitido (correcto)');
} catch (err) {
  fallos++;
  console.log(`  FALLO bug 1: se sigue impidiendo el pago dividido -> ${String(err.message).split('\n')[0]}`);
}

// BUG 2 · el ticket es unico POR CAJA, no por tienda: dos cajas pueden emitir el
// mismo numero (sobre todo al reconciliar ventas hechas sin conexion). Antes el
// UNIQUE era (store_id, ticket_number) y la segunda caja fallaba al sincronizar.
const cajas = (await db.query(
  `select distinct register_id from pos.sales union select id from pos.registers order by 1 limit 2`,
)).rows.map((r) => r.register_id);
const operador = (await db.query(`select id from core.users limit 1`)).rows[0].id;
const nuevaVenta = (regId, ticket) => `
  insert into pos.sales (store_id, register_id, ticket_number, operator_id, total)
  values ('${venta.store_id}', '${regId}', '${ticket}', '${operador}', 10.00)`;

if (cajas.length >= 2) {
  try {
    await db.exec(nuevaVenta(cajas[0], 'TEST-DUP-1') + ';' + nuevaVenta(cajas[1], 'TEST-DUP-1'));
    console.log('  ok   bug 2: dos cajas emiten el MISMO numero de ticket -> permitido (correcto)');
  } catch (err) {
    fallos++;
    console.log(`  FALLO bug 2: se sigue impidiendo la numeracion por caja -> ${String(err.message).split('\n')[0]}`);
  }
  await debeFallar(db, 'bug 2b: el MISMO ticket en la MISMA caja si se rechaza',
    nuevaVenta(cajas[0], 'TEST-DUP-1'));
} else {
  console.log(`  ---  bug 2: omitido, el seed solo tiene ${cajas.length} caja(s)`);
}

// BUG 3 · recibir DOS VECES el mismo lote en la misma ubicacion debe permitirse.
try {
  const lote = (await db.query(`select product_id, location_id, batch_code from inventory.lots limit 1`)).rows[0];
  await db.exec(`
    insert into inventory.lots (store_id, product_id, location_id, batch_code, expiry_date, qty, unit_cost)
    values ('${venta.store_id}', '${lote.product_id}', '${lote.location_id}', '${lote.batch_code}',
            current_date + 30, 10, 1.00);`);
  console.log('  ok   bug 3: el mismo lote puede recibirse dos veces en la misma ubicacion');
} catch (err) {
  fallos++;
  console.log(`  FALLO bug 3 -> ${String(err.message).split('\n')[0]}`);
}

// REGLA DE NEGOCIO que SI debe seguir impidiendose: dos sesiones ABIERTAS en la misma caja.
await debeFallar(db, 'una sola sesion de caja ABIERTA por registro', `
  insert into pos.cash_sessions (store_id, register_id, opened_by, opening_float, status)
  values ('${venta.store_id}', '${reg.id}', gen_random_uuid(), 100, 'ABIERTA');
  insert into pos.cash_sessions (store_id, register_id, opened_by, opening_float, status)
  values ('${venta.store_id}', '${reg.id}', gen_random_uuid(), 100, 'ABIERTA');`);

// Inmutabilidad de las tablas append-only.
// OJO: hay que INSERTAR una fila antes de intentar mutarla. Un UPDATE sobre una
// tabla vacia afecta a 0 filas y NO dispara el trigger, asi que daria un falso
// "permitido". Es el error que cometio la primera version de este arnes.
await db.exec(`insert into core.audit_log (module, action) values ('test', 'INSERT_DE_PRUEBA')`);
await debeFallar(db, 'audit_log es inmutable (UPDATE rechazado)',
  `update core.audit_log set action = 'MANIPULADO'`);
await debeFallar(db, 'audit_log es inmutable (DELETE rechazado)',
  `delete from core.audit_log`);

await db.exec(`insert into core.outbox_events (event_type, aggregate_type, payload)
               values ('test.evento', 'test', '{"original":true}'::jsonb)`);
await debeFallar(db, 'outbox: el CONTENIDO del evento es inmutable ante UPDATE',
  `update core.outbox_events set payload = '{"hack":true}'::jsonb`);
await debeFallar(db, 'outbox: el evento no se puede borrar',
  `delete from core.outbox_events`);
// ...pero el relay SI debe poder marcar el estado de entrega. Esto debe PASAR.
try {
  await db.exec(`update core.outbox_events set status = 'PROCESADO', processed_at = now(), retries = 1
                 where event_type = 'test.evento'`);
  console.log('  ok   outbox: el relay SI puede actualizar status/retries/processed_at');
} catch (err) {
  fallos++;
  console.log(`  FALLO outbox: el relay no puede marcar el estado -> ${String(err.message).split('\n')[0]}`);
}

await db.exec(`insert into tasks.task_events (task_id, store_id, type)
               select id, store_id, 'CREADA' from tasks.tasks limit 1`);
await debeFallar(db, 'task_events es inmutable (DELETE rechazado)',
  `delete from tasks.task_events`);

// El CHECK de la forma ECA.
await debeFallar(db, 'una regla con acciones no-array es rechazada', `
  insert into rules.rules (store_id, code, name, event_type, actions)
  values ('${venta.store_id}', 'MALA', 'mala', 'test', '{"no":"es array"}'::jsonb)`);

// ---------------------------------------------------------------------
// FASE E · Idempotencia del seed (segunda ejecucion)
// ---------------------------------------------------------------------
titulo('E · Idempotencia del seed');
const antes = (await db.query(`select count(*)::int n from catalog.products`)).rows[0].n;
try {
  await db.exec(readFileSync(join(ROOT, 'db/seed/001_demo_store.sql'), 'utf8'));
  const despues = (await db.query(`select count(*)::int n from catalog.products`)).rows[0].n;
  check('reejecutar el seed no duplica productos', antes === despues, `${antes} -> ${despues}`);
} catch (err) {
  fallos++;
  console.log(`  FALLO el seed no es idempotente: ${String(err.message).split('\n')[0]}`);
}

// El POS queda fuera del MVP, pero la optionalidad hay que comprarla cuando es barata:
// la linea libre permite cobrar un producto que la app no conoce (catalogo parcial).
titulo('F · Optionalidad comprada para el POS futuro');
const colStock = await db.query(`
  select column_name from information_schema.columns
  where table_schema = 'inventory' and table_name = 'stock' and column_name = 'last_counted_at'`);
check('inventory.stock registra cuando se conto por ultima vez (stock creible)',
  colStock.rows.length === 1);

const colProd = await db.query(`
  select is_nullable from information_schema.columns
  where table_schema = 'pos' and table_name = 'sale_lines' and column_name = 'product_id'`);
check('pos.sale_lines.product_id es NULLABLE (admite linea libre)',
  colProd.rows[0]?.is_nullable === 'YES', `is_nullable=${colProd.rows[0]?.is_nullable}`);

// Una linea libre (sin producto, con descripcion) DEBE aceptarse.
const venta2 = (await db.query(`select id from pos.sales limit 1`)).rows[0];
try {
  await db.exec(`insert into pos.sale_lines (sale_id, line_no, product_id, description, qty, unit_price, line_total)
                 values ('${venta2.id}', 901, NULL, 'Articulo no dado de alta', 1, 3.50, 3.50)`);
  console.log('  ok   linea libre sin producto y con descripcion -> aceptada');
} catch (err) {
  fallos++;
  console.log(`  FALLO la linea libre fue rechazada -> ${String(err.message).split('\n')[0]}`);
}
// Y una linea sin producto NI descripcion debe rechazarse.
await debeFallar(db, 'linea sin producto y sin descripcion (ambiguedad en caja)',
  `insert into pos.sale_lines (sale_id, line_no, product_id, description, qty, unit_price, line_total)
   values ('${venta2.id}', 902, NULL, NULL, 1, 1.00, 1.00)`);

// ---------------------------------------------------------------------
// G · Jerarquia de roles, bloqueo optimista y alertas por persona
// ---------------------------------------------------------------------
titulo('G · Jerarquia de roles, bloqueo optimista y alertas por persona');

// --- G1 · El rol requerido es el MINIMO, no el exclusivo -----------------
const niveles = await db.query(`select code, level from core.roles order by level desc`);
console.log(`  niveles: ${niveles.rows.map((r) => `${r.code}=${r.level}`).join(' > ')}`);
check('los niveles son GERENCIA 30 > COORDINADORA 20 > OPERADORA 10',
  niveles.rows.map((r) => r.level).join(',') === '30,20,10',
  niveles.rows.map((r) => `${r.code}=${r.level}`).join(','));

const elegibilidad = await db.query(`
  select u.email, t.code as template, (ur.level >= tr.level) as elegible
  from core.users u
  join core.roles ur on ur.id = u.role_id
  cross join tasks.task_templates t
  join core.roles tr on tr.code = t.required_role
  where (u.email = 'coordinacion3@malato.es' and t.code = 'LIMPIEZA_LINEAL')
     or (u.email = 'sala1@malato.es'        and t.code = 'CONTROL_CAJA')`);
const coordLimpieza = elegibilidad.rows.find((r) => r.template === 'LIMPIEZA_LINEAL');
const operControl = elegibilidad.rows.find((r) => r.template === 'CONTROL_CAJA');
check('una COORDINADORA SI puede tomar una tarea requerida OPERADORA (20 >= 10)',
  coordLimpieza?.elegible === true, `elegible=${coordLimpieza?.elegible}`);
check('una OPERADORA NO puede tomar una tarea requerida COORDINADORA (10 < 20)',
  operControl?.elegible === false, `elegible=${operControl?.elegible}`);

// Y el seed USA la jerarquia, no solo la declara.
const cruzada = await db.query(`
  select count(*)::int as n
  from tasks.tasks t
  join tasks.task_templates tp on tp.id = t.template_id
  join core.users u  on u.id = t.assignee_id
  join core.roles ur on ur.id = u.role_id
  join core.roles tr on tr.code = tp.required_role
  where ur.level > tr.level`);
check('el seed asigna alguna tarea a alguien de rol SUPERIOR al requerido',
  cruzada.rows[0].n >= 1, `${cruzada.rows[0].n} tareas`);

// --- G2 · Bloqueo optimista del Kanban -----------------------------------
const tarea = (await db.query(`select id, version from tasks.tasks order by created_at limit 1`)).rows[0];
const candidatos = (await db.query(
  `select id from core.users where email in ('sala1@malato.es','sala2@malato.es') order by email`,
)).rows;

const primera = await db.query(
  `update tasks.tasks set assignee_id = '${candidatos[0].id}'
   where id = '${tarea.id}' and version = ${tarea.version} returning id, version`,
);
check('1ª reasignacion con la version correcta -> aceptada',
  primera.rows.length === 1, `filas=${primera.rows.length}`);
check('la version avanza exactamente de uno en uno',
  primera.rows[0]?.version === tarea.version + 1,
  `${tarea.version} -> ${primera.rows[0]?.version}`);

const segunda = await db.query(
  `update tasks.tasks set assignee_id = '${candidatos[1].id}'
   where id = '${tarea.id}' and version = ${tarea.version} returning id`,
);
check('2ª reasignacion con la version YA OBSOLETA -> rechazada (0 filas, no pisa)',
  segunda.rows.length === 0, `filas=${segunda.rows.length}`);

await debeFallar(db, 'una version inventada (salto de 5) la rechaza el trigger',
  `update tasks.tasks set version = version + 5 where id = '${tarea.id}'`);

// --- G3 · Estado de lectura POR PERSONA ----------------------------------
const aviso = (await db.query(
  `select id from notify.notifications where target_role = 'COORDINADORA' order by created_at limit 1`,
)).rows[0];
const coords = (await db.query(
  `select u.id from core.users u join core.roles r on r.id = u.role_id
   where r.code = 'COORDINADORA' order by u.email`,
)).rows;
check('hay 3 coordinadoras para el reparto de alertas', coords.length === 3, `${coords.length}`);

await db.exec(`
  insert into notify.notification_reads (notification_id, user_id) values ('${aviso.id}', '${coords[0].id}');
  insert into notify.notification_reads (notification_id, user_id) values ('${aviso.id}', '${coords[1].id}');`);

const lecturas = await db.query(
  `select count(*)::int as n from notify.notification_reads where notification_id = '${aviso.id}'`,
);
check('dos coordinadoras marcan leida la MISMA alerta -> dos filas independientes',
  lecturas.rows[0].n === 2, `filas=${lecturas.rows[0].n}`);

const pendienteTercera = await db.query(`
  select count(*)::int as n from notify.notifications n
  where n.id = '${aviso.id}'
    and not exists (select 1 from notify.notification_reads r
                    where r.notification_id = n.id and r.user_id = '${coords[2].id}')`);
check('la alerta sigue PENDIENTE para la tercera coordinadora (no desaparece)',
  pendienteTercera.rows[0].n === 1, `n=${pendienteTercera.rows[0].n}`);

await debeFallar(db, 'nadie marca leida dos veces la misma alerta (PK compuesta)',
  `insert into notify.notification_reads (notification_id, user_id) values ('${aviso.id}', '${coords[0].id}')`);

// --- G4 · Plantilla y coherencia del seed --------------------------------
const plantilla = await db.query(`
  select r.code, count(u.id)::int as n
  from core.roles r left join core.users u on u.role_id = r.id
  group by r.code order by r.code`);
const porRol = Object.fromEntries(plantilla.rows.map((r) => [r.code, r.n]));
console.log(`  plantilla: ${plantilla.rows.map((r) => `${r.code}=${r.n}`).join('  ')}`);
check('plantilla real: 1 Gerencia + 3 Coordinadoras + 2 Operadoras',
  porRol['GERENCIA'] === 1 && porRol['COORDINADORA'] === 3 && porRol['OPERADORA'] === 2,
  JSON.stringify(porRol));

const huerfanos = await db.query(`
  select 'tasks.assignee_id' as donde, count(*)::int as n from tasks.tasks t
    where t.assignee_id is not null and not exists (select 1 from core.users u where u.id = t.assignee_id)
  union all
  select 'pos.sales.operator_id', count(*)::int from pos.sales s
    where not exists (select 1 from core.users u where u.id = s.operator_id)
  union all
  select 'pos.cash_sessions.opened_by', count(*)::int from pos.cash_sessions c
    where c.opened_by is not null and not exists (select 1 from core.users u where u.id = c.opened_by)
  union all
  select 'pos.cash_sessions.closed_by', count(*)::int from pos.cash_sessions c
    where c.closed_by is not null and not exists (select 1 from core.users u where u.id = c.closed_by)
  union all
  select 'inventory.wastage.user_id', count(*)::int from inventory.wastage w
    where w.user_id is not null and not exists (select 1 from core.users u where u.id = w.user_id)
  union all
  select 'rules.rule_overrides.target_user_id', count(*)::int from rules.rule_overrides o
    where o.target_user_id is not null and not exists (select 1 from core.users u where u.id = o.target_user_id)
  union all
  select 'notify.notifications.target_user_id', count(*)::int from notify.notifications n
    where n.target_user_id is not null and not exists (select 1 from core.users u where u.id = n.target_user_id)`);
const conHuerfanos = huerfanos.rows.filter((r) => r.n > 0);
check('ninguna referencia del seed apunta a un usuario inexistente',
  conHuerfanos.length === 0, conHuerfanos.map((r) => `${r.donde}=${r.n}`).join(', '));

const retirado = await db.query(`select count(*)::int as n from core.users where email = 'sala3@malato.es'`);
check('el usuario retirado sala3 ya no existe', retirado.rows[0].n === 0);

await db.close();

console.log(`\n${'='.repeat(60)}`);
console.log(fallos === 0
  ? 'ESQUEMA EJECUTADO Y COMPORTAMIENTO VERIFICADO: 0 fallos'
  : `RESULTADO: ${fallos} FALLO(S)`);
console.log('='.repeat(60));
process.exit(fallos === 0 ? 0 : 1);
