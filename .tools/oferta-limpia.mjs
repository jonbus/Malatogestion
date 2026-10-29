/* Deja UNA sola cascada de ofertas, limpia y con las fechas a la vista. */
const U = 'http://127.0.0.1:8100';
const post = (r, c) => fetch(U + r, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));
const get = (r) => fetch(U + r).then(async x => x.json());

const HOY = (await get('/api/estado')).dia;
const DESDE = '2026-10-26';
const HASTA = '2026-11-08';
const d = (f) => `${f.slice(8)}/${f.slice(5, 7)}`;      // 26/10
const PREP = 'ofertas:' + DESDE + ':prep';
const LIN = 'ofertas:' + DESDE + ':lineales';
const CAR = 'ofertas:' + DESDE + ':cartel';

/* --- 1) se borra todo lo de ofertas, para no dejar duplicados ---------- */
console.log('  === limpieza ===');
const e0 = await get('/api/estado');
for (const x of (e0.encargos || [])) {
  if (String(x.clave || '').startsWith('ofertas:')) {
    await post('/api/encargo-borrar', { id: x.id });
    console.log('   borrada: ' + String(x.clave).padEnd(34) + (x.hecho ? '[hecha]' : ''));
  }
}

/* --- 2) la Jefa da de alta las ofertas -------------------------------- */
console.log('\n  === la Jefa da de alta las ofertas ===');
const r1 = await post('/api/encargo', {
  quien: 'ge1',
  t: `Preparar las ofertas del ${d(DESDE)} al ${d(HASTA)}`,
  p: 'gerencia',
  f: HOY,
  que: `del ${d(DESDE)} al ${d(HASTA)}`,
  clave: PREP,
  partes: [
    `Dar de alta las ofertas (del ${d(DESDE)} al ${d(HASTA)})`,
    'Sacar las etiquetas',
    'Organizar los stoppers',
    'Marcar que está preparado'
  ],
  cascada: [
    { t: `Quitar las vencidas y pegar las nuevas · del ${d(DESDE)} al ${d(HASTA)}`,
      p: 'coordinacion', f: DESDE, clave: LIN,
      partes: ['Primero: quitar todas las vencidas',
               'Después: pegar las nuevas en los lineales'] },
    { t: `Pegar la cartelería grande · del ${d(DESDE)} al ${d(HASTA)}`,
      p: 'gerencia', f: DESDE, clave: CAR }
  ]
});
const prep = (r1.body.encargos || []).find(x => x.clave === PREP);
console.log(`   HTTP ${r1.status} · "${prep && prep.t}" para hoy (${HOY})`);

const e1 = await get('/api/estado');
console.log(`   la coordinadora la ve ANTES: ` +
  ((e1.encargos || []).some(x => x.clave === LIN) ? 'SÍ — MAL' : 'no (correcto)'));

/* --- 3) la Jefa la marca ---------------------------------------------- */
console.log('\n  === la Jefa termina de prepararlas ===');
const r2 = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
console.log(`   HTTP ${r2.status} · nacen ${r2.body.nacidos} tareas`);

/* --- 4) el resultado --------------------------------------------------- */
console.log('\n  === lo que hay ahora ===');
const e2 = await get('/api/estado');
for (const x of (e2.encargos || [])) {
  if (!String(x.clave || '').startsWith('ofertas:')) continue;
  console.log(`   ${x.hecho ? '[hecha]' : '[     ]'} ${x.p.padEnd(13)} ${x.f}  ${x.t}`);
  (x.partes || []).forEach((p, i) => console.log(`              ${i + 1}. ${p}`));
}

const lin = (e2.encargos || []).find(x => x.clave === LIN);
const car = (e2.encargos || []).find(x => x.clave === CAR);
console.log('\n  ==========================================================');
console.log('   LAS OFERTAS VAN DEL ' + d(DESDE) + ' AL ' + d(HASTA));
console.log('  ==========================================================');
console.log(`   Coordinadora · Calendario · ${DESDE}`);
console.log(`     ${lin ? '-> ' + lin.t : '-> NO LLEGÓ'}`);
console.log(`   Jefa · Calendario · ${DESDE}`);
console.log(`     ${car ? '-> ' + car.t : '-> NO LLEGÓ'}`);
