/* Prueba en vivo de la entrada de gerencia.
   Uso:  node .tools\probar-gerencia-en-vivo.mjs <clave>

   La clave se pasa por argumento para no dejarla escrita en ningún fichero.
*/
const BASE = 'https://tienda-malato.netlify.app';
const PIN = process.argv[2];
if (!PIN) { console.log('   falta la clave: pásala como argumento'); process.exit(2); }

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};
const post = (ruta, cuerpo) => fetch(BASE + ruta, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo)
}).then(async r => ({ status: r.status, body: await r.json() }));

console.log('   === la clave NO está en la página ===');
const t = await (await fetch(BASE + '/')).text();
ok('la página no lleva la clave escrita', !t.includes(PIN));
ok('la puerta está, pero SIN decir «gerencia»',
   t.includes('id="caja-clave"') && !t.includes('Clave de gerencia'));
ok('la puerta se abre desde el logo', t.includes('id="logo-login"'));
ok('y la comprobación va al servidor', t.includes('/api/entrar'));
ok('la bandeja de gerencia está', t.includes('pintaGerencia'));
ok('y las cuatro ventanas', t.includes('Las cuatro ventanas del mes'));

console.log('\n   === entrar ===');
const mal = await post('/api/entrar', { pin: '000000' });
ok('con clave mala: 401', mal.status === 401, mal);
ok('y no dice si la clave existe', mal.body.error === 'clave incorrecta', mal.body);

const vacia = await post('/api/entrar', {});
ok('sin clave: 401', vacia.status === 401, vacia);

const casi = await post('/api/entrar', { pin: PIN.slice(0, -1) });
ok('con una parecida: 401', casi.status === 401, casi);

const bien = await post('/api/entrar', { pin: PIN });
ok('con la buena: 200', bien.status === 200, bien);
ok('y entra como gerencia', bien.body.puesto === 'gerencia', bien.body);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
