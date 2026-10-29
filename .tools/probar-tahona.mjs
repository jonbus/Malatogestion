/* Prueba de la tahona: los cinco panes, entrada y devolución, y el resumen.
   node .tools\probar-tahona.mjs
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

/* una fecha que no es de nadie, para no tocar el pan de verdad */
const HOY = '2099-01-05';
const PANES = ['txapata', 'txapatita', 'barra', 'cuarto', 'txoripan'];

console.log('   === la entrada de la mañana ===');
const e = await post('/api/tahona', {
  quien: 'co1', fecha: HOY, cual: 'entrada',
  valores: { txapata: 20, txapatita: 12, barra: 40, cuarto: 15, txoripan: 8 }
});
ok('se guarda', e.status === 200 && e.body.ok === true, e.body);
const t1 = (e.body.tahona || {})[HOY] || {};
ok('los cinco panes', PANES.every(p => t1.entrada && t1.entrada[p] !== null), t1);
ok('la txapata son 20', t1.entrada && t1.entrada.txapata === 20, t1.entrada);

console.log('\n   === la devolución de la tarde ===');
const d = await post('/api/tahona', {
  quien: 'op1', fecha: HOY, cual: 'devolucion',
  valores: { txapata: 3, txapatita: 2, barra: 5, cuarto: 1, txoripan: 0 }
});
ok('se guarda', d.status === 200 && d.body.ok === true, d.body);
const t2 = (d.body.tahona || {})[HOY] || {};
ok('la entrada sigue ahí', t2.entrada && t2.entrada.txapata === 20, t2.entrada);
ok('y la devolución también', t2.devolucion && t2.devolucion.barra === 5, t2.devolucion);

console.log('\n   === se lee después ===');
const est = await (await pedir('/api/estado')).json();
ok('el estado trae la tahona', !!est.tahona && !!est.tahona[HOY], Object.keys(est.tahona || {}));
ok('con las dos partes', !!est.tahona[HOY].entrada && !!est.tahona[HOY].devolucion);

console.log('\n   === valores raros ===');
const r = await post('/api/tahona', {
  quien: 'co1', fecha: HOY, cual: 'entrada',
  valores: { txapata: -5, barra: 'muchas', cuarto: 1.239, txoripan: '' }
});
const v = ((r.body.tahona || {})[HOY] || {}).entrada || {};
ok('un negativo se queda VACIO', v.txapata === null, v.txapata);
ok('un texto se queda VACIO', v.barra === null, v.barra);
ok('un decimal se redondea', v.cuarto === 1.24, v.cuarto);
ok('una casilla vacía se queda vacía', v.txoripan === null, v.txoripan);
const mala = await post('/api/tahona', { quien: 'co1', fecha: 'basura', valores: {} });
ok('una fecha mala se rechaza', mala.status === 400, mala.status);

console.log('\n   === la pantalla ===');
const html = await (await pedir('/')).text();
PANES.forEach(p => ok(`tiene el campo ${p}`, html.includes(`"${p}"`)));
ok('el botón de guardar', html.includes('tah-guardar'));
ok('la sección del pan existe', html.includes('function pintaPanes'));
ok('el pan tiene su botón en el menú', html.includes('Registro de panes'));
ok('la Jefa tiene el resumen', html.includes('bloqueTahonaResumen'));

console.log('\n   === limpieza ===');
await post('/api/tahona-borrar', { fecha: HOY });
console.log('   (borrada la fecha de mentira)');

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
