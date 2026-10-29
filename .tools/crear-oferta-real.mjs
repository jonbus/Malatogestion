/* Crea una oferta real y comprueba que la cascada llega a coordinación.
   node .tools\crear-oferta-real.mjs
*/
const U = 'http://127.0.0.1:8100';

const post = (r, c) => fetch(U + r, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));
const get = (r) => fetch(U + r).then(async x => x.json());

const HOY = (await get('/api/estado')).dia;
const DESDE = '2026-10-26';   // lunes en que empiezan
const HASTA = '2026-11-08';   // domingo en que terminan (2 semanas)
const PREP = 'ofertas:' + DESDE + ':prep';
const LIN = 'ofertas:' + DESDE + ':lineales';
const CAR = 'ofertas:' + DESDE + ':cartel';

console.log(`  hoy: ${HOY}`);
console.log(`  las ofertas van del ${DESDE} al ${HASTA}\n`);

/* --- 1) la Jefa da de alta las ofertas -------------------------------- */
console.log('  === 1 · la Jefa da de alta las ofertas ===');
const r1 = await post('/api/encargo', {
  quien: 'ge1',
  t: `Preparar las ofertas del ${DESDE.slice(8)}/${DESDE.slice(5,7)} al ${HASTA.slice(8)}/${HASTA.slice(5,7)}`,
  p: 'gerencia',
  f: HOY,
  que: 'hasta el ' + HASTA,
  clave: PREP,
  partes: [
    'Dar de alta las ofertas y poner el hasta',
    'Sacar las etiquetas',
    'Organizar los stoppers',
    'Marcar que está preparado'
  ],
  cascada: [
    { t: `Quitar las ofertas vencidas y pegar las nuevas (del ${DESDE.slice(8)}/${DESDE.slice(5,7)} al ${HASTA.slice(8)}/${HASTA.slice(5,7)})`,
      p: 'coordinacion', f: DESDE, clave: LIN,
      partes: ['Primero: quitar todas las vencidas',
               'Después: pegar las nuevas en los lineales'] },
    { t: 'Pegar la cartelería grande',
      p: 'gerencia', f: DESDE, clave: CAR }
  ]
});
const prep = (r1.body.encargos || []).find(x => x.clave === PREP);
console.log(`   HTTP ${r1.status} · la tarea de preparar ${prep ? 'creada para hoy' : 'NO creada'}`);

/* --- 2) ¿la ve la Jefa? ----------------------------------------------- */
const e1 = await get('/api/estado');
const paraJefa = (e1.encargos || []).filter(x => x.p === 'gerencia' && !x.hecho);
console.log(`   la Jefa tiene ${paraJefa.length} tarea(s) extra sin hacer hoy`);

/* --- 3) ¿la ve ya la coordinadora? NO debe verla ------------------------ */
const antesCoord = (e1.encargos || []).filter(x => x.p === 'coordinacion' && x.clave === LIN);
console.log(`   la coordinadora la ve ANTES de marcarla: ${antesCoord.length === 0 ? 'NO (correcto)' : 'SÍ — MAL'}`);

/* --- 4) la Jefa la marca ---------------------------------------------- */
console.log('\n  === 2 · la Jefa termina de prepararlas ===');
const r2 = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
console.log(`   HTTP ${r2.status} · nacen ${r2.body.nacidos} tareas nuevas`);

/* --- 5) ¿le llega a la coordinadora? ---------------------------------- */
console.log('\n  === 3 · ¿le llega a la coordinadora? ===');
const e2 = await get('/api/estado');
const lin = (e2.encargos || []).find(x => x.clave === LIN);
const car = (e2.encargos || []).find(x => x.clave === CAR);

if (lin) {
  console.log(`   SÍ  · "${lin.t}"`);
  console.log(`        para el ${lin.f} · puesto: ${lin.p} · ${(lin.partes||[]).length} pasos`);
  (lin.partes || []).forEach((p, i) => console.log(`          ${i+1}. ${p}`));
} else {
  console.log('   NO le ha llegado · FALLO');
}
console.log(`   cartelería para la Jefa: ${car ? 'sí, el ' + car.f : 'NO'}`);

/* --- resumen ---------------------------------------------------------- */
console.log('\n  ==============================================');
console.log('   LO QUE TIENES QUE VER');
console.log('  ==============================================');
console.log(`   Como COORDINADORA · pestaña Calendario · día ${DESDE}`);
console.log(`   -> "Quitar las ofertas vencidas y pegar las nuevas"`);
console.log(`   Como JEFA · pestaña Calendario · día ${DESDE}`);
console.log(`   -> "Pegar la cartelería grande"`);
console.log(`   Las ofertas: del ${DESDE} al ${HASTA}`);
