// Valida sintaxis PostgreSQL real (parser oficial via WASM) de todos los .sql del proyecto.
// Uso: node .tools/validate-sql.mjs
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const libpg = require('libpg-query');
const parse = libpg.parse || libpg.parseQuery || libpg.default?.parse;

if (typeof parse !== 'function') {
  console.error('No encuentro la funcion parse en libpg-query. Exports:', Object.keys(libpg));
  process.exit(2);
}

const ROOT = process.cwd();
const SKIP = new Set(['node_modules', '.tools', '.npmcache', '.git', 'dist', 'build']);

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    if (SKIP.has(entry)) continue;
    const full = join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (entry.toLowerCase().endsWith('.sql')) out.push(full);
  }
  return out;
}

const files = walk(ROOT).sort();
if (files.length === 0) {
  console.error('No se ha encontrado ningun fichero .sql');
  process.exit(2);
}

let failed = 0;
let totalBytes = 0;

for (const file of files) {
  const rel = relative(ROOT, file);
  const sql = readFileSync(file, 'utf8');
  totalBytes += sql.length;
  const lines = sql.split('\n').length;
  try {
    const res = await parse(sql);
    const n = res?.stmts?.length ?? res?.parse_tree?.stmts?.length ?? '?';
    console.log(`OK    ${rel}  (${lines} lineas, ${n} sentencias)`);
  } catch (err) {
    failed++;
    console.log(`FALLO ${rel}  (${lines} lineas)`);
    console.log(`      ${String(err.message).split('\n')[0]}`);
  }
}

console.log(`\n${files.length - failed}/${files.length} ficheros validos, ${(totalBytes / 1024).toFixed(1)} KB de SQL`);
process.exit(failed === 0 ? 0 : 1);
