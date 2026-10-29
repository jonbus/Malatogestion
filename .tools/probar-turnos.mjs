/* Prueba los turnos: que la semana dictada salga y que la rotación avance.
   node .tools\probar-turnos.mjs
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
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(script.indexOf('{', i), k + 1); }
  }
  throw new Error('no cierro ' + marca);
}

const DATOS = JSON.parse(sacarObjeto('const DATOS = '));
const turnoDe = new Function('DATOS', sacar('turnoDe') + '\nreturn turnoDe;')(DATOS);

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

const sem = (p, n, f) => turnoDe(p, n, f);

console.log('   === la semana dictada (19-25 de octubre) ===');
ok('Tienda 1 hace fin de semana', sem('tienda', 1, '2026-10-21').clave === 'FD',
   sem('tienda', 1, '2026-10-21'));
ok('Tienda 2 hace mañana', sem('tienda', 2, '2026-10-21').clave === 'M',
   sem('tienda', 2, '2026-10-21'));
ok('Tienda 3 hace tarde', sem('tienda', 3, '2026-10-21').clave === 'T',
   sem('tienda', 3, '2026-10-21'));

console.log('\n   === la rotación avanza cada 3 semanas ===');
ok('la semana siguiente Tienda 1 pasa a mañana',
   sem('tienda', 1, '2026-10-28').clave === 'M', sem('tienda', 1, '2026-10-28'));
ok('y la otra Tienda 2 pasa a tarde',
   sem('tienda', 2, '2026-10-28').clave === 'T', sem('tienda', 2, '2026-10-28'));
ok('a las 3 semanas vuelve a empezar',
   sem('tienda', 1, '2026-11-11').clave === 'FD', sem('tienda', 1, '2026-11-11'));

console.log('\n   === los días libres de cada turno ===');
ok('fin de semana: martes libre', sem('tienda', 1, '2026-10-20').horas === 0,
   sem('tienda', 1, '2026-10-20'));
ok('fin de semana: domingo trabaja', sem('tienda', 1, '2026-10-25').horas > 0,
   sem('tienda', 1, '2026-10-25'));
ok('mañana: lunes libre', sem('tienda', 2, '2026-10-19').horas === 0,
   sem('tienda', 2, '2026-10-19'));
ok('mañana: sábado trabaja', sem('tienda', 2, '2026-10-24').horas > 0,
   sem('tienda', 2, '2026-10-24'));
ok('tarde: lunes por la mañana sí', sem('tienda', 3, '2026-10-19').horas > 0,
   sem('tienda', 3, '2026-10-19'));
ok('tarde: sábado libre', sem('tienda', 3, '2026-10-24').horas === 0,
   sem('tienda', 3, '2026-10-24'));

console.log('\n   === coordinación: el lunes 26 empieza la semana 1 ===');
ok('lunes 26 = semana 1', sem('coordinacion', 1, '2026-10-26').clave === 'S1',
   sem('coordinacion', 1, '2026-10-26'));
ok('el 2 de noviembre = semana 2', sem('coordinacion', 1, '2026-11-02').clave === 'S2',
   sem('coordinacion', 1, '2026-11-02'));
ok('el 9 = semana 3', sem('coordinacion', 1, '2026-11-09').clave === 'S3',
   sem('coordinacion', 1, '2026-11-09'));
ok('el 16 = semana 4', sem('coordinacion', 1, '2026-11-16').clave === 'S4',
   sem('coordinacion', 1, '2026-11-16'));
ok('el 23 vuelve a la semana 1', sem('coordinacion', 1, '2026-11-23').clave === 'S1',
   sem('coordinacion', 1, '2026-11-23'));

console.log('\n   === la coordinadora 2 tiene la semana 1 casi libre ===');
const c2 = ['2026-10-26','2026-10-27','2026-10-28','2026-10-29','2026-10-30',
            '2026-10-31','2026-11-01'].map(f => sem('coordinacion', 2, f).horas);
const totalC2 = c2.reduce((a, b) => a + b, 0);
ok('suma pocas horas esa semana', totalC2 > 0 && totalC2 < 15, { c2, totalC2 });

console.log('\n   === la oficina ===');
ok('la semana 4 no trabaja el viernes',
   sem('gerencia', 1, '2026-11-20').horas === 0, sem('gerencia', 1, '2026-11-20'));
ok('la semana 1 sí trabaja el domingo',
   sem('gerencia', 1, '2026-11-01').horas > 0, sem('gerencia', 1, '2026-11-01'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
