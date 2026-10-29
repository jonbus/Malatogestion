/* Prueba completa de la app en Cloudflare.
   node .tools\probar-cloudflare.mjs
*/
const U = 'https://app.supermalato.workers.dev';

/* Cloudflare rechaza a los programas que no se identifican como navegador,
   así que las pruebas se presentan como tal. Un móvil de verdad no tiene
   este problema. */
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta,
  Object.assign({ headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
                opciones || {}));

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};
const post = (ruta, cuerpo) => pedir(ruta, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo ?? {})
}).then(async r => ({ status: r.status, body: await r.json().catch(() => ({})) }));

console.log(`  dirección: ${U}\n`);

/* 1 · la aplicación */
console.log('   === la aplicación ===');
const r = await pedir('/');
const html = await r.text();
ok('carga la página', r.status === 200 && html.length > 100000, html.length);
ok('es la versión de hoy', /v-\d{4}-\d{2}-\d{2}-\d+/.test(html));
ok('trae el recuento del lunes', html.includes('Recuento del lunes'));
ok('trae los botones de la Jefa', html.includes('gerencia: ['));

/* 2 · la API */
console.log('\n   === la API ===');
const e = await (await pedir('/api/estado')).json();
ok('el estado responde', e.ok === true, e);
ok('dice el día', /^\d{4}-\d{2}-\d{2}$/.test(String(e.dia)), e.dia);
ok('el estado trae las seis partes',
  ['marcas','traslados','notas','fichajes','encargos','recuentos']
    .every(k => e[k] !== undefined),
  Object.keys(e));

/* 3 · la clave de la Jefa */
console.log('\n   === la clave de la Jefa ===');
const mala = await post('/api/entrar', { pin: 'nada' });
ok('la clave mala se rechaza (401)', mala.status === 401, mala.status);
const buena = await post('/api/entrar', { pin: '«la clave de la Jefa — se dice aparte, no se escribe»' });
ok('la buena entra como gerencia',
  buena.status === 200 && buena.body.puesto === 'gerencia', buena.body);

/* 4 · guardar de verdad */
console.log('\n   === guardar de verdad ===');
const clave = '2026-10-26|op|prueba-cf';
const m = await post('/api/marcas', { quien: 'op1', cambios: { [clave]: { q: 'op1' } } });
ok('se guarda una marca', m.status === 200 && m.body.ok === true, m.body);
const e2 = await (await pedir('/api/estado')).json();
ok('y se lee después', !!e2.marcas[clave], Object.keys(e2.marcas));
const m2 = await post('/api/marcas', { quien: 'op1', cambios: { [clave]: null } });
ok('se puede borrar', m2.status === 200);

/* 5 · el recuento */
console.log('\n   === el recuento del lunes ===');
const rec = await post('/api/recuento', {
  quien: 'co1', fecha: '2099-01-05',
  valores: { pollos: 4, codillos: 2, patatas: 1, bravas: 0 }
});
ok('se guarda el recuento', rec.status === 200 && rec.body.ok === true, rec.body);
const e3 = await (await pedir('/api/estado')).json();
ok('y se lee después', e3.recuentos && e3.recuentos['2099-01-05'], e3.recuentos);

/* 6 · la cascada de las ofertas */
console.log('\n   === la cascada de las ofertas ===');
const T = 'CF-' + Date.now();
const c1 = await post('/api/encargo', {
  quien: 'ge1', t: 'Preparar ' + T, p: 'gerencia', f: '2026-10-26',
  clave: T + ':prep',
  cascada: [{ t: 'Lineales ' + T, p: 'coordinacion', f: '2026-11-02', clave: T + ':lin' }]
});
const prep = (c1.body.encargos || []).find(x => x.clave === T + ':prep');
ok('nace la de preparar', !!prep);
const h = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
ok('al marcarla nace la de coordinación', h.body.nacidos === 1, h.body.nacidos);
const e4 = await (await pedir('/api/estado')).json();
ok('coordinación la tiene', (e4.encargos || []).some(x => x.clave === T + ':lin'));

/* 7 · limpieza */
console.log('\n   === limpieza ===');
for (const x of ((await (await pedir('/api/estado')).json()).encargos || [])) {
  if (String(x.clave || '').startsWith(T)) await post('/api/encargo-borrar', { id: x.id });
}
await post('/api/marcas', { quien: 'op1', cambios: { [clave]: null } });
/* se borra la clave de la fecha de mentira, sin tocar ningún día real */
await post('/api/recuento-borrar', { fecha: '2099-01-05' });
const fin = await (await pedir('/api/estado')).json();
ok('no queda basura', !(fin.encargos || []).some(x => String(x.clave || '').startsWith(T)));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
