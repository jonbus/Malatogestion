/* Prueba en vivo: encargar una tarea desde el calendario y que salte a su día. */
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
const d = new Date(HOY + 'T12:00:00');
d.setDate(d.getDate() + 12);
const F = d.toLocaleDateString('en-CA');

console.log(`   hoy ${HOY} · el encargo va al ${F}\n`);

const t = await (await fetch(BASE + '/')).text();
console.log('   === en la página ===');
ok('el botón de encargar', t.includes('Encargar una tarea'));
ok('el bloque del día', t.includes('Tareas encargadas para este día'));
ok('la función que encarga', t.includes('encargarTarea'));
ok('el punto morado de los encargos', t.includes('es-encargo'));
ok('se elige el puesto', t.includes('tarea-puesto'));

console.log('\n   === encargar y que salte a su día ===');
const e1 = await post('/api/encargo', {
  quien: 'ge1', t: 'LLAMAR AL PROVEEDOR (prueba)', p: 'tienda', f: F
});
ok('se crea', e1.body.ok === true, e1.body);
const nuevo = (e1.body.encargos || []).find(x => x.t === 'LLAMAR AL PROVEEDOR (prueba)');
ok('con su fecha', nuevo && nuevo.f === F, nuevo);
ok('sin marca de diario', nuevo && !nuevo.diario, nuevo);
ok('apunta quién lo puso', nuevo && nuevo.q === 'ge1', nuevo);

const e2 = await (await fetch(BASE + '/api/estado')).json();
const esta = (e2.encargos || []).some(x => x.t === 'LLAMAR AL PROVEEDOR (prueba)' && x.f === F);
ok('está guardado', esta);

/* un encargo de otro día no debe aparecer en este */
const otro = (e2.encargos || []).filter(x => !x.hecho && x.f === HOY &&
  x.t === 'LLAMAR AL PROVEEDOR (prueba)');
ok('no sale en el día de hoy', otro.length === 0, otro);

console.log('\n   === marcarlo como hecho ===');
const e3 = await post('/api/encargo-hecho', { id: nuevo.id, quien: 'op1' });
const sigue = (e3.body.encargos || []).find(x => x.id === nuevo.id && !x.hecho);
ok('al hacerlo, deja de estar pendiente', !sigue, sigue);

console.log('\n   === limpieza ===');
const e4 = await (await fetch(BASE + '/api/estado')).json();
const basura = (e4.encargos || []).filter(x => x.t === 'LLAMAR AL PROVEEDOR (prueba)');
for (const x of basura) await post('/api/encargo-borrar', { id: x.id });
const e5 = await (await fetch(BASE + '/api/estado')).json();
ok('no queda basura',
   (e5.encargos || []).filter(x => x.t === 'LLAMAR AL PROVEEDOR (prueba)').length === 0);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
