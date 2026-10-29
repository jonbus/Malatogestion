// Validador semántico estático para el esquema de "APP Malato".
// Usa el parser real de PostgreSQL (libpg-query / libpg_query) para construir el
// catálogo de objetos y comprobar referencias entre ficheros, en el orden real
// de ejecución (db/init -> migraciones -> seed).
//
// Uso: node .tools/validate-semantics.mjs
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const libpg = require('libpg-query');
const parse = libpg.parse || libpg.parseQuery || libpg.default?.parse;

const FILES = (process.env.SQL_FILES ? process.env.SQL_FILES.split(',') : [
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
]).map((s) => s.trim()).filter(Boolean);

const BUILTIN_TYPES = new Set([
  'uuid', 'text', 'int', 'int4', 'int8', 'integer', 'bigint', 'smallint', 'boolean', 'bool',
  'numeric', 'decimal', 'real', 'double', 'char', 'varchar', 'character', 'timestamp',
  'timestamptz', 'date', 'time', 'timetz', 'interval', 'json', 'jsonb', 'citext', 'ltree',
  'inet', 'cidr', 'macaddr', 'bytea', 'money', 'serial', 'bigserial', 'tsvector', 'point',
]);

const errors = [];
const warnings = [];
const schemas = new Set(['public', 'pg_catalog', 'information_schema', 'pg_temp']);
const types = new Map();   // 'schema.name' -> 'enum'
const tables = new Map();  // 'schema.name' -> { cols, notNullNoDefault, unique, pk }
const funcs = new Set();
const pendingFKs = [];     // se validan al final: permite autorreferencias

const err = (f, m) => errors.push(`${f}: ${m}`);
const warn = (f, m) => warnings.push(`${f}: ${m}`);

// ---------------------------------------------------------------- utils AST
// Los nodos lista de libpg_query llegan como array o como { List: { items } }.
const listOf = (v) => {
  if (Array.isArray(v)) return v;
  if (v && v.List && Array.isArray(v.List.items)) return v.List.items;
  return [];
};
const strVal = (n) => (n && n.String ? n.String.sval : null);
const namePath = (names) => listOf(names).map(strVal).filter(Boolean);
const qname = (parts) => (parts.length > 1 ? `${parts[0]}.${parts[1]}` : parts[0]);
const relName = (rv) => (rv ? (rv.schemaname ? `${rv.schemaname}.${rv.relname}` : rv.relname) : null);

function walk(node, fn) {
  if (node === null || typeof node !== 'object') return;
  if (Array.isArray(node)) { for (const n of node) walk(n, fn); return; }
  fn(node);
  for (const [k, v] of Object.entries(node)) {
    if (k === 'location') continue;
    if (v && typeof v === 'object') walk(v, fn);
  }
}

function lookupTable(ref) {
  if (!ref) return null;
  if (tables.has(ref)) return { key: ref, def: tables.get(ref) };
  if (!ref.includes('.')) {
    for (const s of schemas) {
      const k = `${s}.${ref}`;
      if (tables.has(k)) return { key: k, def: tables.get(k) };
    }
    if (tables.has(ref)) return { key: ref, def: tables.get(ref) };
  }
  return null;
}

// libpg_query coloca las restricciones de tabla dentro de tableElts (nodos
// { Constraint }), no en un campo `constraints` aparte. Hay que recorrer ambas.
function tableConstraints(cs) {
  const out = [];
  for (const elt of listOf(cs.tableElts)) if (elt.Constraint) out.push(elt.Constraint);
  for (const c of listOf(cs.constraints)) if (c.Constraint) out.push(c.Constraint);
  return out;
}

function applyTableConstraint(con, def, rel, file) {
  if (con.contype === 'CONSTR_PRIMARY') {
    const ks = listOf(con.keys).map(strVal).filter(Boolean);
    for (const k of ks) def.pk.add(k);
    def.uniqueSets.push(ks);
  }
  if (con.contype === 'CONSTR_UNIQUE') {
    const ks = listOf(con.keys).map(strVal).filter(Boolean);
    for (const k of ks) def.unique.add(k);
    def.uniqueSets.push(ks);
  }
  if (con.contype === 'CONSTR_FOREIGN') {
    pendingFKs.push({
      file, from: rel, pktable: relName(con.pktable),
      fkAttrs: listOf(con.fk_attrs).map(strVal).filter(Boolean),
      pkAttrs: listOf(con.pk_attrs).map(strVal).filter(Boolean),
    });
  }
}

// ---------------------------------------------------- recolección de ColumnDef
function collectColumns(createStmt, rel, file) {
  const isTemp = createStmt.relation?.relpersistence === 't';
  const def = { cols: new Map(), notNullNoDefault: new Set(), unique: new Set(), pk: new Set(), uniqueSets: [], isTemp, file };

  for (const elt of listOf(createStmt.tableElts)) {
    const cd = elt.ColumnDef;
    if (!cd) continue;
    const name = cd.colname;
    let notNull = false, hasDefault = false;
    const typeParts = namePath(cd.typeName?.names);
    const typeName = typeParts[typeParts.length - 1] || '?';
    if (typeParts.length === 1 && !BUILTIN_TYPES.has(typeName.toLowerCase())) {
      const found = types.has(typeName) || [...types.keys()].some((k) => k.endsWith(`.${typeName}`));
      if (!found) err(file, `tipo desconocido "${typeName}" en ${rel}.${name}`);
    } else if (typeParts.length === 2 && typeParts[0] !== 'pg_catalog') {
      if (!types.has(`${typeParts[0]}.${typeName}`)) {
        err(file, `tipo desconocido "${typeParts[0]}.${typeName}" en ${rel}.${name}`);
      }
    }
    for (const c of listOf(cd.constraints)) {
      const con = c.Constraint;
      if (!con) continue;
      if (con.contype === 'CONSTR_NOTNULL') notNull = true;
      if (con.contype === 'CONSTR_DEFAULT') hasDefault = true;
      if (con.contype === 'CONSTR_GENERATED') hasDefault = true;
      if (con.contype === 'CONSTR_PRIMARY') { def.pk.add(name); def.uniqueSets.push([name]); }
      if (con.contype === 'CONSTR_UNIQUE') { def.unique.add(name); def.uniqueSets.push([name]); }
      if (con.contype === 'CONSTR_FOREIGN') {
        pendingFKs.push({ file, from: `${rel}.${name}`, pktable: relName(con.pktable), pkAttrs: listOf(con.pk_attrs).map(strVal).filter(Boolean) });
      }
    }
    if (cd.identity) hasDefault = true;
    def.cols.set(name, { typeName, notNull, hasDefault });
    if (notNull && !hasDefault) def.notNullNoDefault.add(name);
  }

  for (const con of tableConstraints(createStmt)) applyTableConstraint(con, def, rel, file);
  return def;
}

function checkColumnRefs(expr, def, file, ctx) {
  if (!expr || !def) return;
  const funcNames = new Set();
  walk(expr, (n) => { if (n.FuncCall) funcNames.add(namePath(n.FuncCall.funcname).pop()); });
  walk(expr, (n) => {
    if (!n.ColumnRef) return;
    const fields = listOf(n.ColumnRef.fields).map(strVal).filter(Boolean);
    if (fields.length !== 1) return;
    const f = fields[0];
    if (funcNames.has(f) || f === 'NEW' || f === 'OLD') return;
    if (!def.cols.has(f)) err(file, `${ctx}: referencia a columna inexistente "${f}"`);
  });
}

// ---------------------------------------------------------------- pasada 1
let totalStmts = 0;

for (const file of FILES) {
  const sql = readFileSync(file, 'utf8');
  let res;
  try { res = await parse(sql); } catch (e) { err(file, `parse: ${e.message}`); continue; }

  for (const { stmt } of res.stmts || []) {
    totalStmts++;
    if (stmt.CreateSchemaStmt) { schemas.add(stmt.CreateSchemaStmt.schemaname); continue; }

    if (stmt.CreateEnumStmt) {
      const parts = namePath(stmt.CreateEnumStmt.typeName);
      types.set(qname(parts), 'enum');
      if (parts.length > 1 && !schemas.has(parts[0])) err(file, `CREATE TYPE en esquema no creado: ${qname(parts)}`);
      continue;
    }

    if (stmt.CreateStmt || stmt.CreateForeignTableStmt) {
      const cs = stmt.CreateStmt || stmt.CreateForeignTableStmt;
      const rel = relName(cs.relation);
      if (cs.relation?.schemaname && !schemas.has(cs.relation.schemaname)) {
        err(file, `CREATE TABLE en esquema no creado: ${rel}`);
      }
      const def = collectColumns(cs, rel, file);
      tables.set(rel, def);  // antes de validar CHECK, y permite autorreferencias
      for (const con of tableConstraints(cs)) {
        if (con.contype === 'CONSTR_CHECK' && con.raw_expr) {
          checkColumnRefs(con.raw_expr, def, file, `CHECK ${rel}${con.conname ? ` (${con.conname})` : ''}`);
        }
      }
      for (const elt of listOf(cs.tableElts)) {
        const cd = elt.ColumnDef;
        if (!cd) continue;
        for (const c of listOf(cd.constraints)) {
          const con = c.Constraint;
          if (con?.contype === 'CONSTR_CHECK' && con.raw_expr) {
            checkColumnRefs(con.raw_expr, def, file, `CHECK ${rel}.${cd.colname}`);
          }
        }
      }
      continue;
    }

    if (stmt.CreateFunctionStmt) { funcs.add(qname(namePath(stmt.CreateFunctionStmt.funcname))); continue; }

    if (stmt.IndexStmt) {
      const ix = stmt.IndexStmt;
      const rel = relName(ix.relation);
      const found = lookupTable(rel);
      if (!found) { err(file, `CREATE INDEX sobre tabla inexistente ${rel}`); continue; }
      for (const p of listOf(ix.indexParams)) {
        const ie = p.IndexElem;
        if (!ie) continue;
        if (ie.name && !found.def.cols.has(ie.name)) {
          err(file, `índice ${ix.idxname ?? ''} sobre ${rel}: columna inexistente "${ie.name}"`);
        }
        if (ie.expression) checkColumnRefs(ie.expression, found.def, file, `índice ${ix.idxname ?? ''}`);
      }
      if (ix.whereClause) checkColumnRefs(ix.whereClause, found.def, file, `índice parcial ${ix.idxname ?? ''}`);
      if (ix.unique) {
        found.def.unique.add(`__index__${ix.idxname}`);
        found.def.uniqueSets.push(listOf(ix.indexParams).map((p) => p.IndexElem?.name).filter(Boolean));
      }
      continue;
    }

    if (stmt.CreateTrigStmt) {
      const tr = stmt.CreateTrigStmt;
      if (!lookupTable(relName(tr.relation))) err(file, `CREATE TRIGGER sobre tabla inexistente ${relName(tr.relation)}`);
      const fn = qname(namePath(tr.funcname));
      if (!funcs.has(fn)) err(file, `trigger ${tr.trigname}: función inexistente ${fn}`);
      continue;
    }

    if (stmt.RevokeStmt || stmt.GrantStmt) {
      const g = stmt.GrantStmt || stmt.RevokeStmt;
      for (const o of listOf(g.objects)) {
        const rv = o.RangeVar;
        if (rv && !lookupTable(relName(rv))) {
          err(file, `${stmt.RevokeStmt ? 'REVOKE' : 'GRANT'} sobre tabla inexistente ${relName(rv)}`);
        }
      }
      continue;
    }

    if (stmt.InsertStmt) {
      const ins = stmt.InsertStmt;
      const rel = relName(ins.relation);
      const found = lookupTable(rel);
      if (!found) { err(file, `INSERT en tabla inexistente ${rel}`); continue; }
      const cols = listOf(ins.cols).map((c) => c.ResTarget?.name).filter(Boolean);
      for (const c of cols) if (!found.def.cols.has(c)) err(file, `INSERT en ${rel}: columna inexistente "${c}"`);
      for (const c of found.def.notNullNoDefault) {
        if (!cols.includes(c)) err(file, `INSERT en ${rel}: falta la columna NOT NULL sin DEFAULT "${c}"`);
      }
      const sel = ins.selectStmt?.SelectStmt;
      if (sel && sel.valuesLists) {
        const n = cols.length || found.def.cols.size;
        for (const row of listOf(sel.valuesLists)) {
          const k = listOf(row).length;
          if (k !== n) err(file, `INSERT en ${rel}: fila con ${k} valores, se esperan ${n}`);
        }
      }
      if (ins.onConflictClause) {
        const infer = ins.onConflictClause.infer;
        const hasTarget = infer && (infer.infer === true || listOf(infer.indexElems).length > 0);
        const hasUnique = found.def.pk.size > 0 || found.def.unique.size > 0;
        if (hasTarget && !hasUnique) {
          warn(file, `INSERT en ${rel} con ON CONFLICT (target) sin UNIQUE/PK conocido`);
        }
      }
      continue;
    }
  }
}

// ---------------------------------------------------------------- FKs (pasada final)
for (const fk of pendingFKs) {
  const found = lookupTable(fk.pktable);
  if (!found) { err(fk.file, `FK de ${fk.from} apunta a tabla inexistente ${fk.pktable}`); continue; }
  for (const col of fk.pkAttrs) {
    if (!found.def.cols.has(col)) err(fk.file, `FK de ${fk.from}: ${fk.pktable}.${col} no existe`);
  }
  for (const col of fk.fkAttrs ?? []) {
    const src = lookupTable(fk.from.includes('.') ? fk.from.split('.').slice(0, 2).join('.') : fk.from);
    if (src && !src.def.cols.has(col)) err(fk.file, `FK de ${fk.from}: columna local ${col} no existe`);
  }
}

// ------------------------------------------- referencias en SELECT / FROM
for (const file of FILES) {
  const sql = readFileSync(file, 'utf8');
  let res;
  try { res = await parse(sql); } catch { continue; }
  for (const { stmt } of res.stmts || []) {
    walk(stmt, (n) => {
      if (!n.SelectStmt) return;
      const s = n.SelectStmt;
      const scope = new Map();
      const ctes = new Set();
      for (const cte of listOf(s.withClause?.ctes)) {
        const nm = cte.CommonTableExpr?.ctename;
        if (nm) ctes.add(nm);
      }
      const addFrom = (fc) => {
        for (const item of listOf(fc)) {
          const rv = item.RangeVar;
          if (rv) {
            const found = lookupTable(relName(rv));
            if (!found) {
              if (!ctes.has(rv.relname)) err(file, `FROM/JOIN a tabla inexistente ${relName(rv)}`);
            } else {
              scope.set(rv.alias?.aliasname || rv.relname, found.def);
            }
          }
          if (item.RangeSubselect) {
            if (item.RangeSubselect.alias?.aliasname) scope.set(item.RangeSubselect.alias.aliasname, null);
            addFrom([item.RangeSubselect.subquery]);
          }
          if (item.JoinExpr) addFrom([item.JoinExpr.larg, item.JoinExpr.rarg]);
        }
      };
      addFrom(s.fromClause);
      walk(s, (m) => {
        if (!m.ColumnRef) return;
        const fields = listOf(m.ColumnRef.fields).map(strVal).filter(Boolean);
        if (fields.length < 2) return;
        const [qual, col] = fields;
        const def = scope.get(qual);
        if (def && !def.cols.has(col)) err(file, `columna inexistente: ${qual}.${col}`);
      });
    });
  }
}

// ------------------------------------------- idempotencia de los INSERT del seed
// Un INSERT solo es idempotente si puede chocar con una clave única de negocio
// (no basta el PK uuid aleatorio) o si lleva una guarda WHERE NOT EXISTS.
for (const file of FILES) {
  const sql = readFileSync(file, 'utf8');
  let res;
  try { res = await parse(sql); } catch { continue; }
  for (const { stmt } of res.stmts || []) {
    if (!stmt.InsertStmt) continue;
    const ins = stmt.InsertStmt;
    const found = lookupTable(relName(ins.relation));
    if (!found) continue;

    let hasExistsGuard = false;
    walk(ins, (n) => {
      if (n.SubLink && String(n.SubLink.subLinkType || '').includes('EXISTS')) hasExistsGuard = true;
    });
    if (hasExistsGuard) continue;

    const meaningfulUnique = found.def.uniqueSets.some(
      (set) => set.length > 0 && !(set.length === 1 && set[0] === 'id'),
    );
    if (!meaningfulUnique) {
      err(file, `INSERT en ${relName(ins.relation)} no es idempotente: solo tiene el PK uuid y no lleva guarda NOT EXISTS`);
    }
  }
}

// ---------------------------------------------------------------- informe
console.log(`Sentencias analizadas: ${totalStmts}`);
console.log(`Tablas: ${tables.size} | Tipos: ${types.size} | Esquemas: ${schemas.size} | FK: ${pendingFKs.length}`);
if (warnings.length) {
  console.log(`\nAVISOS (${warnings.length}):`);
  for (const w of warnings) console.log(`  ! ${w}`);
}
if (errors.length) {
  console.log(`\nERRORES (${errors.length}):`);
  for (const e of errors) console.log(`  x ${e}`);
  process.exit(1);
}
console.log('\nSin errores de referencia.');
