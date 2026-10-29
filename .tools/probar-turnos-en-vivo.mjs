/* Comprueba que los turnos están publicados. */
const BASE = 'https://tienda-malato.netlify.app';
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

const t = await (await fetch(BASE + '/')).text();
console.log(`   HTTP 200 · ${Math.round(t.length / 1024)} KB\n`);

for (const [n, s] of [
  ['la pestaña Turnos', '"turnos","Turnos"'],
  ['la función que calcula el turno', 'function turnoDe'],
  ['el ancla de tienda', '"tiendaAncla": "2026-10-19"'],
  ['el ancla del ciclo', '"cicloAncla": "2026-10-26"'],
  ['los 3 turnos de tienda', '"Fin de semana"'],
  ['las 4 semanas de coordinación', '"coord": {'],
  ['las 4 semanas de la oficina', '"oficina": {'],
  ['la semana dictada', '"tiendaSemana1": {'],
]) ok(n, t.includes(s));

const e = await (await fetch(BASE + '/api/estado')).json();
console.log(`\n   la función responde: dia=${e.dia}`);
ok('la app sigue viva', !!e.dia);

console.log(`\n   ${fallos === 0 ? 'TODO PUBLICADO' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
