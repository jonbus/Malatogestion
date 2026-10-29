/* Prueba que una fecha mala ya NO tumba la aplicación.
   node .tools\probar-fechas-malas.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

function sacar(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
}
function objeto(marca) {
  const i = js.indexOf(marca);
  let prof = 0;
  for (let k = js.indexOf('{', i); k < js.length; k++) {
    if (js[k] === '{') prof++;
    else if (js[k] === '}') { prof--; if (prof === 0) return js.slice(js.indexOf('{', i), k + 1); }
  }
}

const DATOS = JSON.parse(objeto('const DATOS = '));
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

const entorno = `
  const DATOS = ${JSON.stringify(DATOS)};
  const DIA = "2026-10-23";
  const MESES = ["enero","febrero","marzo","abril","mayo","junio","julio",
    "agosto","septiembre","octubre","noviembre","diciembre"];
`;
const F = new Function(entorno + sacar('fechaBuena') + sacar('semanaDe') +
  sacar('sumarDias') + sacar('bonito') + sacar('turnoDe') +
  '\nreturn { fechaBuena, semanaDe, sumarDias, bonito, turnoDe };')();

const MALAS = [undefined, null, '', 'basura', '2026-13-45', 0];
console.log('   === fechas malas: ninguna debe reventar ===');
for (const f of MALAS) {
  let rompio = false, detalle = '';
  try {
    F.semanaDe(f); F.sumarDias(f, 1); F.bonito(f);
    F.turnoDe('coordinacion', 2, f);   // este era el que daba «reading '2'»
    F.turnoDe('coordinacion', 1, f);
    F.turnoDe('tienda', 1, f);
    F.turnoDe('gerencia', 1, f);
  } catch (e) { rompio = true; detalle = e.message; }
  ok(`con ${JSON.stringify(f)} no revienta`, !rompio, detalle);
}

console.log('\n   === y con una fecha buena sigue bien ===');
ok('el lunes 26 es lunes', F.semanaDe('2026-10-26') === 'LUN', F.semanaDe('2026-10-26'));
ok('la Coordinadora 2 trabaja la semana 1',
  F.turnoDe('coordinacion', 2, '2026-10-26').horas >= 0);
ok('Tienda 2 hace el turno A',
  F.turnoDe('tienda', 2, '2026-10-21').clave === 'A', F.turnoDe('tienda', 2, '2026-10-21').clave);
ok('la fecha mala cae a hoy',
  F.fechaBuena('basura') === '2026-10-23', F.fechaBuena('basura'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
