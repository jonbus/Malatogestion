/* Diagnostica por qué no sale la ausencia en Turnos. */
import fs from 'node:fs';

const t = fs.readFileSync('docs/nube/public/index.html', 'utf8');

const i = t.indexOf('"ausencias"');
console.log('  ausencias en los datos:');
console.log('   ', t.slice(i, i + 150));

const j = t.indexOf('const GENTE');
console.log('\n  GENTE:');
console.log('   ', t.slice(j, j + 100));

/* se saca la función y se prueba con hoy */
function sacar(nombre) {
  const k = t.indexOf('function ' + nombre + '(');
  let prof = 0;
  for (let x = t.indexOf('{', k); x < t.length; x++) {
    if (t[x] === '{') prof++;
    else if (t[x] === '}') { prof--; if (prof === 0) return t.slice(k, x + 1); }
  }
}
function sacarObjeto(marca) {
  const k = t.indexOf(marca);
  let prof = 0;
  for (let x = t.indexOf('{', k); x < t.length; x++) {
    if (t[x] === '{') prof++;
    else if (t[x] === '}') { prof--; if (prof === 0) return t.slice(t.indexOf('{', k), x + 1); }
  }
}

const DATOS = JSON.parse(sacarObjeto('const DATOS = '));
console.log('\n  ¿hay ausencias?', JSON.stringify(DATOS.turnos.ausencias));

const ausenciaDe = new Function('DATOS', sacar('ausenciaDe') + '\nreturn ausenciaDe;')(DATOS);
console.log('  ausenciaDe("coordinacion", 2, "2026-10-23") ->',
  JSON.stringify(ausenciaDe('coordinacion', 2, '2026-10-23')));
console.log('  ausenciaDe("coordinacion", 1, "2026-10-23") ->',
  JSON.stringify(ausenciaDe('coordinacion', 1, '2026-10-23')));
