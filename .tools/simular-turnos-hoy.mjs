/* Simula las seis filas de «Turnos» para hoy. */
import fs from 'node:fs';

const t = fs.readFileSync('docs/nube/public/index.html', 'utf8');

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
const F = new Function('DATOS', sacar('turnoDe') + '\n' + sacar('ausenciaDe') +
  '\nreturn {turnoDe, ausenciaDe};')(DATOS);

const GENTE = [
  { puesto: 'tienda', numero: 1, nombre: 'Tienda 1' },
  { puesto: 'tienda', numero: 2, nombre: 'Tienda 2' },
  { puesto: 'tienda', numero: 3, nombre: 'Tienda 3' },
  { puesto: 'coordinacion', numero: 1, nombre: 'Coordinadora 1' },
  { puesto: 'coordinacion', numero: 2, nombre: 'Coordinadora 2' },
  { puesto: 'gerencia', numero: 1, nombre: 'Oficina' },
];

const HOY = '2026-10-23';
console.log(`  === Turnos de ${HOY} ===\n`);
for (const g of GENTE) {
  const tu = F.turnoDe(g.puesto, g.numero, HOY);
  const au = F.ausenciaDe(g.puesto, g.numero, HOY);
  const marca = au ? 'de vacaciones' : (tu.trabaja ? tu.horas + ' h' : 'libre');
  const quien = au ? 'lo cubre ' + au.cubre : (tu.trabaja ? tu.nombre : 'no trabaja');
  console.log(`  ${g.nombre.padEnd(15)} ${quien.padEnd(34)} ${marca}`);
}
