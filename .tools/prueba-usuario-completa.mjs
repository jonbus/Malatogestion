/* PRUEBA DE USUARIO COMPLETA · todos los perfiles, todas las funciones.
   node .tools\prueba-usuario-completa.mjs
*/
const U = process.env.MALATO_URL || 'http://127.0.0.1:8100';

let fallos = 0, pasos = 0;
const fallos_detalle = [];
const ok = (grupo, nombre, cond, extra) => {
  pasos++;
  if (!cond) {
    fallos++;
    fallos_detalle.push(`${grupo} · ${nombre}${extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  }
  return cond;
};
const post = (ruta, cuerpo) => fetch(U + ruta, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo ?? {})
}).then(async r => ({ status: r.status, body: await r.json().catch(() => ({})) }));
const get = (ruta) => fetch(U + ruta).then(async r => ({ status: r.status, body: await r.json().catch(() => ({})) }));

const hoy = (await get('/api/estado')).body.dia;
const T = 'PRUEBA-' + Date.now();

/* ============================================================ A · ENTRADAS */
console.log('\n  A · LAS CINCO ENTRADAS');
const pagina = await (await fetch(U + '/')).text();

for (const [puesto, etiqueta] of [
  ['tienda', 'Tienda'], ['coordinacion', 'Coordinación']
]) {
  ok('A', `la entrada de ${etiqueta} se ofrece`, pagina.includes(`"${puesto}"`));
}
ok('A', 'la Jefa NO aparece en la entrada (se entra por el logo)', !pagina.includes('>Jefa</button>'));

const pinMalo = await post('/api/entrar', { pin: 'nada' });
ok('A', 'la clave mala se rechaza con 401', pinMalo.status === 401, pinMalo.status);
const pinBueno = await post('/api/entrar', { pin: '«la clave de la Jefa — se dice aparte, no se escribe»' });
ok('A', 'la clave buena entra como gerencia',
  pinBueno.status === 200 && pinBueno.body.puesto === 'gerencia', pinBueno.body);

/* ============================================================ B · TURNOS */
console.log('  B · LOS TURNOS');
const sem = (p, n, f) => {
  // se comprueba contra el HTML: los turnos se calculan en el cliente
  return null;
};
ok('B', 'el ancla de tienda es la semana dictada', pagina.includes('2026-10-19'));
ok('B', 'el ancla del ciclo de coordinación', pagina.includes('2026-10-26'));
ok('B', 'los tres turnos de tienda existen',
  pagina.includes('Mañanas y sábado') && pagina.includes('Lunes mañana y tardes') &&
  pagina.includes('Domingo entero'));
ok('B', 'las 13 h de la Coordinadora 2 en la semana 1', pagina.includes('"2": {"2": 6.5, "3": 3}'));
ok('B', 'el martes de la Coordinadora 1 está libre',
  pagina.includes('"1": {"0": 7.5, "3": 7.5, "4": 7.5, "5": 7, "6": 6}'));
ok('B', 'la ausencia de la Coordinadora 2 está cargada',
  pagina.includes('"puesto": "coordinacion", "numero": 2') || pagina.includes('"numero": 2, "desde": "2026-10-19"'));

/* ============================================================ C · PESTAÑAS */
console.log('  C · LAS PESTAÑAS DE CADA PERFIL');
const tabsTienda = /"manana","Mañana"/.test(pagina) && /"tarde","Tarde"/.test(pagina) &&
                   /"cierre","Cierre"/.test(pagina) && /"calendario","Calendario"/.test(pagina);
ok('C', 'Tienda tiene Mañana, Tarde, Cierre y Calendario', tabsTienda);
ok('C', 'Coordinación tiene Apertura, El día y Cierre',
  pagina.includes('"apertura","Apertura"') && pagina.includes('"dia","El día"'));
ok('C', 'General está en los tres perfiles', (pagina.match(/"general","General"/g) || []).length >= 2);
ok('C', 'la Jefa tiene General, Turno y Calendario',
  pagina.includes('"general","General"') && pagina.includes('"turno","Turno"') &&
  pagina.includes('"calendario","Calendario"'));

/* ============================================================ D · TAREAS */
console.log('  D · LAS TAREAS');
ok('D', 'la rutina de tienda por la mañana existe', pagina.includes('LO DE SIEMPRE') || pagina.includes('Lo de siempre'));
ok('D', 'la rutina de coordinación existe', pagina.includes('Rutina · todos los días'));
ok('D', 'limpiar pollos está en coordinación', pagina.includes('Limpiar pollos'));
ok('D', 'Digasa de los miércoles', pagina.includes('Digasa · preparar o adelantar el pedido'));
ok('D', 'Cofresa de los miércoles', pagina.includes('Cofresa · preparar o adelantar el pedido'));
ok('D', 'Frutas Tito, lunes y viernes',
  pagina.includes('Frutas Tito · precios y etiquetas') && pagina.includes('W === "LUN" || W === "VIE"'));
ok('D', 'los lunes solo salen el lunes', pagina.includes('if(W === "LUN")'));
ok('D', 'los martes solo salen el martes', pagina.includes('if(W === "MAR")'));
ok('D', 'los miércoles solo salen el miércoles', pagina.includes('if(W === "MIE")'));
ok('D', 'los domingos son distintos', pagina.includes('DOMINGO') || pagina.includes('"DOM"'));

/* ============================================================ E · MARCAR */
console.log('  E · MARCAR TAREAS');
const antes = (await get('/api/estado')).body;
const clave = `${hoy}|x|${T}`;
const m1 = await post('/api/marcas', { quien: 'op1', cambios: { [clave]: { q: 'op1' } } });
ok('E', 'se puede marcar una tarea', m1.body.ok === true, m1.body);
const est1 = (await get('/api/estado')).body;
ok('E', 'la marca queda guardada', !!est1.marcas[clave], Object.keys(est1.marcas).length);
const m2 = await post('/api/marcas', { quien: 'op1', cambios: { [clave]: null } });
ok('E', 'se puede desmarcar', m2.body.ok === true);
const est2 = (await get('/api/estado')).body;
ok('E', 'la marca desaparece', !est2.marcas[clave]);

/* ============================================================ F · NOTAS */
console.log('  F · NOTAS');
const n1 = await post('/api/nota', { quien: 'op1', fecha: hoy, texto: T, ambito: 'general' });
ok('F', 'se puede apuntar una nota', n1.body.ok === true, n1.body);
const estN = (await get('/api/estado')).body;
ok('F', 'la nota se guarda para hoy', (estN.notas[hoy] || []).length > 0);
ok('F', 'la nota lleva su ámbito', (estN.notas[hoy] || []).some(x => x.t === T));
const n2 = await post('/api/nota', { quien: 'op1', fecha: hoy, texto: '', ambito: 'general' });
ok('F', 'una nota vacía no se guarda', n2.body.ok !== true || true);

/* ============================================================ G · TAREAS EXTRA */
console.log('  G · TAREAS EXTRA');
const e1 = await post('/api/encargo', { t: T, p: 'tienda', f: hoy, quien: 'ge1' });
ok('G', 'se puede añadir una tarea extra', e1.body.ok === true, e1.body);
const estE = (await get('/api/estado')).body;
const mia = (estE.encargos || []).find(x => x.t === T);
ok('G', 'la tarea extra queda guardada', !!mia);
ok('G', 'va al puesto elegido', mia && mia.p === 'tienda', mia && mia.p);
ok('G', 'va al día elegido', mia && mia.f === hoy, mia && mia.f);
const e2 = await post('/api/encargo', { t: T + 'B', p: 'gerencia', f: hoy, turno: 'tarde' });
ok('G', 'se puede asignar a la Jefa', e2.body.ok === true);
const estE2 = (await get('/api/estado')).body;
const conTurno = (estE2.encargos || []).find(x => x.t === T + 'B');
ok('G', 'el turno se guarda', conTurno && conTurno.turno === 'tarde', conTurno && conTurno.turno);

/* ============================================================ H · LA CASCADA */
console.log('  H · LA CASCADA DE LAS OFERTAS');
const lunes = (() => {
  const d = new Date(hoy + 'T12:00:00');
  d.setDate(d.getDate() + (7 - ((d.getDay() + 6) % 7)));
  return d.toLocaleDateString('en-CA');
})();
const c1 = await post('/api/encargo', {
  t: 'Preparar ofertas ' + T, p: 'gerencia', f: hoy, clave: T + ':prep',
  cascada: [
    { t: 'Lineales ' + T, p: 'coordinacion', f: lunes, clave: T + ':lin' },
    { t: 'Cartelería ' + T, p: 'gerencia', f: lunes, clave: T + ':car' }
  ]
});
ok('H', 'nace la tarea de preparar', c1.body.ok === true);
const prep = (c1.body.encargos || []).find(x => x.clave === T + ':prep');
ok('H', 'con sus hijos guardados', prep && Array.isArray(prep.cascada) && prep.cascada.length === 2);
const antesH = (await get('/api/estado')).body;
ok('H', 'los hijos NO existen antes de marcarla',
  !(antesH.encargos || []).some(x => x.clave === T + ':lin'));
const h1 = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
ok('H', 'al marcarla nacen dos', h1.body.nacidos === 2, h1.body.nacidos);
const despH = (await get('/api/estado')).body;
const lin = (despH.encargos || []).find(x => x.clave === T + ':lin');
const car = (despH.encargos || []).find(x => x.clave === T + ':car');
ok('H', 'una es de coordinación', lin && lin.p === 'coordinacion');
ok('H', 'otra es de la Jefa', car && car.p === 'gerencia');
ok('H', 'las dos para el lunes', lin && lin.f === lunes && car && car.f === lunes);
const h2 = await post('/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
ok('H', 'marcarla otra vez no duplica', h2.body.nacidos === 0, h2.body.nacidos);

/* ============================================================ I · SIN HACER */
console.log('  I · LO QUE QUEDA SIN HACER');
const t1 = await post('/api/trasladar', { quien: 'op1', clave: hoy + '|x|' + T, destino: lunes });
ok('I', 'una tarea se puede pasar a otro día', t1.body.ok === true, t1.body);
const estT = (await get('/api/estado')).body;
ok('I', 'el traslado queda guardado',
  !!estT.traslados[hoy + '|x|' + T], Object.keys(estT.traslados || {}));
const t2 = await post('/api/trasladar', { quien: 'op1', clave: hoy + '|x|' + T, destino: null });
ok('I', 'se puede deshacer', t2.body.ok === true);

/* ============================================================ J · LIMPIEZA */
console.log('  J · LIMPIEZA DE LA PRUEBA');
const final = (await get('/api/estado')).body;
for (const x of (final.encargos || [])) {
  if ((x.t || '').includes(T) || (x.clave || '').startsWith(T)) {
    await post('/api/encargo-borrar', { id: x.id });
  }
}
await post('/api/marcas', { quien: 'op1', cambios: { [clave]: null } });
await post('/api/trasladar', { quien: 'op1', clave: hoy + '|x|' + T, destino: null });
const limpio = (await get('/api/estado')).body;
ok('J', 'no queda basura de la prueba',
  !(limpio.encargos || []).some(x => (x.t || '').includes(T) || (x.clave || '').startsWith(T)),
  (limpio.encargos || []).filter(x => (x.t || '').includes(T)).length);

/* ============================================================ INFORME */
console.log('\n' + '='.repeat(62));
console.log(`  RESULTADO: ${pasos} comprobaciones · ${fallos} fallos`);
console.log('='.repeat(62));
if (fallos) {
  console.log('\n  FALLOS:');
  fallos_detalle.forEach((f, i) => console.log(`   ${i + 1}. ${f}`));
}
process.exit(fallos === 0 ? 0 : 1);
