/* Verifica las tres correcciones a través del túnel. */
const U = 'https://enrolled-myers-seating-snap.trycloudflare.com';

const r = await fetch(U + '/', { signal: AbortSignal.timeout(25000) });
const t = await r.text();
console.log(`  HTTP ${r.status} · ${Math.round(t.length / 1024)} KB`);
console.log(`  pie con marca de versión: ${t.includes('id="version"')}`);
console.log(`  vacaciones en los 7 días:  ${t.includes('ausenciaDe(g.puesto, g.numero, f)')}`);
console.log(`  dice «Jefa»:              ${t.includes('Jefa')}`);
console.log(`  dice «Oficina»:           ${t.includes('>Oficina<')}`);

console.log('\n  === la clave de la jefa ===');
const mau = await fetch(U + '/api/entrar', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pin: '000000' })
});
console.log(`  con clave mala: HTTP ${mau.status}`);

const bie = await fetch(U + '/api/entrar', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pin: '«la clave de la Jefa — se dice aparte, no se escribe»' })
});
const d = await bie.json();
console.log(`  con la buena:   HTTP ${bie.status} · ${JSON.stringify(d)}`);
