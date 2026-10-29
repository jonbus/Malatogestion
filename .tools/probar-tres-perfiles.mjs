/* PRUEBA DE LOS TRES PERFILES · simula el clic de cada uno.
   node .tools\probar-tres-perfiles.mjs
*/
import fs from 'node:fs';

const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

let fallos = 0;
const ok = (g, n, c, extra) => {
  if (!c) { fallos++; console.log(`   FALLO  [${g}] ${n}${extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`); }
  else console.log(`   OK     [${g}] ${n}`);
};

function sacar(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
  throw new Error('no cierro ' + nombre);
}

/* ---------------------------------------------------- 0 · corrupción */
console.log('\n   === 0 · el fichero está sano ===');
ok('0', 'sin [2][2] corrupto', !/\[2\]\[2\]/.test(js));
ok('0', 'sin [1][1] corrupto', !/\[1\]\[1\]/.test(js));
/* [0][0] sí es legítimo: es `lista[0][0]`, la clave de la primera pestaña */
ok('0', 'el [0][0] que hay es el de las pestañas', /lista\[0\]\[0\]/.test(js));
ok('0', 'lleva la versión de hoy', /v-\d{4}-\d{2}-\d{2}-\d+/.test(html));

/* ---------------------------------------------------- 1 · nombres */
console.log('\n   === 1 · el nombre de cada uno ===');
const entorno = `
  const MESES = ["enero","febrero","marzo","abril","mayo","junio","julio",
                 "agosto","septiembre","octubre","noviembre","diciembre"];
`;
const fab1 = new Function(entorno + sacar('nombreDe') + '\nreturn nombreDe;');
const nombreDe = fab1();
ok('1', 'Tienda 1', nombreDe('op1') === 'Tienda 1', nombreDe('op1'));
ok('1', 'Tienda 3', nombreDe('op3') === 'Tienda 3', nombreDe('op3'));
ok('1', 'Coordinadora 1', nombreDe('co1') === 'Coordinadora 1', nombreDe('co1'));
ok('1', 'Coordinadora 2', nombreDe('co2') === 'Coordinadora 2', nombreDe('co2'));
ok('1', 'Jefa', nombreDe('ge1') === 'Jefa', nombreDe('ge1'));

/* ---------------------------------------------------- 2 · datos por perfil */
console.log('\n   === 2 · cada perfil tiene sus pestañas ===');
const DATOS = (() => {
  const i = js.indexOf('const DATOS = ');
  let prof = 0;
  for (let k = js.indexOf('{', i); k < js.length; k++) {
    if (js[k] === '{') prof++;
    else if (js[k] === '}') { prof--; if (prof === 0) return JSON.parse(js.slice(js.indexOf('{', i), k + 1)); }
  }
})();
ok('2', 'la tienda tiene mañana, tarde y cierre',
  !!(DATOS.tienda && DATOS.tienda.manana && DATOS.tienda.tarde && DATOS.tienda.cierre));
ok('2', 'la coordinación tiene apertura, día y cierre',
  !!(DATOS.coordinacion && DATOS.coordinacion.apertura && DATOS.coordinacion.dia));
ok('2', 'la jefa tiene su bandeja',
  !!(DATOS.gerencia && DATOS.gerencia.entrada && DATOS.gerencia.hoy));
ok('2', 'hay 2 patrones de apertura', Object.keys(DATOS.coordinacion.apertura).length === 2,
  Object.keys(DATOS.coordinacion.apertura));
ok('2', 'los patrones son A y B',
  Object.keys(DATOS.coordinacion.apertura).sort().join('') === 'AB',
  Object.keys(DATOS.coordinacion.apertura));
ok('2', 'los turnos están cargados', !!(DATOS.turnos && DATOS.turnos.tienda));
ok('2', 'las vacaciones están cargadas', (DATOS.turnos.ausencias || []).length > 0);

/* ---------------------------------------------------- 3 · sub-pasos de cada perfil */
console.log('\n   === 3 · el clic de los sub-pasos (los tres perfiles) ===');
const ent3 = `
  const ARR = {}; const PAS = {}; const REG = {}; const ENC = {}; const PICK = {};
  const tocados = [];
  function tocar(k, v){ tocados.push(["tocar", k, v]); }
  function tocarEn(f, k, v){ tocados.push(["tocarEn", f, k, v]); }
  function hecha(k){ return false; }
  function hechaEn(f, k){ return false; }
  function pinta(){}
  function ponerSync(){}
  function origenDe(k){ return PAS[k] || null; }
  function encargoHecho(id){ tocados.push(["encargoHecho", id]); }
  function encargoBorrar(id){ tocados.push(["encargoBorrar", id]); }
  function borrarNota(id){ tocados.push(["borrarNota", id]); }
`;
const fab3 = new Function(ent3 + sacar('atenderClic') + '\nreturn { atenderClic, tocados };');
const E3 = fab3();

const nodo = (sel, dataset, padre) => ({
  sel, dataset: dataset || {}, padre: padre || null,
  closest(s) { let n = this; while (n) { if (n.sel === s) return n; n = n.padre; } return null; }
});
const ev = (t) => ({ target: t, stopPropagation() {}, preventDefault() {} });

for (const [perfil, prefijo] of [['tienda', 'gh'], ['coordinación', 'dr'], ['jefa', 'go']]) {
  const item = nodo('.item', { k: prefijo + '0' });
  const cab = nodo('.cab-item', {}, item);
  const partes = nodo('.partes', {}, cab);
  const parte = nodo('.parte', { parte: prefijo + '0.1' }, partes);
  E3.tocados.length = 0;
  E3.atenderClic(ev(parte));
  ok('3', `${perfil}: el sub-paso se marca`,
    E3.tocados.some(t => t[0] === 'tocar' && t[1] === prefijo + '0.1'), E3.tocados);
  E3.tocados.length = 0;
  E3.atenderClic(ev(cab));
  ok('3', `${perfil}: la tarea entera responde`, E3.tocados.length > 0, E3.tocados);
}

/* ---------------------------------------------------- 4 · la cascada completa */
console.log('\n   === 4 · la cascada de las ofertas, de principio a fin ===');
const post = (r, c) => fetch(U + r, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'User-Agent': UA },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));

const est = await (await fetch(U + '/api/estado', { headers: { 'User-Agent': UA } })).json();
const HOY = est.dia;
const T = 'CASCADA-' + Date.now();
const lunes = (() => {
  const d = new Date(HOY + 'T12:00:00');
  d.setDate(d.getDate() + (7 - ((d.getDay() + 6) % 7)));
  return d.toLocaleDateString('en-CA');
})();

/* 4.1 la jefa prepara */
const c1 = await post('/api/encargo', {
  t: 'Preparar ofertas ' + T, p: 'gerencia', f: HOY, clave: T + ':prep',
  cascada: [
    { t: 'Lineales ' + T, p: 'coordinacion', f: lunes, clave: T + ':lin' },
    { t: 'Cartelería ' + T, p: 'gerencia', f: lunes, clave: T + ':car' }
  ]
});
ok('4', 'la jefa crea la tarea de preparar', c1.body.ok === true, c1.body);
const prep = (c1.body.encargos || []).find(x => x.clave === T + ':prep');
ok('4', 'va para hoy', prep && prep.f === HOY, prep && prep.f);

/* 4.2 coordinación NO la ve todavía */
const antes = (await (await fetch(U + '/api/estado')).json()).encargos || [];
const linAntes = antes.filter(x => x.clave === T + ':lin');
ok('4', 'coordinación NO ve nada aún', linAntes.length === 0, linAntes.length);

/* 4.3 la jefa la marca -> salta */
const h = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
ok('4', 'al marcarla nacen 2', h.body.nacidos === 2, h.body.nacidos);

const desp = (await (await fetch(U + '/api/estado')).json()).encargos || [];
const lin = desp.find(x => x.clave === T + ':lin');
const car = desp.find(x => x.clave === T + ':car');
ok('4', 'coordinación recibe la de lineales', !!lin && lin.p === 'coordinacion', lin && lin.p);
ok('4', 'la jefa recibe la de cartelería', !!car && car.p === 'gerencia', car && car.p);
ok('4', 'las dos para el lunes', !!lin && lin.f === lunes && !!car && car.f === lunes);

/* 4.4 coordinación la marca */
if (lin) {
  const h2 = await post('/api/encargo-hecho', { id: lin.id, quien: 'co1' });
  ok('4', 'coordinación puede marcarla', h2.body.ok === true, h2.body);
  const tras = (await (await fetch(U + '/api/estado')).json()).encargos || [];
  const linHecha = tras.find(x => x.clave === T + ':lin');
  ok('4', 'y queda marcada', linHecha && linHecha.hecho === true);
}

/* 4.5 limpieza */
for (const x of ((await (await fetch(U + '/api/estado')).json()).encargos || [])) {
  if ((x.t || '').includes(T) || (x.clave || '').startsWith(T)) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
const fin = (await (await fetch(U + '/api/estado')).json()).encargos || [];
ok('4', 'no queda basura', !fin.some(x => (x.t || '').includes(T)), fin.filter(x => (x.t || '').includes(T)).length);

/* ---------------------------------------------------- 5 · los turnos */
console.log('\n   === 5 · los turnos de hoy ===');
const turnoDe = new Function('DATOS', 'const DIA="2026-10-23";' +
  sacar('fechaBuena') + sacar('turnoDe') + '\nreturn turnoDe;')(DATOS);
const ausenciaDe = new Function('DATOS', sacar('ausenciaDe') + '\nreturn ausenciaDe;')(DATOS);
/* se usa una fecha FIJA: los turnos rotan, así que «hoy» cambia la respuesta */
const DIA_FIJO = '2026-10-21';
ok('5', 'Tienda 2 hace mañanas ese día', turnoDe('tienda', 2, DIA_FIJO).clave === 'A',
  turnoDe('tienda', 2, DIA_FIJO).clave);
ok('5', 'Tienda 3 hace tardes ese día', turnoDe('tienda', 3, DIA_FIJO).clave === 'B',
  turnoDe('tienda', 3, DIA_FIJO).clave);
ok('5', 'Tienda 1 hace el fin de semana ese día', turnoDe('tienda', 1, DIA_FIJO).clave === 'C',
  turnoDe('tienda', 1, DIA_FIJO).clave);
ok('5', 'la Coordinadora 2 estaba de vacaciones esos días',
  !!ausenciaDe('coordinacion', 2, '2026-10-21'));
ok('5', 'y ya no lo está el 26', !ausenciaDe('coordinacion', 2, '2026-10-26'));
ok('5', 'la Coordinadora 1 trabaja', turnoDe('coordinacion', 1, DIA_FIJO).trabaja);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
