/* Verifica el cartel de error y la versión, en el aire. */
const U = 'https://enrolled-myers-seating-snap.trycloudflare.com';

const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(25000) })).text();
console.log(`  KB: ${Math.round(t.length / 1024)}`);
const cosas = {
  'versión -16': 'v-2026-10-23-16',
  'cartel de error': 'id="fallo"',
  'vigilante de errores': 'unhandledrejection',
  'enseñarFallo': 'function ensenarFallo',
  'engancharItems': 'function engancharItems',
  'la Jefa engancha': 'engancharItems();',
};
for (const [k, v] of Object.entries(cosas)) {
  console.log(`  ${t.includes(v) ? 'OK   ' : 'FALTA'}  ${k}`);
}
