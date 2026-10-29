/* Prueba en vivo del «para cuándo lo pasas». */
const BASE = 'https://tienda-malato.netlify.app';
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};
const post = (ruta, cuerpo) => fetch(BASE + ruta, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo)
}).then(r => r.json());

const e = await (await fetch(BASE + '/api/estado')).json();
const HOY = e.dia;
const manana = new Date(HOY + 'T12:00:00');
manana.setDate(manana.getDate() + 1);
const MANANA = manana.toLocaleDateString('en-CA');

console.log(`   hoy ${HOY} · mañana ${MANANA}\n`);

/* las novedades están en la página */
const t = await (await fetch(BASE + '/')).text();
for (const [n, s] of [['bloque SIN HACER', 'SIN HACER'],
                      ['menú ¿para cuándo?', '¿Para cuándo lo pasas?'],
                      ['próxima vez', 'La próxima vez que yo vuelva'],
                      ['pasadas a este día', 'Pasadas a este día'],
                      ['la marca «venía del»', 'venía del']]) {
  ok(n, t.includes(s));
}

/* pasar una tarea a mañana */
const clave = `${HOY}|op|td0`;
let r = await post('/api/trasladar', { quien: 'op1', clave, destino: { f: MANANA, t: 'manana' } });
ok('se pasa a mañana', r.ok === true && r.traslados[clave], r);
ok('con la fecha', r.traslados[clave].f === MANANA, r.traslados[clave]);
ok('con el turno', r.traslados[clave].t === 'manana', r.traslados[clave]);

const e2 = await (await fetch(BASE + '/api/estado')).json();
ok('el estado lo devuelve', !!e2.traslados[clave], Object.keys(e2.traslados || {}));

/* la próxima vez */
const clave2 = `${HOY}|op|td1`;
r = await post('/api/trasladar', { quien: 'op1', clave: clave2, destino: { proxima: true } });
ok('«próxima vez» se guarda', r.traslados[clave2].proxima === true, r.traslados[clave2]);
ok('con quién', r.traslados[clave2].q === 'op1', r.traslados[clave2]);

/* quitar el destino */
r = await post('/api/trasladar', { clave: clave2, destino: null });
ok('se le puede quitar el destino', !r.traslados[clave2], r.traslados[clave2]);

/* errores */
r = await post('/api/trasladar', { clave: 'sinfecha', destino: { f: MANANA } });
ok('clave sin fecha se rechaza', r.ok === false, r);

/* limpieza: se quita SOLO lo que ha creado esta prueba */
await post('/api/trasladar', { clave, destino: null });

const e3 = await (await fetch(BASE + '/api/estado')).json();
ok('esta prueba no deja nada suyo', !e3.traslados[clave], e3.traslados[clave]);
console.log(`   (quedan ${Object.keys(e3.traslados || {}).length} traslados de otros)`);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
