/* Prueba en vivo: gerencia escondida tras el logo, clave nueva y encargos.
   node .tools\probar-nube-v2.mjs <clave>
*/
const BASE = 'https://tienda-malato.netlify.app';
const PIN = process.argv[2];
if (!PIN) { console.log('   falta la clave'); process.exit(2); }

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};
const post = (ruta, cuerpo) => fetch(BASE + ruta, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo)
}).then(async r => ({ status: r.status, body: await r.json() }));

const t = await (await fetch(BASE + '/')).text();
console.log('   === la puerta escondida ===');
ok('gerencia NO aparece como puesto', !/\["gerencia","Gerencia"/.test(t));
ok('en el login solo hay tienda y coordinación',
   /const PUESTOS = \[\["tienda","Tienda",3\],\["coordinacion","Coordinación",2\]\];/.test(t), 
   (t.match(/const PUESTOS = .*?;/) || [])[0]);
ok('la palabra «Clave» está, sin decir gerencia', t.includes('id="caja-clave"'));
ok('el logo es la puerta', t.includes('id="logo-login"'));
ok('la clave no está escrita en la página', !t.includes(PIN));

console.log('\n   === la clave ===');
ok('con clave mala: 401', (await post('/api/entrar', { pin: '000000' })).status === 401);
ok('con la buena: 200', (await post('/api/entrar', { pin: PIN })).status === 200);
ok('y dice puesto gerencia', (await post('/api/entrar', { pin: PIN })).body.puesto === 'gerencia');

console.log('\n   === la bollería y los encargos ===');
ok('tienda tiene el desplegable de bollería', t.includes('Palmeras kinder'));
ok('con los 10 tipos', ['Donettes','Palmeras surtidas','Palmeras choco','Palmeras kinder',
    'Palmeras coco','Lazos choco','Lazos azúcar','Lazos rayados','Morenitos','Varios']
    .every(x => t.includes(x)));

const clave = 'bolleria:prueba-' + Date.now();
const e1 = await post('/api/encargo', {
  quien: 'op1', t: 'Etiquetar la bollería a granel', p: 'gerencia',
  diario: true, clave: clave, que: 'Palmeras kinder'
});
ok('se crea el encargo', e1.body.ok === true, e1.body);
const creado = (e1.body.encargos || []).find(x => x.clave === clave);
ok('con el tipo de bollería', creado && creado.que === 'Palmeras kinder', creado);
ok('y es de los que salen a diario', creado && creado.diario === true, creado);

/* no se duplica */
const e2 = await post('/api/encargo', {
  quien: 'op1', t: 'Etiquetar la bollería a granel', p: 'gerencia',
  diario: true, clave: clave
});
ok('no se duplica', e2.body.yaEstaba === true, e2.body);

/* se marca hecho y desaparece */
const e3 = await post('/api/encargo-hecho', { id: creado.id, quien: 'ge1' });
const sigue = (e3.body.encargos || []).find(x => x.id === creado.id && !x.hecho);
ok('al marcarlo, deja de estar pendiente', !sigue, sigue);

/* y se puede borrar */
const e4 = await post('/api/encargo', { quien: 'ge1', t: 'Encargo de prueba', p: 'tienda', f: '2026-12-01' });
const nuevo = (e4.body.encargos || []).find(x => x.t === 'Encargo de prueba');
ok('se crea un encargo con fecha', !!nuevo, e4.body.encargos);
const e5 = await post('/api/encargo-borrar', { id: nuevo.id });
ok('se puede borrar', e5.body.borrados === 1, e5.body);

/* coordinación del sábado */
ok('coordinación sube la bollería el sábado', t.includes('Subir la bollería a granel'));
ok('y repone el utillaje', t.includes('Reponer el utillaje de la tienda'));

/* gerencia en la tienda hasta las 9 */
ok('gerencia entra en la tienda hasta las 9', t.includes('En la tienda hasta las 9:00'));

/* limpieza */
for (const x of (e3.body.encargos || [])) {
  if (x.clave && x.clave.startsWith('bolleria:prueba')) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
const fin = await (await fetch(BASE + '/api/estado')).json();
const basura = (fin.encargos || []).filter(x => x.t === 'Encargo de prueba' ||
  (x.clave || '').startsWith('bolleria:prueba'));
ok('no queda basura de la prueba', basura.length === 0, basura);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
