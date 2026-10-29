/* Comprueba qué sale en «Viene en los próximos días» con los datos reales.
   node .tools\probar-viene.mjs
*/
import fs from 'node:fs';

const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta, Object.assign({
  headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
  opciones || {}));
const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

function sacar(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
}
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

/* la prueba crea sus propias tareas: no depende de que haya datos */
const CLAVES = ['viene:prueba:coord', 'viene:prueba:jefa'];
for (const c of (await (await pedir('/api/estado')).json()).encargos || []) {
  if (CLAVES.includes(String(c.clave))) {
    await pedir('/api/encargo-borrar', { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: c.id }) });
  }
}
const hoyISO = '2026-10-26';
await pedir('/api/encargo', { method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA Quitar las vencidas y pegar las nuevas',
    p: 'coordinacion', f: '2026-10-28', clave: CLAVES[0] }) });
await pedir('/api/encargo', { method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA Pegar la cartelería grande',
    p: 'gerencia', f: '2026-10-28', clave: CLAVES[1] }) });

const estado = await (await pedir('/api/estado')).json();
const HOY = hoyISO;

const entorno = `
  const encargos = ${JSON.stringify(estado.encargos || [])};
  const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],
                ["JUE","Jueves"],["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
  const NOMBRE_PUESTO = { tienda: "Tienda", coordinacion: "Coordinación", gerencia: "Jefa" };
  function sumarDias(f, n){
    const d = new Date(f + "T12:00:00"); d.setDate(d.getDate() + n);
    return d.toLocaleDateString("en-CA");
  }
  function semanaDe(f){
    const p = f.split("-").map(Number);
    const w = (new Date(p[0], p[1]-1, p[2]).getDay() + 6) % 7;
    return ["LUN","MAR","MIE","JUE","VIE","SAB","DOM"][w];
  }
`;
const bloqueViene = new Function(entorno + sacar('bloqueViene') + '\nreturn bloqueViene;')();

const salida = bloqueViene(HOY);
console.log(`   hoy: ${HOY}`);
console.log('   === lo que se pinta ===');
console.log('   ' + (salida ? salida.replace(/\s+/g, ' ').slice(0, 420) + '…' : '(vacío)'));

console.log('\n   === comprobaciones ===');
ok('aparece el bloque hoy', salida.includes('Viene en los próximos días'));
ok('sale la tarea de coordinación',
  salida.includes('PRUEBA Quitar las vencidas'));
ok('sale la cartelería de la Jefa', salida.includes('PRUEBA Pegar la cartelería'));
ok('sale el día 26', salida.includes('28/10'));
ok('dice el puesto de cada una',
  salida.includes('Coordinación') && salida.includes('Jefa'));
ok('no es marcable', !salida.includes('cab-item') && !salida.includes('data-k'));
ok('avisa de que solo se mira', salida.includes('solo para mirar'));

/* y desde el propio 26 ya no debe anunciarlas */
const elMismoDia = bloqueViene('2026-10-28');
ok('el mismo día ya no las anuncia', !elMismoDia.includes('28/10'), elMismoDia.slice(0, 120));

/* limpieza */
for (const c of (await (await pedir('/api/estado')).json()).encargos || []) {
  if (CLAVES.includes(String(c.clave))) {
    await pedir('/api/encargo-borrar', { method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: c.id }) });
  }
}

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
