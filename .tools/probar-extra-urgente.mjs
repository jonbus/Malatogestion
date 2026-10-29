/* Prueba: tarea extra con tipo, que se marca y que se pasa a otro día.
   node .tools\probar-extra-urgente.mjs
*/
const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta, Object.assign({
  headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
  opciones || {}));
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
const T = 'EX-' + Date.now();

console.log('   === se dan de alta dos: una extra y una urgente ===');
const a = await post('/api/encargo', {
  quien: 'ge1', t: 'Extra ' + T, p: 'tienda', f: HOY, turno: 'tarde',
  clave: T + ':a', tipo: 'extra'
});
const b = await post('/api/encargo', {
  quien: 'ge1', t: 'Urgente ' + T, p: 'tienda', f: HOY, turno: 'tarde',
  clave: T + ':b', tipo: 'urgente'
});
ok('se crean las dos', a.body.ok === true && b.body.ok === true);
const est = await (await pedir('/api/estado')).json();
const ea = (est.encargos || []).find(x => x.clave === T + ':a');
const eb = (est.encargos || []).find(x => x.clave === T + ':b');
ok('la primera es extra', ea && ea.tipo === 'extra', ea && ea.tipo);
ok('la segunda es urgente', eb && eb.tipo === 'urgente', eb && eb.tipo);
ok('la urgente conserva el turno', eb && eb.turno === 'tarde', eb && eb.turno);

console.log('\n   === se marca (tickar) ===');
const h = await post('/api/encargo-hecho', { id: ea.id, quien: 'op2' });
ok('se puede marcar', h.status === 200 && h.body.ok === true, h.body);
const est2 = await (await pedir('/api/estado')).json();
const ea2 = (est2.encargos || []).find(x => x.clave === T + ':a');
ok('queda marcada', ea2 && ea2.hecho === true);

console.log('\n   === se pasa a otro día ===');
const dosDias = '2099-06-15';
const m = await post('/api/encargo-mover', { id: eb.id, f: dosDias });
ok('se mueve', m.status === 200 && m.body.ok === true, m.body);
const est3 = await (await pedir('/api/estado')).json();
const eb3 = (est3.encargos || []).find(x => x.clave === T + ':b');
ok('queda en el 28', eb3 && eb3.f === dosDias, eb3 && eb3.f);
ok('ya no está en hoy', eb3 && eb3.f !== HOY);

console.log('\n   === dejarla sin día ===');
const m2 = await post('/api/encargo-mover', { id: eb.id, f: null });
ok('se puede dejar sin día', m2.status === 200 && m2.body.ok === true, m2.body);
const est4 = await (await pedir('/api/estado')).json();
const eb4 = (est4.encargos || []).find(x => x.clave === T + ':b');
ok('sin fecha', eb4 && eb4.f === null, eb4 && eb4.f);

console.log('\n   === fechas malas ===');
const m3 = await post('/api/encargo-mover', { id: eb.id, f: 'basura' });
ok('una fecha mala se rechaza', m3.status === 400, m3.status);
const m4 = await post('/api/encargo-mover', { id: 'no-existe', f: dosDias });
ok('un id que no existe, 404', m4.status === 404, m4.status);

console.log('\n   === en la pantalla ===');
const html = await (await pedir('/')).text();
ok('el desplegable de tipo', html.includes('id="tarea-tipo"'));
ok('ofrece Extra y Urgente',
  html.includes('>Extra</option>') && html.includes('>Urgente</option>'));
ok('la marca de urgente', html.includes('tag urgente'));
ok('el «si no da tiempo»', html.includes('Si no da tiempo'));
ok('el campo para pasarla', html.includes('inp-enc'));

console.log('\n   === limpieza ===');
for (const x of ((await (await pedir('/api/estado')).json()).encargos || [])) {
  if (String(x.clave || '').startsWith(T)) await post('/api/encargo-borrar', { id: x.id });
}
const fin = (await (await pedir('/api/estado')).json()).encargos || [];
ok('sin basura', !fin.some(x => String(x.clave || '').startsWith(T)));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
