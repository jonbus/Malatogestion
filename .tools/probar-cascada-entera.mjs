/* La cascada, de punta a punta: montarla, tachar y ver nacer el hijo.
   node .tools\probar-cascada-entera.mjs
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
const PADRE = 'PRUEBA CORTAR CHORIZO ' + Date.now();

console.log('   === 1 · se crea el padre y su cascada, como hace la pantalla ===');
const padre = await post('/api/encargo', {
  quien: 'co1', t: PADRE, p: 'coordinacion', f: HOY, tipo: 'extra', clave: PADRE });
ok('el padre se crea', padre.body.ok === true, padre.body);

const casc = await post('/api/cascada', { quien: 'co1', tarea: PADRE, hijos: [
  { que: 'Envasar ' + PADRE, p: 'tienda', turno: 'tarde', cuando: 0 },
  { que: 'Etiquetar ' + PADRE, p: 'tienda', cuando: 1 }
]});
ok('la cascada se guarda con dos hijos', (casc.body.cascadas || {})[PADRE.toLowerCase()]?.length === 2,
   (casc.body.cascadas || {})[PADRE.toLowerCase()]);

console.log('\n   === 2 · antes de tachar, los hijos NO existen ===');
let est = await (await pedir('/api/estado')).json();
ok('no hay hijos todavía',
   !(est.encargos || []).some(x => x.t.includes('Envasar ' + PADRE)),
   (est.encargos || []).filter(x => x.t.includes(PADRE)).map(x => x.t));

console.log('\n   === 3 · se tacha el padre → nace el primero ===');
const e = (est.encargos || []).find(x => x.t === PADRE);
await post('/api/encargo-hecho', { id: e.id, quien: 'co1' });
const lan = await post('/api/cascada-lanzar', { quien: 'co1', tarea: PADRE, fecha: HOY });
ok('nace el de envasar', lan.body.nacidos.length >= 1, lan.body.nacidos);
est = await (await pedir('/api/estado')).json();
ok('está en la lista', (est.encargos || []).some(x => x.t.includes('Envasar ' + PADRE)));
ok('va a tienda', (est.encargos || []).find(x => x.t.includes('Envasar ' + PADRE))?.p === 'tienda');

console.log('\n   === 4 · y no se duplica al volver a lanzarla ===');
await post('/api/cascada-lanzar', { quien: 'co1', tarea: PADRE, fecha: HOY });
est = await (await pedir('/api/estado')).json();
ok('solo hay uno de envasar',
   (est.encargos || []).filter(x => x.t.includes('Envasar ' + PADRE)).length === 1);

console.log('\n   === 5 · la pantalla lo ofrece ===');
const html = await (await pedir('/')).text();
ok('el bloque «cuando se haga, crear»', html.includes('Cuando se haga, crear'));
ok('solo a coordinación y Jefa', html.includes('quien.puesto === "coordinacion" || quien.puesto === "gerencia"'));
ok('puede poner varios (+ otra)', html.includes('anadirHijo()'));
ok('y quitar', html.includes('quitarHijo('));
ok('guarda la cascada', html.includes('/api/cascada'));

console.log('\n   === limpieza ===');
est = await (await pedir('/api/estado')).json();
for (const x of (est.encargos || [])) {
  if (x.t.includes(PADRE)) await post('/api/encargo-borrar', { id: x.id });
}
await post('/api/cascada', { quien: 'co1', tarea: PADRE, hijos: [] });
est = await (await pedir('/api/estado')).json();
ok('sin tareas de prueba', !(est.encargos || []).some(x => x.t.includes(PADRE)));
ok('sin cascada de prueba',
   !Object.keys(est.cascadas || {}).some(k => k.includes(PADRE.toLowerCase())));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
