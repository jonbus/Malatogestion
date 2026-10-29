/* Prueba del núcleo, con un almacén falso en memoria.
   node docs/nube/prueba-nucleo.mjs
*/
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const nucleo = require('./netlify/functions/nucleo.js');

let fallos = 0;
function comprobar(nombre, condicion, extra) {
  console.log(`   ${condicion ? 'OK  ' : 'FALLO'}  ${nombre}${extra && !condicion ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!condicion) fallos++;
}

/* Almacén falso, con la misma forma que Netlify Blobs */
function almacenFalso() {
  const datos = new Map();
  return {
    _datos: datos,
    async get(clave, opciones) {
      const v = datos.get(clave);
      if (v === undefined) return null;
      return opciones && opciones.type === 'json' ? JSON.parse(v) : v;
    },
    async setJSON(clave, valor) { datos.set(clave, JSON.stringify(valor)); },
    async set(clave, valor) { datos.set(clave, valor); }
  };
}

const llamar = (manejar, metodo, ruta, cuerpo) =>
  manejar({ metodo, ruta, cuerpo: cuerpo ? JSON.stringify(cuerpo) : null });

const DIAS = nucleo.hoyISO('Europe/Madrid');
const haceDias = (n) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toLocaleDateString('en-CA', { timeZone: 'Europe/Madrid' });
};
console.log(`   (día de la tienda: ${DIAS})\n`);

/* ------------------------------------------------------------------ 1 */
{
  console.log(' 1) estado vacío al empezar');
  const m = nucleo.crearManejador({ store: almacenFalso() });
  const r = await llamar(m, 'GET', '/api/estado');
  comprobar('responde 200', r.status === 200, r);
  comprobar('sin marcas', Object.keys(r.body.marcas).length === 0, r.body.marcas);
  comprobar('día correcto', r.body.dia === DIAS, r.body.dia);
}

/* ------------------------------------------------------------------ 2 */
{
  console.log('\n 2) marcar tareas y que se guarden');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const k1 = DIAS + '|md0.1';
  const k2 = DIAS + '|md0.0';
  const r = await llamar(m, 'POST', '/api/marcas', { quien: 'op1', cambios: { [k1]: true, [k2]: true } });
  comprobar('aplicadas 2', r.body.aplicados === 2, r.body);
  comprobar('quién queda apuntado', true);
  const r2 = await llamar(m, 'GET', '/api/estado');
  comprobar('las 2 están', Object.keys(r2.body.marcas).length === 2, r2.body.marcas);
  comprobar('con autor', r2.body.marcas[k1].q === 'op1', r2.body.marcas[k1]);
  comprobar('con hora', /^\d{2}:\d{2}$/.test(r2.body.marcas[k1].h), r2.body.marcas[k1]);
  comprobar('la versión sube', r2.body.version >= 1, r2.body.version);
}

/* ------------------------------------------------------------------ 3 */
{
  console.log('\n 3) desmarcar');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const k = DIAS + '|t3.0';
  await llamar(m, 'POST', '/api/marcas', { quien: 'op1', cambios: { [k]: true } });
  await llamar(m, 'POST', '/api/marcas', { quien: 'op2', cambios: { [k]: false } });
  const r = await llamar(m, 'GET', '/api/estado');
  comprobar('ya no está', !r.body.marcas[k], r.body.marcas);
}

/* ------------------------------------------------------------------ 4 */
{
  console.log('\n 4) dos personas comparten las mismas marcas');
  const store = almacenFalso();
  const a = nucleo.crearManejador({ store });
  const b = nucleo.crearManejador({ store });
  await llamar(a, 'POST', '/api/marcas', { quien: 'op1', cambios: { [DIAS + '|a1']: true } });
  const vista = await llamar(b, 'GET', '/api/estado');
  comprobar('la segunda lo ve', !!vista.body.marcas[DIAS + '|a1'], vista.body.marcas);
  comprobar('y sabe quién fue', vista.body.marcas[DIAS + '|a1'].q === 'op1',
    vista.body.marcas[DIAS + '|a1']);
}

/* ------------------------------------------------------------------ 5 */
{
  console.log('\n 5) las marcas de OTRO día se ven, pero cada día tiene las suyas');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const HACE3 = haceDias(3);
  await llamar(m, 'POST', '/api/marcas', { quien: 'op1', cambios: { [HACE3 + '|vieja']: true } });
  await llamar(m, 'POST', '/api/marcas', { quien: 'op1', cambios: { [DIAS + '|hoy']: true } });
  const r = await llamar(m, 'GET', '/api/estado');
  comprobar('están las dos', Object.keys(r.body.marcas).length === 2, r.body.marcas);
  comprobar('con fechas distintas',
    Object.keys(r.body.marcas).some(k => k.startsWith(HACE3)) &&
    Object.keys(r.body.marcas).some(k => k.startsWith(DIAS)), r.body.marcas);
}

/* ------------------------------------------------------------------ 6 */
{
  console.log('\n 6) una clave sin fecha se ignora');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const r = await llamar(m, 'POST', '/api/marcas', { quien: 'op1', cambios: { 'sindecha': true } });
  comprobar('no aplica nada', r.body.aplicados === 0, r.body);
}

/* ------------------------------------------------------------------ 7 */
{
  console.log('\n 7) fichar: entrar, no duplicar, salir');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const e1 = await llamar(m, 'POST', '/api/fichar', { quien: 'op1', puesto: 'tienda' });
  comprobar('entrada apuntada', !!e1.body.entrada, e1.body);
  const e2 = await llamar(m, 'POST', '/api/fichar', { quien: 'op1', puesto: 'tienda' });
  comprobar('no duplica', e2.body.yaEstaba === true, e2.body);
  const r = await llamar(m, 'GET', '/api/estado');
  comprobar('un solo fichaje', r.body.fichajes.length === 1, r.body.fichajes);
  comprobar('del día de hoy', r.body.fichajes[0].dia === DIAS, r.body.fichajes[0]);
  const s = await llamar(m, 'POST', '/api/fichar', { quien: 'op1', puesto: 'tienda', salir: true });
  comprobar('salida apuntada', !!s.body.salida, s.body);
  const r2 = await llamar(m, 'GET', '/api/estado');
  comprobar('la salida queda', !!r2.body.fichajes[0].s, r2.body.fichajes);
}

/* ------------------------------------------------------------------ 8 */
{
  console.log('\n 8) errores claros');
  const m = nucleo.crearManejador({ store: almacenFalso() });
  const a = await llamar(m, 'POST', '/api/marcas', {});
  comprobar('sin cambios -> 400', a.status === 400, a);
  const b = await llamar(m, 'POST', '/api/fichar', {});
  comprobar('sin quién -> 400', b.status === 400, b);
  const c = await llamar(m, 'GET', '/api/no-existe');
  comprobar('ruta mala -> 404', c.status === 404, c);
}

/* ------------------------------------------------------------------ 9 */
{
  console.log('\n 9) poda: no se guarda para siempre');
  const estado = {
    version: 1,
    marcas: { '2020-01-01|vieja': { q: 'x', h: '10:00' }, [DIAS + '|hoy']: { q: 'x', h: '10:00' } },
    fichajes: [{ q: 'x', p: 'p', e: '10:00', s: null, dia: '2020-01-01' },
               { q: 'x', p: 'p', e: '10:00', s: null, dia: DIAS }]
  };
  const p = nucleo.podar(estado, 'Europe/Madrid');
  comprobar('tira la marca vieja', !p.marcas['2020-01-01|vieja'], p.marcas);
  comprobar('deja la de hoy', !!p.marcas[DIAS + '|hoy'], p.marcas);
  comprobar('tira el fichaje viejo', p.fichajes.length === 1, p.fichajes);
}

/* ------------------------------------------------------------------ 10 */
{
  console.log('\n 10) pasar una tarea a otro día');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const origen = DIAS + '|op|td0';
  const destino = haceDias(-2);
  const r = await llamar(m, 'POST', '/api/trasladar',
    { clave: origen, destino: { f: destino, t: 'manana' } });
  comprobar('responde 200', r.status === 200, r);
  comprobar('queda guardado', !!r.body.traslados[origen], r.body.traslados);
  comprobar('con la fecha de destino', r.body.traslados[origen].f === destino,
    r.body.traslados[origen]);
  comprobar('con el turno', r.body.traslados[origen].t === 'manana', r.body.traslados[origen]);
  const e = await llamar(m, 'GET', '/api/estado');
  comprobar('se ve en el estado', !!e.body.traslados[origen], e.body.traslados);
}

/* ------------------------------------------------------------------ 11 */
{
  console.log('\n 11) «la próxima vez que vuelva»');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const k = DIAS + '|op|td1';
  const r = await llamar(m, 'POST', '/api/trasladar',
    { quien: 'op1', clave: k, destino: { proxima: true } });
  comprobar('se guarda como próxima', r.body.traslados[k].proxima === true, r.body.traslados[k]);
  comprobar('con quién', r.body.traslados[k].q === 'op1', r.body.traslados[k]);
  comprobar('sin fecha', r.body.traslados[k].f === undefined, r.body.traslados[k]);
}

/* ------------------------------------------------------------------ 12 */
{
  console.log('\n 12) quitarle el destino (vuelve a «sin día»)');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const k = DIAS + '|op|td2';
  await llamar(m, 'POST', '/api/trasladar', { clave: k, destino: { f: haceDias(-1) } });
  const r = await llamar(m, 'POST', '/api/trasladar', { clave: k, destino: null });
  comprobar('ya no está', !r.body.traslados[k], r.body.traslados);
}

/* ------------------------------------------------------------------ 13 */
{
  console.log('\n 13) traslados mal hechos');
  const m = nucleo.crearManejador({ store: almacenFalso() });
  const a = await llamar(m, 'POST', '/api/trasladar', { destino: { f: DIAS } });
  comprobar('sin clave -> 400', a.status === 400, a);
  const b = await llamar(m, 'POST', '/api/trasladar', { clave: 'sinfecha', destino: { f: DIAS } });
  comprobar('clave sin fecha -> 400', b.status === 400, b);
  const c = await llamar(m, 'POST', '/api/trasladar',
    { clave: DIAS + '|op|x', destino: { f: 'mañana' } });
  comprobar('fecha mala -> 400', c.status === 400, c);
}

/* ------------------------------------------------------------------ 14 */
{
  console.log('\n 14) poda de traslados viejos');
  const estado = {
    version: 1, marcas: {}, fichajes: [],
    traslados: { '2020-01-01|op|viejo': { f: '2020-01-02' },
                 [DIAS + '|op|hoy']: { f: DIAS } }
  };
  const p = nucleo.podar(estado, 'Europe/Madrid');
  comprobar('tira el traslado viejo', !p.traslados['2020-01-01|op|viejo'], p.traslados);
  comprobar('deja el de hoy', !!p.traslados[DIAS + '|op|hoy'], p.traslados);
}

/* ------------------------------------------------------------------ 15 */
{
  console.log('\n 15) el calendario: notas generales y personales');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const f = haceDias(-5);   // un día futuro (haceDias con número negativo)

  const g = await llamar(m, 'POST', '/api/nota',
    { quien: 'co1', fecha: f, texto: 'Cierra a las 14:00', ambito: 'general' });
  comprobar('guarda una nota general', g.status === 200 && !!g.body.nota, g);
  comprobar('con ámbito general', g.body.nota.a === 'general', g.body.nota);
  comprobar('con quién la escribió', g.body.nota.q === 'co1', g.body.nota);
  comprobar('con hora', /^\d{2}:\d{2}$/.test(g.body.nota.h), g.body.nota);

  const p = await llamar(m, 'POST', '/api/nota',
    { quien: 'op1', fecha: f, texto: 'Pedir cambio de turno', ambito: 'personal' });
  comprobar('guarda una personal', p.body.nota.a === 'personal', p.body.nota);

  const e = await llamar(m, 'GET', '/api/estado');
  comprobar('las dos están', (e.body.notas[f] || []).length === 2, e.body.notas[f]);
}

/* ------------------------------------------------------------------ 16 */
{
  console.log('\n 16) borrar una nota');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const f = haceDias(-5);
  const a = await llamar(m, 'POST', '/api/nota',
    { quien: 'op1', fecha: f, texto: 'Una', ambito: 'general' });
  const b = await llamar(m, 'POST', '/api/nota',
    { quien: 'op1', fecha: f, texto: 'Otra', ambito: 'general' });
  const r = await llamar(m, 'POST', '/api/nota-borrar', { id: a.body.nota.id });
  comprobar('borra una', r.body.borrada === 1, r.body);
  const e = await llamar(m, 'GET', '/api/estado');
  comprobar('queda la otra', (e.body.notas[f] || []).length === 1, e.body.notas[f]);
  comprobar('y es la correcta', e.body.notas[f][0].id === b.body.nota.id, e.body.notas[f]);
}

/* ------------------------------------------------------------------ 17 */
{
  console.log('\n 17) notas mal hechas');
  const m = nucleo.crearManejador({ store: almacenFalso() });
  const a = await llamar(m, 'POST', '/api/nota', { quien: 'op1', fecha: 'mañana', texto: 'x' });
  comprobar('fecha mala -> 400', a.status === 400, a);
  const b = await llamar(m, 'POST', '/api/nota',
    { quien: 'op1', fecha: haceDias(-2), texto: '   ' });
  comprobar('texto vacío -> 400', b.status === 400, b);
  const c = await llamar(m, 'POST', '/api/nota', { fecha: haceDias(-2), texto: 'x' });
  comprobar('sin quién -> 400', c.status === 400, c);
  const d = await llamar(m, 'POST', '/api/nota-borrar', {});
  comprobar('borrar sin id -> 400', d.status === 400, d);
}

/* ------------------------------------------------------------------ 18 */
{
  console.log('\n 18) las notas futuras NO se podan');
  const futuro = new Date();
  futuro.setDate(futuro.getDate() + 20);
  const fFuturo = futuro.toLocaleDateString('en-CA', { timeZone: 'Europe/Madrid' });
  const estado = {
    version: 1, marcas: {}, fichajes: [], traslados: {},
    notas: { [fFuturo]: [{ id: 'a', q: 'op1', t: 'dentro de 20 días', a: 'general' }],
             '2020-01-01': [{ id: 'b', q: 'op1', t: 'muy vieja', a: 'general' }] }
  };
  const p = nucleo.podar(estado, 'Europe/Madrid');
  comprobar('guarda la futura', !!p.notas[fFuturo], p.notas);
  comprobar('tira la de hace años', !p.notas['2020-01-01'], p.notas);
}

/* ------------------------------------------------------------------ 19 */
{
  console.log('\n 19) la clave de gerencia');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store, pinGerencia: '583104' });

  const bien = await llamar(m, 'POST', '/api/entrar', { pin: '583104' });
  comprobar('con la buena, entra', bien.status === 200 && bien.body.ok === true, bien);
  comprobar('y dice que es gerencia', bien.body.puesto === 'gerencia', bien.body);

  const mal = await llamar(m, 'POST', '/api/entrar', { pin: '000000' });
  comprobar('con otra, no entra', mal.status === 401 && mal.body.ok === false, mal);

  const vacia = await llamar(m, 'POST', '/api/entrar', {});
  comprobar('sin clave, no entra', vacia.status === 401, vacia);

  const casi = await llamar(m, 'POST', '/api/entrar', { pin: '58310' });
  comprobar('con una parecida, tampoco', casi.status === 401, casi);

  const sin = nucleo.crearManejador({ store: almacenFalso() });
  const nada = await llamar(sin, 'POST', '/api/entrar', { pin: '583104' });
  comprobar('si no está configurada, no deja pasar', nada.status === 503, nada);
}

/* ------------------------------------------------------------------ 20 */
{
  console.log('\n 20) LA CASCADA: una tarea no nace hasta que la anterior se hace');
  const store = almacenFalso();
  const m = nucleo.crearManejador({ store });
  const lunes = haceDias(-3);          // tres días después de hoy

  const r = await llamar(m, 'POST', '/api/encargo', {
    quien: 'ge1', t: 'Preparar las ofertas', p: 'gerencia', f: DIAS,
    clave: 'ofertas:prep:prueba',
    cascada: [
      { t: 'Quitar las vencidas y pegar las nuevas', p: 'coordinacion',
        f: lunes, clave: 'ofertas:lineales:prueba' },
      { t: 'Pegar la cartelería grande', p: 'gerencia',
        f: lunes, clave: 'ofertas:cartel:prueba' }
    ]
  });
  comprobar('nace la primera', r.body.ok === true, r.body);
  const prep = (r.body.encargos || []).find(x => x.clave === 'ofertas:prep:prueba');
  ok_prep(comprobar, prep);

  /* antes de hacerla, los hijos NO existen */
  const antes = await llamar(m, 'GET', '/api/estado');
  const hijosAntes = (antes.body.encargos || []).filter(x =>
    ['ofertas:lineales:prueba', 'ofertas:cartel:prueba'].includes(x.clave));
  comprobar('los hijos NO existen todavía', hijosAntes.length === 0, hijosAntes.length);

  /* se marca la primera -> nacen las dos */
  const h = await llamar(m, 'POST', '/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
  comprobar('al hacerla nacen 2', h.body.nacidos === 2, h.body.nacidos);

  const despues = await llamar(m, 'GET', '/api/estado');
  const hijos = (despues.body.encargos || []).filter(x =>
    ['ofertas:lineales:prueba', 'ofertas:cartel:prueba'].includes(x.clave));
  comprobar('ahora sí existen', hijos.length === 2, hijos.length);
  comprobar('una es de coordinación',
    hijos.some(x => x.p === 'coordinacion'), hijos.map(x => x.p));
  comprobar('otra es de la oficina',
    hijos.some(x => x.p === 'gerencia'), hijos.map(x => x.p));
  comprobar('para el lunes', hijos.every(x => x.f === lunes), hijos.map(x => x.f));
  comprobar('y se sabe de dónde vienen',
    hijos.every(x => x.vieneDe === prep.id), hijos.map(x => x.vieneDe));

  /* marcarla otra vez no duplica los hijos */
  const otra = await llamar(m, 'POST', '/api/encargo-hecho', { id: prep.id, quien: 'ge1' });
  const fin = await llamar(m, 'GET', '/api/estado');
  const hijos2 = (fin.body.encargos || []).filter(x =>
    ['ofertas:lineales:prueba', 'ofertas:cartel:prueba'].includes(x.clave));
  comprobar('no se duplican', hijos2.length === 2, hijos2.length);
}

function ok_prep(comprobar, prep) {
  comprobar('con sus pasos', prep && Array.isArray(prep.cascada) && prep.cascada.length === 2,
    prep && prep.cascada);
}

console.log(`\n  ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
