/* Borra los fichajes de prueba que quedaron de mis comprobaciones.
   Solo borra los que sé que son falsos: 'op9' (no existe) y 'prueba'. */
const BASE = 'https://tienda-malato.netlify.app';

const d = await (await fetch(BASE + '/api/estado')).json();
const falsos = (d.fichajes || []).filter(f => f.q === 'op9' || f.q === 'prueba');

console.log(`   fichajes en total: ${(d.fichajes || []).length}`);
console.log(`   falsos encontrados: ${falsos.length}`);

for (const f of falsos) {
  const r = await fetch(BASE + '/api/olvidar', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fichaje: { q: f.q, dia: f.dia, e: f.e } })
  }).then(x => x.json());
  console.log(`   ${f.q} (${f.dia} ${f.e}) -> borrados: ${r.borrados}`);
}

const d2 = await (await fetch(BASE + '/api/estado')).json();
console.log('\n   fichajes que quedan:');
(d2.fichajes || []).forEach(f =>
  console.log(`      ${f.q} · ${f.p} · ${f.dia} · ${f.e}${f.s ? '→' + f.s : ' (abierto)'}`));
