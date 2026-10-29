/* Verifica el clic delegado en el aire. */
const U = 'https://enrolled-myers-seating-snap.trycloudflare.com';

const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(25000) })).text();
console.log(`  KB: ${Math.round(t.length / 1024)}`);
const cosas = {
  'versión -17': 'v-2026-10-23-17',
  'atenderClic definida': 'function atenderClic',
  'un solo escuchador': 'addEventListener("click", atenderClic)',
  'ya NO engancha uno a uno': !t.includes('  engancharItems();'),
  'cartel de error': 'id="fallo"',
  'engancharItems ya no se define': 'function engancharItems',
};
for (const [k, v] of Object.entries(cosas)) {
  const ok = typeof v === 'boolean' ? v : t.includes(v);
  console.log(`  ${ok ? 'OK   ' : 'FALTA'}  ${k}`);
}
