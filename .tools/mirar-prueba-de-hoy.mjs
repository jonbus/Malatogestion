/* Mira qué se marcó en la prueba de hoy, para no borrar datos de nadie. */
const BASE = 'https://tienda-malato.netlify.app';
const d = await (await fetch(BASE + '/api/estado')).json();

const porPuesto = { op: [], co: [] };
for (const k of Object.keys(d.marcas)) {
  const [f, p, clave] = k.split('|');
  if (f !== d.dia) continue;
  (porPuesto[p] || (porPuesto[p] = [])).push({ clave, quien: d.marcas[k].q, hora: d.marcas[k].h });
}

console.log(`   día ${d.dia}\n`);
for (const p of Object.keys(porPuesto)) {
  const l = porPuesto[p];
  if (!l.length) continue;
  const quienes = [...new Set(l.map(x => x.quien))];
  console.log(`   ${p}: ${l.length} marcas · de ${quienes.join(', ')}`);
  const secciones = {};
  l.forEach(x => {
    const sec = String(x.clave).replace(/[0-9._]+$/, '');
    secciones[sec] = (secciones[sec] || 0) + 1;
  });
  console.log('      por bloque: ' + Object.entries(secciones)
    .sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}:${v}`).join(' · '));
  console.log('      horas: ' + [...new Set(l.map(x => x.hora))].sort().slice(0, 8).join(', '));
  console.log();
}

console.log('   fichajes de hoy:');
(d.fichajes || []).filter(f => f.dia === d.dia).forEach(f =>
  console.log(`      ${f.q} · ${f.p} · entró ${f.e}${f.s ? ' · salió ' + f.s : ' (sigue dentro)'}`));
