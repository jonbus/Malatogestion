/* Las llamadas: que se cree, que salga el teléfono y que el botón marque.
   node .tools\probar-llamadas.mjs
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

console.log('   === los 31 proveedores están ===');
const est = await (await pedir('/api/estado')).json();
const prov = est.proveedores || [];
ok('hay 31', prov.length === 31, prov.length);
ok('con 59 teléfonos', prov.reduce((n, x) => n + (x.cs || []).length, 0) === 59,
   prov.reduce((n, x) => n + (x.cs || []).length, 0));
const cadagua = prov.find(x => x.n === 'Cadagua');
ok('Cadagua tiene 3 contactos', cadagua && cadagua.cs.length === 3, cadagua && cadagua.cs.length);
ok('Cadagua cierra a las 15:00', cadagua && cadagua.antes === '15:00');
ok('Cadagua tiene código 231949', cadagua && cadagua.cod === '231949');
const digasa = prov.find(x => x.n === 'Digasa / Coaliment');
ok('Digasa cierra a las 13:00', digasa && digasa.antes === '13:00');
ok('los teléfonos van en dígitos',
   cadagua && cadagua.cs.every(c => /^[0-9]+$/.test(c.t)), cadagua && cadagua.cs);

console.log('\n   === se crea una llamada ===');
const HOY = est.dia;
const clave = 'llamada:PRUEBA:' + Date.now();
const r = await post('/api/encargo', {
  quien: 'co1', t: 'Cadagua · Oficina', p: 'coordinacion', f: HOY,
  tipo: 'llamada', tel: '946798229', motivo: 'confirmar el pedido',
  antesDe: '15:00', clave: clave });
ok('se crea', r.body.ok === true, r.body);
const e = (r.body.encargos || []).find(x => x.clave === clave);
ok('es de tipo llamada', e && e.tipo === 'llamada', e && e.tipo);
ok('guarda el teléfono', e && e.tel === '946798229', e && e.tel);
ok('guarda el motivo', e && e.motivo === 'confirmar el pedido', e && e.motivo);
ok('guarda la hora límite', e && e.antesDe === '15:00', e && e.antesDe);

console.log('\n   === la pantalla ===');
const html = await (await pedir('/')).text();
ok('el bloque de llamar', html.includes('Llamar a un proveedor'));
ok('el desplegable de contactos', html.includes('ll-prov'));
ok('el campo del motivo', html.includes('ll-motivo'));
ok('el botón de añadir', html.includes('anadirLlamada'));
ok('el enlace de marcar', html.includes('href="tel:'));
ok('el aviso de la hora', html.includes('se pasó la hora'));
ok('pone el teléfono bonito', html.includes('telBonito'));

console.log('\n   === limpieza ===');
await post('/api/encargo-borrar', { id: e.id });
const fin = (await (await pedir('/api/estado')).json()).encargos || [];
ok('sin basura', !fin.some(x => x.clave === clave));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
