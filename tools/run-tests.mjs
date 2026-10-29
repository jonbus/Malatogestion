/**
 * Ejecuta TODOS los tests uno a uno.
 *
 * IMPORTANTE: no usa `node --test <dir>` porque el runner de Node lanza
 * subprocesos con stdio por tuberia y el sandbox lo bloquea con EPERM.
 * En su lugar lanza cada fichero con stdio heredado, que si funciona.
 *
 * Uso: node tools/run-tests.mjs
 */
import { spawnSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { join, relative } from 'node:path';

const ROOT = process.cwd();
const TESTS_DIR = join(ROOT, 'tests');

const files = readdirSync(TESTS_DIR)
  .filter((name) => name.endsWith('.test.ts'))
  .sort();

if (files.length === 0) {
  console.error('No hay ficheros *.test.ts en tests/');
  process.exit(1);
}

let failed = 0;
const results = [];

for (const name of files) {
  const file = join(TESTS_DIR, name);
  const started = Date.now();
  const result = spawnSync(process.execPath, [file], {
    stdio: 'inherit',
    cwd: ROOT,
  });
  const elapsed = Date.now() - started;

  if (result.status === 0) {
    results.push(`OK    ${relative(ROOT, file)} (${elapsed} ms)`);
  } else {
    failed += 1;
    results.push(`FALLO ${relative(ROOT, file)} (exit ${result.status})`);
  }
}

console.log('\n================ RESUMEN ================');
for (const line of results) console.log(line);
console.log(`\n${files.length - failed}/${files.length} ficheros de test en verde`);
process.exit(failed === 0 ? 0 : 1);
