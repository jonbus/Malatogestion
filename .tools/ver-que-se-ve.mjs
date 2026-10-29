/* Comprueba exactamente lo que verá cada perfil en el calendario del 26/10. */
const U = 'http://127.0.0.1:8100';
const DIA_VISTA = '2026-10-26';

const e = await (await fetch(U + '/api/estado')).json();
const encargos = e.encargos || [];

/* así filtra la pestaña Calendario: por día, de cualquier puesto */
const losDelDia = encargos.filter(x => !x.hecho && (x.diario || x.f === DIA_VISTA));
console.log(`  día que se mira: ${DIA_VISTA}`);
console.log(`  el calendario muestra ${losDelDia.length} tarea(s) extra ese día:\n`);
for (const x of losDelDia) {
  console.log(`   · [${x.p}] ${x.t}`);
  (x.partes || []).forEach((p, i) => console.log(`        ${i + 1}. ${p}`));
}

console.log('\n  === lo que verá cada perfil EN SU PESTAÑA DEL DÍA ===');
for (const [puesto, etiqueta] of [['tienda', 'Tienda'], ['coordinacion', 'Coordinación'],
                                  ['gerencia', 'Jefa']]) {
  /* así filtra el bloque del día: por puesto y por día */
  const suyas = encargos.filter(x => !x.hecho && x.p === puesto &&
    (x.diario || x.f === DIA_VISTA));
  console.log(`   ${etiqueta.padEnd(14)} ${suyas.length} tarea(s)` +
    (suyas.length ? ': ' + suyas.map(x => x.t).join(' | ') : ''));
}

console.log('\n  === y hoy, 2026-10-23 ===');
for (const [puesto, etiqueta] of [['tienda', 'Tienda'], ['coordinacion', 'Coordinación'],
                                  ['gerencia', 'Jefa']]) {
  const suyas = encargos.filter(x => !x.hecho && x.p === puesto &&
    (x.diario || x.f === '2026-10-23'));
  console.log(`   ${etiqueta.padEnd(14)} ${suyas.length} tarea(s)` +
    (suyas.length ? ': ' + suyas.map(x => x.t).join(' | ') : ''));
}
