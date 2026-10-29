/* Prueba de los encargos: un día, una serie, y el aviso de pedir.
   node .tools\probar-encargos.mjs
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
const T = 'PRUEBA-' + Date.now();

console.log('   === un día suelto (lo de Ana) ===');
const a = await post('/api/encargo-fecha', {
  quien: 'ge1', que: '1 pan molde Zuaza y 2 pasas', cliente: 'Ana',
  tipo: 'dia', desde: '2099-03-10', antelacion: 1, quienPide: 'coordinacion'
});
ok('se crea', a.status === 200 && a.body.ok === true, a.body);
const ea = (a.body.encargosFecha || []).find(x => x.cliente === 'Ana');
ok('guarda el cliente', ea && ea.cliente === 'Ana');
ok('guarda la antelación', ea && ea.antelacion === 1, ea && ea.antelacion);

console.log('\n   === una serie entre fechas (lo de Carmen) ===');
const b = await post('/api/encargo-fecha', {
  quien: 'co1', que: '1 txapata', cliente: 'Carmen',
  tipo: 'rango', desde: '2099-04-05', hasta: '2099-04-09', antelacion: 1
});
ok('se crea la serie', b.body.ok === true, b.body);
const eb = (b.body.encargosFecha || []).find(x => x.cliente === 'Carmen');
ok('guarda desde y hasta', eb && eb.desde === '2099-04-05' && eb.hasta === '2099-04-09',
  eb && { d: eb.desde, h: eb.hasta });

console.log('\n   === varios días de la semana (lo de Juan) ===');
const c = await post('/api/encargo-fecha', {
  quien: 'ge1', que: '1 pan casero', cliente: 'Juan',
  tipo: 'semana', desde: '2099-05-04', hasta: '2099-05-31', dias: [2, 4]
});
ok('se crea', c.body.ok === true, c.body);
const ec = (c.body.encargosFecha || []).find(x => x.cliente === 'Juan');
ok('guarda los días', ec && ec.dias.join() === '2,4', ec && ec.dias);

console.log('\n   === una serie sin días, se rechaza ===');
const d = await post('/api/encargo-fecha', {
  quien: 'ge1', que: 'x', tipo: 'semana', desde: '2099-05-04', dias: []
});
ok('se rechaza con 400', d.status === 400, d.status);

console.log('\n   === se marca pedido y recibido ===');
const m1 = await post('/api/encargo-fecha-hecho', {
  id: ea.id, cual: 'pedido', fecha: '2099-03-10', quien: 'co1' });
ok('se marca pedido', m1.body.ok === true, m1.body);
const tra = (m1.body.encargosFecha || []).find(x => x.id === ea.id);
ok('queda apuntado', tra && tra.pedidos['2099-03-10']);
const m2 = await post('/api/encargo-fecha-hecho', {
  id: ea.id, cual: 'recibido', fecha: '2099-03-10' });
ok('se marca recibido', m2.body.ok === true);

console.log('\n   === la pantalla ===');
const html = await (await pedir('/')).text();
ok('el botón de añadir', html.includes('Añadir un encargo'));
ok('el aviso gordo', html.includes('encargo-gordo'));
ok('dice PEDIR HOY', html.includes('PEDIR HOY'));
ok('el formulario', html.includes('guardarEncargo'));
ok('los tres tipos', html.includes('Un día') && html.includes('Todos los días') &&
   html.includes('Varios días de la semana'));

console.log('\n   === limpieza ===');
for (const x of ((await (await pedir('/api/estado')).json()).encargosFecha || [])) {
  if (['Ana','Carmen','Juan'].includes(x.cliente)) {
    await post('/api/encargo-fecha-borrar', { id: x.id });
  }
}
const fin = (await (await pedir('/api/estado')).json()).encargosFecha || [];
ok('sin basura', !fin.some(x => ['Ana','Carmen','Juan'].includes(x.cliente)),
  fin.map(x => x.cliente));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
