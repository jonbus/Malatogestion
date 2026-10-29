/* Prueba de la memoria de nombres y las sugerencias.
   node .tools\probar-nombres.mjs
*/
const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (r, o) => fetch(U + r, Object.assign({
  headers: Object.assign({ 'User-Agent': UA }, (o || {}).headers || {}) }, o || {}));
const post = (r, c) => pedir(r, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

const S = 'Chorizo prueba ' + Date.now();

console.log('   === se escribe una tarea y queda registrada ===');
const a = await post('/api/encargo', {
  quien: 'co1', t: S, p: 'tienda', f: '2026-10-27', clave: S });
ok('se crea', a.body.ok === true, a.body);

const est = await (await pedir('/api/estado')).json();
ok('su nombre queda en la memoria', (est.nombres || []).includes(S), (est.nombres || []).length);

console.log('\n   === al escribir, la ofrece ===');
const sug = await post('/api/sugerencias', { q: 'chorizo prueba' });
ok('la sugiere', (sug.body.sugerencias || []).includes(S), sug.body.sugerencias);
const vacio = await post('/api/sugerencias', { q: '' });
ok('sin escribir nada, ofrece las últimas', (vacio.body.sugerencias || []).length > 0,
   (vacio.body.sugerencias || []).length);
const nada = await post('/api/sugerencias', { q: 'zzzzzznoexiste' });
ok('si no hay nada, no inventa', (nada.body.sugerencias || []).length === 0,
   nada.body.sugerencias);

console.log('\n   === no se duplica el nombre ===');
await post('/api/encargo', { quien: 'co1', t: S, p: 'tienda', f: '2026-10-28' });
const est2 = (await (await pedir('/api/estado')).json()).nombres || [];
ok('sigue apareciendo una vez', est2.filter(n => n === S).length === 1,
   est2.filter(n => n === S).length);

console.log('\n   === y sobrevive a limpiar las tareas ===');
const antes = ((await (await pedir('/api/estado')).json()).encargos || [])
  .filter(x => x.t === S);
for (const x of antes) await post('/api/encargo-borrar', { id: x.id });
const est3 = await (await pedir('/api/estado')).json();
ok('la tarea ya no está', !(est3.encargos || []).some(x => x.t === S));
ok('pero el nombre sí', (est3.nombres || []).includes(S));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
