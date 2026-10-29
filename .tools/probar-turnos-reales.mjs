/* Comprueba los turnos reales contra la plantilla.
   node .tools\probar-turnos-reales.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];

function sacar(nombre) {
  const i = script.indexOf('function ' + nombre + '(');
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(i, k + 1); }
  }
}
function sacarObjeto(marca) {
  const i = script.indexOf(marca);
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(script.indexOf('{', i), k + 1); }
  }
}

const DATOS = JSON.parse(sacarObjeto('const DATOS = '));
const turnoDe = new Function('DATOS', 'const DIA="2026-10-23";' +
  sacar('fechaBuena') + sacar('turnoDe') + '\nreturn turnoDe;')(DATOS);

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};
const h = (p, n, f) => turnoDe(p, n, f).horas;

/* --- la semana que se dictó: 19 al 25 de octubre --- */
console.log('   === la semana dictada (19-25 oct) ===');
ok('Tienda 1 = domingo entero y tardes', turnoDe('tienda', 1, '2026-10-21').clave === 'C',
   turnoDe('tienda', 1, '2026-10-21').clave);
ok('Tienda 2 = mañanas y sábado', turnoDe('tienda', 2, '2026-10-21').clave === 'A',
   turnoDe('tienda', 2, '2026-10-21').clave);
ok('Tienda 3 = lunes mañana y tardes', turnoDe('tienda', 3, '2026-10-21').clave === 'B',
   turnoDe('tienda', 3, '2026-10-21').clave);

/* --- las horas de cada turno, de la plantilla --- */
console.log('\n   === horas de los tres turnos de tienda ===');
const suma = (p, n, dias) => dias.reduce((a, f) => a + h(p, n, f), 0);
const sem = ['2026-10-19','2026-10-20','2026-10-21','2026-10-22','2026-10-23','2026-10-24','2026-10-25'];
ok('turno A = 20 h', suma('tienda', 2, sem) === 20, suma('tienda', 2, sem));
ok('turno B = 21,5 h', suma('tienda', 3, sem) === 21.5, suma('tienda', 3, sem));
ok('turno C = 19,5 h', suma('tienda', 1, sem) === 19.5, suma('tienda', 1, sem));

/* --- la rotación, 3 semanas --- */
console.log('\n   === la rotación ===');
ok('la semana siguiente Tienda 1 pasa a A',
   turnoDe('tienda', 1, '2026-10-28').clave === 'A', turnoDe('tienda', 1, '2026-10-28').clave);
ok('y a la tercera pasa a B',
   turnoDe('tienda', 1, '2026-11-04').clave === 'B', turnoDe('tienda', 1, '2026-11-04').clave);
ok('y a la cuarta vuelve a C',
   turnoDe('tienda', 1, '2026-11-11').clave === 'C', turnoDe('tienda', 1, '2026-11-11').clave);

/* --- coordinación: semana 1 desde el 26 --- */
console.log('\n   === coordinación ===');
const coord1 = ['2026-10-26','2026-10-27','2026-10-28','2026-10-29','2026-10-30',
                '2026-10-31','2026-11-01'].reduce((a, f) => a + h('coordinacion', 1, f), 0);
ok('Coordinadora 1 semana 1 = 35,5 h', coord1 === 35.5, coord1);
const coord2 = ['2026-10-26','2026-10-27','2026-10-28','2026-10-29','2026-10-30',
                '2026-10-31','2026-11-01'].reduce((a, f) => a + h('coordinacion', 2, f), 0);
ok('Coordinadora 2 semana 1 = 9,5 h', coord2 === 9.5, coord2);
ok('el martes de la semana 1, Coordinadora 1 libre',
   h('coordinacion', 1, '2026-10-27') === 0, h('coordinacion', 1, '2026-10-27'));

/* --- la oficina --- */
console.log('\n   === la oficina ===');
const ofic1 = ['2026-10-26','2026-10-27','2026-10-28','2026-10-29','2026-10-30',
               '2026-10-31','2026-11-01'].reduce((a, f) => a + h('gerencia', 1, f), 0);
ok('la oficina semana 1 = 44,5 h', ofic1 === 44.5, ofic1);

/* --- las medias del año --- */
console.log('\n   === las medias de 4 semanas (coordinación) ===');
const dias4 = [];
for (let i = 0; i < 28; i++) {
  const d = new Date('2026-10-26T12:00:00');
  d.setDate(d.getDate() + i);
  dias4.push(d.toLocaleDateString('en-CA'));
}
for (const n of [1, 2]) {
  const total = dias4.reduce((a, f) => a + h('coordinacion', n, f), 0);
  const media = total / 4;
  const esperado = n === 1 ? 31.25 : 21.0;
  ok(`Coordinadora ${n}: media ${media.toFixed(2)} h/sem (esperado ${esperado})`,
     Math.abs(media - esperado) < 0.3, media);
}

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
