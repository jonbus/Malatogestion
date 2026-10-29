/* Las cuatro pruebas de la cascada, antes de tocar la pantalla.
   node .tools\probar-cascadas.mjs
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

const HOY = (await (await pedir('/api/estado')).json()).dia;
const TAREA = 'PRUEBA CORTAR CHORIZO ' + Date.now();
const TAREA2 = 'PRUEBA CORTAR DOS ' + Date.now();

console.log('   === 0 · quién puede montarla ===');
const sinPermiso = await post('/api/cascada', {
  quien: 'op1', tarea: TAREA, hijos: [{ que: 'Envasar', p: 'tienda' }] });
ok('tienda NO puede montarla', sinPermiso.status === 403, sinPermiso.status);

console.log('\n   === 1 · se monta ===');
const mont = await post('/api/cascada', {
  quien: 'co1', tarea: TAREA,
  hijos: [{ que: 'Envasar ' + TAREA, p: 'tienda', turno: 'tarde', cuando: 0 }] });
ok('coordinación sí puede', mont.body.ok === true, mont.body);
ok('queda guardada', !!(mont.body.cascadas || {})[TAREA.toLowerCase()], Object.keys(mont.body.cascadas || {}));

console.log('\n   === 2 · tachar el padre hace nacer el hijo ===');
const lanz = await post('/api/cascada-lanzar', { quien: 'co1', tarea: TAREA, fecha: HOY });
ok('nace el hijo', lanz.body.ok === true && lanz.body.nacidos.length === 1,
   lanz.body.nacidos);
const hijo = (lanz.body.nacidos || [])[0] || {};
ok('va a tienda', hijo.p === 'tienda', hijo.p);
ok('por la tarde', hijo.turno === 'tarde', hijo.turno);
ok('para hoy (cuando=0)', hijo.f === HOY, hijo.f);

console.log('\n   === 3 · lanzarla otra vez NO duplica ===');
const otra = await post('/api/cascada-lanzar', { quien: 'co1', tarea: TAREA, fecha: HOY });
ok('no nace otro', (otra.body.nacidos || []).length === 0, otra.body.nacidos);
const est = await (await pedir('/api/estado')).json();
const suyos = (est.encargos || []).filter(x => String(x.clave || '').includes(TAREA.toLowerCase()));
ok('solo hay uno', suyos.length === 1, suyos.length);

console.log('\n   === 4 · al día siguiente: cuando=1 ===');
await post('/api/cascada', { quien: 'ge1', tarea: TAREA2,
  hijos: [{ que: 'Envasar ' + TAREA2, p: 'tienda', cuando: 1 }] });
const lan2 = await post('/api/cascada-lanzar', { quien: 'ge1', tarea: TAREA2, fecha: '2026-10-30' });
const h2 = (lan2.body.nacidos || [])[0] || {};
ok('nace al día siguiente', h2.f === '2026-10-31', h2.f);

console.log('\n   === 5 · un padre de ayer NO crea nada en el pasado ===');
const lan3 = await post('/api/cascada-lanzar', { quien: 'co1', tarea: TAREA2, fecha: '2026-01-10' });
const h3 = (lan3.body.nacidos || [])[0] || {};
ok('nace para hoy, no en el pasado', h3.f === HOY, { f: h3.f, hoy: HOY });

console.log('\n   === limpieza ===');
for (const x of ((await (await pedir('/api/estado')).json()).encargos || [])) {
  if (String(x.clave || '').includes('prueba cortar')) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
await post('/api/cascada', { quien: 'co1', tarea: TAREA, hijos: [] });
await post('/api/cascada', { quien: 'co1', tarea: TAREA2, hijos: [] });
const fin = (await (await pedir('/api/estado')).json());
ok('sin tareas de prueba',
  !(fin.encargos || []).some(x => String(x.clave || '').includes('prueba cortar')));
ok('sin cascadas de prueba',
  !Object.keys(fin.cascadas || {}).some(k => k.includes('prueba cortar')));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
