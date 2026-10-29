/* Prueba la lógica de fechas, «sin día» y «pasadas a este día»,
   sacándola del propio HTML de la app.

   node .tools/probar-fechas.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];

function sacar(nombre) {
  const i = script.indexOf('function ' + nombre + '(');
  if (i < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(i, k + 1); }
  }
  throw new Error('no cierro ' + nombre);
}

function sacarObjeto(marca) {
  const i = script.indexOf(marca);
  if (i < 0) throw new Error('no encuentro ' + marca);
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(k - (k - script.indexOf('{', i)), k + 1); }
  }
  throw new Error('no cierro ' + marca);
}

const DATOS = JSON.parse(sacarObjeto('const DATOS = '));
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];

const piezas = ['semanaDe', 'sumarDias', 'bonito', 'prefijoPuesto', 'claveEn',
                'hechaEn', 'tablaDia', 'sinDia', 'pasadasA']
  .map(sacar).join('\n');

/* Todas las variables van en el mismo ámbito: se pasan por referencia. */
const marcas = {};
const traslados = {};
const quien = { puesto: 'tienda', numero: 1, id: 'op1' };
const tab = 'tarde';
const fechaSel = '2026-10-21';          // miércoles
const DIAS_ATRAS = 7;

const F = new Function('marcas', 'traslados', 'quien', 'tab', 'fechaSel',
  'DATOS', 'DIAS', 'DIAS_ATRAS',
  piezas + `return { semanaDe, sumarDias, bonito, claveEn, hechaEn, sinDia, pasadasA,
                     get tabla(){ return tablaDia(); } };`
)(marcas, traslados, quien, tab, fechaSel, DATOS, DIAS, DIAS_ATRAS);

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

console.log('   === fechas ===');
ok('2026-10-21 es miércoles', F.semanaDe('2026-10-21') === 'MIE');
ok('2026-10-25 es domingo', F.semanaDe('2026-10-25') === 'DOM');
ok('sumar 1 día', F.sumarDias('2026-10-21', 1) === '2026-10-22');
ok('restar 1 día', F.sumarDias('2026-10-01', -1) === '2026-09-30');
ok('cruza el año', F.sumarDias('2026-12-31', 1) === '2027-01-01');
ok('cruza febrero bisiesto', F.sumarDias('2028-02-28', 1) === '2028-02-29');

console.log('\n   === SIN HACER ===');
const sin0 = F.sinDia('td');
ok('hay pendientes', sin0.length > 0, sin0.length);
ok('ninguno es de hoy', sin0.every(a => a.f < fechaSel), sin0.map(a => a.f));
ok('no pasa de 7 días', sin0.every(a => (new Date(fechaSel) - new Date(a.f)) / 86400000 <= 7));
ok('ninguno está hecho', sin0.every(a => !F.hechaEn(a.f, a.k)));

/* Al darle destino, sale de SIN HACER */
const uno = sin0[0];
traslados[F.claveEn(uno.f, uno.k)] = { f: F.sumarDias(fechaSel, 1), t: 'manana' };
const sin1 = F.sinDia('td');
ok('al pasarle día, sale de SIN HACER',
   sin1.every(a => !(a.f === uno.f && a.k === uno.k)),
   sin1.filter(a => a.f === uno.f && a.k === uno.k).length);

console.log('\n   === PASADAS A ESTE DÍA ===');
/* Con fechaSel = el destino, aparece */
const destino = F.sumarDias(fechaSel, 1);
const pas1 = F.pasadasA();
ok('con el destino de mañana no aparece hoy', pas1.length === 0, pas1.length);

/* Ahora miramos el día de destino, en la pestaña de la mañana */
quien.puesto = 'tienda';
const F2 = new Function('marcas', 'traslados', 'quien', 'tab', 'fechaSel',
  'DATOS', 'DIAS', 'DIAS_ATRAS',
  piezas + `return { sinDia, pasadasA, claveEn, semanaDe };`
)(marcas, traslados, quien, 'manana', destino, DATOS, DIAS, DIAS_ATRAS);
const pas2 = F2.pasadasA();
ok('en el día de destino sí aparece', pas2.length === 1, pas2.length);
ok('y es la tarea que pasamos', pas2[0] && pas2[0].f === uno.f && pas2[0].k === uno.k, pas2);
ok('con su fecha de origen', pas2[0] && pas2[0].f < destino, pas2[0] && pas2[0].f);

/* Si se hace en el origen, deja de aparecer */
marcas[F.claveEn(uno.f, uno.k)] = { q: 'op1', h: '18:00' };
const pas3 = F2.pasadasA();
ok('hecha en su día, deja de aparecer', pas3.length === 0, pas3.length);

console.log('\n   === lo hecho NO vuelve ===');
const hechas = F.sinDia('td');
ok('ninguna de las hechas vuelve a SIN HACER', hechas.every(a => !F.hechaEn(a.f, a.k)));

console.log('\n   === coordinación ===');
quien.puesto = 'coordinacion';
const Fc = new Function('marcas', 'traslados', 'quien', 'tab', 'fechaSel',
  'DATOS', 'DIAS', 'DIAS_ATRAS',
  piezas + `return { sinDia, pasadasA };`
)(marcas, traslados, quien, 'dia', fechaSel, DATOS, DIAS, DIAS_ATRAS);
ok('coordinación también tiene pendientes', Array.isArray(Fc.sinDia('dd')));
ok('y sus claves son las de coordinación', Fc.sinDia('dd').every(a => a.k.startsWith('dd')));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
