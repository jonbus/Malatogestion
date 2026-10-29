/* Comprueba el martes y las ausencias en la versión del túnel. */
const U = 'https://gathered-daughters-attorney-cons.trycloudflare.com';

const t = await (await fetch(U + '/')).text();
const i = t.indexOf('"coord"');
const trozo = t.slice(i, i + 220);
console.log('  coord:', trozo);
console.log();
const j = t.indexOf('"ausencias"');
console.log('  ausencias:', t.slice(j, j + 130));
console.log();
console.log('  ¿el martes (1) está en la semana 1 de la Coordinadora 1?',
  /"1": \{"1": \{"0": 7\.5, "1": 7\.5/.test(t) ? 'SÍ (mal)' : 'no (bien)');
