/* Comprueba que las ocho cascadas de cortar → envasar están y funcionan.
   node .tools\probar-cascadas-sembradas.mjs
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

const PAREJAS = ['chorizo ibérico', 'chorizo ELE dulce', 'chorizo ELE picante',
  'salchichón ibérico', 'salchichón ELE', 'queso', 'panceta ELE', 'Extremadura'];

const est = await (await pedir('/api/estado')).json();
const casc = est.cascadas || {};
const nombres = est.nombres || [];

console.log('   === las ocho cascadas ===');
PAREJAS.forEach(t => {
  const k = ('Cortar ' + t).toLowerCase();
  const h = (casc[k] || [])[0];
  ok(`«Cortar ${t}» → «Envasar ${t}»`, !!h && h.que === 'Envasar ' + t && h.p === 'tienda', h);
});

console.log('\n   === los dieciséis nombres, en la memoria ===');
PAREJAS.forEach(t => {
  ok('Cortar ' + t, nombres.includes('Cortar ' + t));
  ok('Envasar ' + t, nombres.includes('Envasar ' + t));
});

console.log('\n   === y al escribir, los ofrece ===');
const sug = await post('/api/sugerencias', { q: 'cortar' });
ok('al escribir «cortar» salen las ocho',
  (sug.body.sugerencias || []).filter(s => s.startsWith('Cortar ')).length >= 8,
  (sug.body.sugerencias || []));
const sug2 = await post('/api/sugerencias', { q: 'envasar queso' });
ok('al escribir «envasar queso» sale la buena',
  (sug2.body.sugerencias || []).includes('Envasar queso'), sug2.body.sugerencias);

console.log('\n   === y una cascada sembrada lanza su hijo ===');
const HOY = est.dia;
const PADRE = 'Cortar queso';
const lan = await post('/api/cascada-lanzar', { quien: 'co1', tarea: PADRE, fecha: HOY });
ok('nace «Envasar queso»', (lan.body.nacidos || []).some(x => x.t === 'Envasar queso'),
   lan.body.nacidos);
// limpieza: se quita el hijo de prueba
for (const x of (lan.body.encargos || [])) {
  if (x.t === 'Envasar queso' && !x.hecho) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
const fin = await (await pedir('/api/estado')).json();
ok('sin basura',
  !(fin.encargos || []).some(x => x.t === 'Envasar queso' && !x.hecho));
ok('y la cascada sigue montada',
  ((fin.cascadas || {})['cortar queso'] || []).length === 1);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
