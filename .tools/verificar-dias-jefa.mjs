/* Verifica las tareas nuevas y el filtrado por día. */
const U = 'https://enrolled-myers-seating-snap.trycloudflare.com';

const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(25000) })).text();
console.log(`  KB: ${Math.round(t.length / 1024)}`);
const cosas = {
  'versión -15': 'v-2026-10-23-15',
  'Digasa (miércoles)': 'Digasa · preparar o adelantar el pedido',
  'Cofresa (miércoles)': 'Cofresa · preparar o adelantar el pedido',
  'Frutas Tito': 'Frutas Tito · precios y etiquetas',
  'los lunes, solo el lunes': 'if(W === "LUN")',
  'los martes, solo el martes': 'if(W === "MAR")',
  'los miércoles, solo el miércoles': 'if(W === "MIE")',
  'Frutas Tito lunes y viernes': 'W === "LUN" || W === "VIE"',
};
for (const [k, v] of Object.entries(cosas)) {
  console.log(`  ${t.includes(v) ? 'OK   ' : 'FALTA'}  ${k}`);
}
