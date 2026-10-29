/* Comprueba que el menú «¿Para cuándo lo pasas?» genera botones con su destino.
   node .tools\probar-menu-pasar.mjs
*/
import fs from 'node:fs';

const U = 'http://127.0.0.1:8100';
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
  throw new Error('no cierro ' + nombre);
}

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

/* --- se monta el menú con un entorno mínimo --- */
const entorno = `
  const DIA = "2026-10-23";
  const tab = "manana";
  const quien = { id: "op1", puesto: "tienda" };
  const OPC = {};
  function sumarDias(f, n){
    const d = new Date(f + "T12:00:00"); d.setDate(d.getDate() + n);
    return d.toLocaleDateString("en-CA");
  }
  function bonito(f){ return f; }
  function prefijoPuesto(){ return "op"; }
`;

const fabrica = new Function(entorno + sacar('claveEn') + sacar('menuPasar') +
  '\nreturn { menuPasar, claveEn };');
const { menuPasar, claveEn } = fabrica();

const tarea = { f: '2026-10-23', k: 'td0', partes: [] };
const salida = menuPasar(tarea, 'arr0');

console.log('   === lo que se genera ===');
console.log('   ' + salida.replace(/\s+/g, ' ').slice(0, 300) + '…');

console.log('\n   === comprobaciones ===');
ok('sale la clave en cada botón', salida.includes(`data-clave="${claveEn('2026-10-23', 'td0')}"`));
ok('sale el destino en cada botón', salida.includes('data-destino='));
ok('hay 4 opciones', (salida.match(/op-pasar/g) || []).length === 4,
  (salida.match(/op-pasar/g) || []).length);
ok('el campo «otro día» también lleva clave', salida.includes('inp-pasar" data-clave='));

/* los destinos, uno a uno */
const destinos = [...salida.matchAll(/data-destino='([^']+)'/g)].map(m => JSON.parse(m[1]));
ok('los 4 destinos son JSON válido', destinos.length === 4, destinos.length);
console.log('   ' + JSON.stringify(destinos));
ok('el primero es mañana por la mañana', destinos[0].f === '2026-10-24' && destinos[0].t === 'manana',
  destinos[0]);
ok('el segundo es mañana por la tarde', destinos[1].t === 'tarde', destinos[1]);
ok('el último es «la próxima vez»', destinos[3].proxima === true, destinos[3]);

/* --- y ese destino lo acepta el servidor --- */
console.log('\n   === el servidor acepta ese destino ===');
for (const d of destinos) {
  const r = await fetch(U + '/api/trasladar', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'op1', clave: '2026-10-23|x|PRUEBA-MENU', destino: d })
  });
  const c = await r.json();
  ok('destino ' + JSON.stringify(d) + ' -> ' + r.status, r.status === 200 && c.ok === true, c);
}
/* limpieza */
await fetch(U + '/api/trasladar', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'op1', clave: '2026-10-23|x|PRUEBA-MENU', destino: null })
});

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
