/* Prueba en vivo del calendario. Limpia lo que crea: no deja notas de prueba. */
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
const dentro = new Date(HOY + 'T12:00:00');
dentro.setDate(dentro.getDate() + 10);
const F = dentro.toLocaleDateString('en-CA');

console.log(`   hoy ${HOY} · la nota de prueba va al ${F}\n`);

/* 1 · está en la página */
const t = await (await fetch(BASE + '/')).text();
for (const [n, s] of [
  ['la pestaña Calendario', 'Calendario'],
  ['el calendario dibujado', 'pintaCalendario'],
  ['solo lo general y lo mío', 'notasDe'],
  ['el aviso de lo personal', 'solo lo ves tú'],
]) ok(n, t.includes(s));

/* 2 · una nota general */
const g = await post('/api/nota', { quien: 'prueba', fecha: F, texto: 'NOTA DE PRUEBA general', ambito: 'general' });
ok('guarda la general', g.ok && !!g.nota, g);
ok('con ámbito general', g.nota && g.nota.a === 'general', g.nota);
ok('con hora', g.nota && /^\d{2}:\d{2}$/.test(g.nota.h), g.nota);

/* 3 · una personal */
const p = await post('/api/nota', { quien: 'prueba', fecha: F, texto: 'NOTA DE PRUEBA personal', ambito: 'personal' });
ok('guarda la personal', p.nota && p.nota.a === 'personal', p.nota);
ok('con su dueña', p.nota && p.nota.q === 'prueba', p.nota);

/* 4 · las dos están en el estado */
const e2 = await (await fetch(BASE + '/api/estado')).json();
const mias = (e2.notas[F] || []).filter(n => n.q === 'prueba');
ok('las dos están guardadas', mias.length === 2, mias.length);
ok('una general y una personal',
   mias.some(n => n.a === 'general') && mias.some(n => n.a === 'personal'), mias);

/* 5 · borrar */
for (const n of mias) {
  const b = await post('/api/nota-borrar', { id: n.id });
  ok(`borra «${n.a}»`, b.borrada === 1, b);
}
const e3 = await (await fetch(BASE + '/api/estado')).json();
ok('no queda ninguna de prueba',
   (e3.notas[F] || []).filter(n => n.q === 'prueba').length === 0, e3.notas[F]);

/* 6 · errores */
ok('texto vacío se rechaza', (await post('/api/nota', { quien: 'prueba', fecha: F, texto: '  ' })).ok === false);
ok('fecha mala se rechaza', (await post('/api/nota', { quien: 'prueba', fecha: 'x', texto: 'hola' })).ok === false);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
