/* Verifica la versión y la pestaña General en el aire. */
const U = 'https://enrolled-myers-seating-snap.trycloudflare.com';

const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(25000) })).text();
console.log(`  KB: ${Math.round(t.length / 1024)}`);
const cosas = {
  'versión -14': 'v-2026-10-23-14',
  'engancharItems definida': 'function engancharItems',
  'pestaña General': '"general","General"',
  'bandeja de la Jefa': '"bandeja","Bandeja"',
  'los clics se enganchan': 'engancharItems();',
  'dice Jefa': 'Jefa',
};
for (const [k, v] of Object.entries(cosas)) {
  console.log(`  ${t.includes(v) ? 'OK   ' : 'FALTA'}  ${k}`);
}
console.log(`  ya NO llama al enganchar inventado: ${!t.includes('  enganchar();')}`);
