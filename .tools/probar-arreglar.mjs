/* Prueba del botón «¿Algo para arreglar?».
   node .tools\probar-arreglar.mjs
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
const CLAVE = 'arreglar:prueba-' + Date.now();

console.log('   === se apunta algo para arreglar ===');
const a = await post('/api/encargo', {
  quien: 'op2', t: 'PRUEBA · un caducado de yogur', p: 'coordinacion',
  f: HOY, diario: true, tipo: 'arreglar', clave: CLAVE
});
ok('se crea', a.status === 200 && a.body.ok === true, a.body);
const e1 = await (await pedir('/api/estado')).json();
const arr = (e1.encargos || []).find(x => x.clave === CLAVE);
ok('va a coordinación', arr && arr.p === 'coordinacion', arr && arr.p);
ok('es de tipo arreglar', arr && arr.tipo === 'arreglar', arr && arr.tipo);
ok('sale todos los días hasta que se haga', arr && arr.diario === true, arr && arr.diario);

console.log('\n   === no se puede apuntar dos veces lo mismo ===');
const b = await post('/api/encargo', {
  quien: 'op2', t: 'PRUEBA · un caducado de yogur', p: 'coordinacion',
  f: HOY, diario: true, tipo: 'arreglar', clave: CLAVE
});
ok('la segunda no duplica', b.body.yaEstaba === true || b.body.ok === true, b.body);

console.log('\n   === sigue ahí al día siguiente (no caduca) ===');
ok('tiene diario, así que no desaparece', arr && arr.diario === true);

console.log('\n   === coordinación lo puede marcar cuando esté arreglado ===');
const h = await post('/api/encargo-hecho', { id: arr.id, quien: 'co1' });
ok('se marca', h.status === 200 && h.body.ok === true, h.body);
const e2 = await (await pedir('/api/estado')).json();
const arr2 = (e2.encargos || []).find(x => x.clave === CLAVE);
ok('queda marcada', arr2 && arr2.hecho === true);

console.log('\n   === la pantalla ===');
const html = await (await pedir('/')).text();
ok('el bloque existe', html.includes('Para arreglar'));
ok('tienda lo tiene', html.includes('bloqueArreglar'));
ok('la etiqueta PARA ARREGLAR', html.includes('PARA ARREGLAR'));
ok('el estilo naranja', html.includes('es-arreglar'));
ok('el pan en una columna', html.includes('.tahona{grid-template-columns:1fr}'));

console.log('\n   === limpieza ===');
for (const x of ((await (await pedir('/api/estado')).json()).encargos || [])) {
  if (String(x.clave || '').startsWith('arreglar:prueba')) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
const fin = (await (await pedir('/api/estado')).json()).encargos || [];
ok('sin basura', !fin.some(x => String(x.clave || '').startsWith('arreglar:prueba')));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
