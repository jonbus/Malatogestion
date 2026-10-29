/* Prueba en vivo de la cascada de las ofertas, con las fechas de hoy.
   node .tools\probar-ofertas-en-vivo.mjs
*/
const BASE = 'https://tienda-malato.netlify.app';
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};
const post = (ruta, cuerpo) => fetch(BASE + ruta, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo)
}).then(async r => ({ status: r.status, body: await r.json() }));

const e = await (await fetch(BASE + '/api/estado')).json();
const HOY = e.dia;
const p = HOY.split('-').map(Number);
const d = new Date(p[0], p[1] - 1, p[2]);
d.setDate(d.getDate() + (7 - ((d.getDay() + 6) % 7)));
const LUNES = d.toLocaleDateString('en-CA');
const su = 'ofertas:PRUEBA:' + Date.now();

console.log(`   hoy ${HOY} · las ofertas empiezan el lunes ${LUNES}\n`);

const t = await (await fetch(BASE + '/')).text();
console.log('   === en la página ===');
ok('el botón está', t.includes('Dar de alta las ofertas nuevas'));
ok('calcula el lunes siguiente', t.includes('proximoLunes'));
ok('manda la cascada', t.includes('cascada:'));

console.log('\n   === 1) hoy: gerencia prepara ===');
const r = await post('/api/encargo', {
  quien: 'ge1', t: 'Preparar las ofertas nuevas (PRUEBA)', p: 'gerencia', f: HOY,
  clave: su + ':prep',
  partes: ['Dar de alta', 'Sacar etiquetas', 'Organizar stoppers', 'Marcar preparado'],
  cascada: [
    { t: 'Quitar las vencidas y pegar las nuevas (PRUEBA)', p: 'coordinacion',
      f: LUNES, clave: su + ':lineales' },
    { t: 'Pegar la cartelería grande (PRUEBA)', p: 'gerencia',
      f: LUNES, clave: su + ':cartel' }
  ]
});
ok('se crea la de preparar', r.body.ok === true, r.body);
const prep = (r.body.encargos || []).find(x => x.clave === su + ':prep');
ok('es para hoy', prep && prep.f === HOY, prep);
ok('es de la oficina', prep && prep.p === 'gerencia', prep);

console.log('\n   === 2) los hijos NO existen todavía ===');
const a = await (await fetch(BASE + '/api/estado')).json();
const hijosAntes = (a.encargos || []).filter(x => (x.clave || '').startsWith(su + ':li') ||
                                                    (x.clave || '').startsWith(su + ':ca'));
ok('no existen', hijosAntes.length === 0, hijosAntes.length);
ok('ni coordinación ve nada suyo',
   (a.encargos || []).filter(x => x.p === 'coordinacion' && (x.clave || '').startsWith(su)).length === 0);

console.log('\n   === 3) gerencia la marca: SALTA ===');
const h = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
ok('nacen las dos', h.body.nacidos === 2, h.body.nacidos);
const b = await (await fetch(BASE + '/api/estado')).json();
const hijos = (b.encargos || []).filter(x => (x.clave || '').startsWith(su));
const li = hijos.find(x => x.clave === su + ':lineales');
const ca = hijos.find(x => x.clave === su + ':cartel');
ok('la de los lineales es de coordinación', li && li.p === 'coordinacion', li && li.p);
ok('y va para el lunes', li && li.f === LUNES, li && li.f);
ok('la cartelería es de la oficina', ca && ca.p === 'gerencia', ca && ca.p);
ok('y también el lunes', ca && ca.f === LUNES, ca && ca.f);
ok('se sabe que vienen de la primera', li && li.vieneDe === prep.id, li && li.vieneDe);

console.log('\n   === 4) marcarla otra vez no duplica ===');
const otra = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
ok('no nacen más hijos', otra.body.nacidos === 0, otra.body.nacidos);
const c = await (await fetch(BASE + '/api/estado')).json();
const soloHijos = (c.encargos || []).filter(x =>
  x.clave === su + ':lineales' || x.clave === su + ':cartel');
ok('siguen siendo dos hijos', soloHijos.length === 2, soloHijos.length);

console.log('\n   === 5) limpieza ===');
const f2 = await (await fetch(BASE + '/api/estado')).json();
for (const x of (f2.encargos || [])) {
  if ((x.clave || '').startsWith(su) || x.t.includes('(PRUEBA)')) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
const g = await (await fetch(BASE + '/api/estado')).json();
ok('no queda basura', (g.encargos || []).filter(x => (x.clave || '').startsWith(su)).length === 0);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
