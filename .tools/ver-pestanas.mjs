/* Verifica en la app servida que las pestañas de la Jefa están bien. */
const U = 'http://127.0.0.1:8100';
const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(20000) })).text();

console.log(`  versión: ${(t.match(/v-2026-10-23-\d+/) || ['?'])[0]}`);
console.log(`  «general» excluye a la Jefa: ${t.includes('tab === "general" && quien.puesto')}`);
console.log(`  pestañas de la Jefa: ${t.includes('["turno","Turno"]')
  ? 'General · Turno · Calendario' : '?'}`);
console.log(`  navegador de fechas para la Jefa: ${
  t.includes('(quien.puesto === "gerencia" && tab === "general")')}`);
console.log(`  lista de ofertas: ${t.includes('Dadas de alta · ')}`);
console.log(`  el título detrás de las fechas: ${
  t.indexOf('id="of-desde"') < t.indexOf('id="of-titulo"')}`);
