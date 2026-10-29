/* Prueba el recuento del lunes y su cascada.
   node .tools\probar-recuento.mjs
*/
import fs from 'node:fs';

const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

const post = (r, c) => fetch(U + r, {
  method: 'POST', headers: { 'Content-Type': 'application/json', 'User-Agent': UA },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));
const get = (r) => fetch(U + r, { headers: { 'User-Agent': UA } }).then(x => x.json());

function sacar(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
}
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

/* ---------------------------------------------------- 1 · el servidor */
console.log('   === 1 · guardar el recuento ===');
const HOY = (await get('/api/estado')).dia;
const LUNES = '2099-01-05';
const r1 = await post('/api/recuento', {
  quien: 'co1', fecha: LUNES,
  valores: { pollos: 3, codillos: 5, patatas: 2.5, bravas: 1 }
});
ok('se guarda', r1.body.ok === true, r1.body);
ok('vuelve con los números', r1.body.recuentos && r1.body.recuentos[LUNES], r1.body.recuentos);
ok('los números son los que se mandaron',
  r1.body.recuentos[LUNES].pollos === 3 && r1.body.recuentos[LUNES].bravas === 1,
  r1.body.recuentos[LUNES]);
ok('guarda quién lo apuntó', r1.body.recuentos[LUNES].q === 'co1');
ok('guarda la hora', !!r1.body.recuentos[LUNES].h);

console.log('\n   === 2 · el estado lo devuelve ===');
const e1 = await get('/api/estado');
ok('sale en /api/estado', !!e1.recuentos[LUNES], Object.keys(e1.recuentos || {}));

console.log('\n   === 3 · fechas y valores raros ===');
const r2 = await post('/api/recuento', { quien: 'co1', fecha: 'basura', valores: {} });
ok('una fecha mala se rechaza con 400', r2.status === 400, r2.status);
const r3 = await post('/api/recuento', {
  quien: 'co1', fecha: LUNES, valores: { pollos: -5, codillos: 'muchos', patatas: 1.234 }
});
ok('los valores raros no rompen',
  r3.status === 200 && r3.body.recuentos[LUNES].pollos === 0 &&
  r3.body.recuentos[LUNES].patatas === 1.23,
  r3.body.recuentos && r3.body.recuentos[LUNES]);

/* ---------------------------------------------------- 4 · la pantalla */
console.log('\n   === 4 · la pantalla ===');
ok('existe el bloque', js.includes('function bloqueRecuento'));
ok('los cuatro campos', js.includes('"pollos", "Pollos"') && js.includes('"bravas", "Patatas bravas"'));
ok('calcula el lunes de la semana', js.includes('function lunesDe'));
ok('la tienda lo tiene el lunes', html.includes('if(W === "LUN" && tab === "manana") html += bloqueRecuento(true, false)'));
ok('coordinación lo tiene el lunes', html.includes('if(W === "LUN") html += bloqueRecuento(true, true)'));
ok('la Jefa lo ve siempre', html.includes('bloqueRecuento(false, true)'));
ok('la Jefa tiene histórico', js.includes('Los lunes anteriores'));

/* ---------------------------------------------------- 5 · la cascada */
console.log('\n   === 5 · la cascada: al apuntarlo, la Jefa recibe el jueves ===');
const JUEVES = '2099-01-08';
/* se borra el de pruebas anteriores, para empezar de cero */
for (const x of (e1.encargos || [])) {
  if (String(x.clave || '').startsWith('recuento:')) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
await post('/api/encargo', {
  quien: 'co1', t: 'Hacer los pedidos con el recuento del 26/10',
  p: 'gerencia', f: JUEVES, clave: 'recuento:' + LUNES + ':pedido',
  partes: ['Mirar el recuento del lunes', 'Hacer los pedidos']
});
const e2 = await get('/api/estado');
const pedido = (e2.encargos || []).find(x => x.clave === 'recuento:' + LUNES + ':pedido');
ok('la Jefa tiene el encargo', !!pedido, (e2.encargos || []).map(x => x.clave));
ok('es de la Jefa', pedido && pedido.p === 'gerencia', pedido && pedido.p);
ok('para el jueves', pedido && pedido.f === JUEVES, pedido && pedido.f);
ok('con sus dos pasos', pedido && pedido.partes.length === 2, pedido && pedido.partes);

/* ---------------------------------------------------- 6 · limpieza */
console.log('\n   === 6 · se deja limpio ===');
await post('/api/recuento-borrar', { fecha: LUNES });
for (const x of ((await get('/api/estado')).encargos || [])) {
  if (String(x.clave || '').startsWith('recuento:')) await post('/api/encargo-borrar', { id: x.id });
}
const fin = await get('/api/estado');
ok('sin encargos de prueba',
  !(fin.encargos || []).some(x => String(x.clave || '').startsWith('recuento:')),
  (fin.encargos || []).length);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
