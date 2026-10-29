/* Simula el clic en «Añadir» con la casilla escrita, sin navegador.
   node .tools\probar-clic-tarea.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

function sacar(nombre) {
  let k = js.indexOf('async function ' + nombre + '(');
  if (k < 0) k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
}

console.log('   === la casilla manda, no la variable ===');

/* un navegador de mentira: las casillas tienen lo que el usuario escribe */
const casillas = {
  'tarea-txt': { value: 'Reponer el pan de molde' },
  'tarea-puesto': { value: 'tienda' },
  'tarea-turno': { value: 'tarde' },
  'tarea-tipo': { value: 'urgente' },
};
const enviado = [];
const avisos = [];

const entorno = `
  const NOMBRE_PUESTO = { tienda: "Tienda", coordinacion: "Coordinación", gerencia: "Jefa" };
  let textoTarea = "", puestoTarea = "tienda", turnoTarea = "", tipoTarea = "extra";
  let formTarea = true;
  let cascHijos = [], cascadas = {};
  const fechaSel = "2026-10-26";
  const quien = { id: "ge1" };
  const document = { getElementById: (id) => CASILLAS[id] || null };
  function ponerSync(estado, texto){ AVISOS.push([estado, texto]); }
  async function mandarEncargo(c){ ENVIADO.push(c); }
  function pinta(){}
  function bonito(f){ return f; }
`;
const F = new Function('CASILLAS', 'ENVIADO', 'AVISOS',
  entorno + sacar('valorDe') + sacar('anadirTareaExtra') +
  '\nreturn { anadirTareaExtra, estado: ()=>({ textoTarea, formTarea, tipoTarea }) };');
const M = F(casillas, enviado, avisos);

await M.anadirTareaExtra();

ok('se ha mandado algo', enviado.length === 1, enviado.length);
const c = enviado[0] || {};
ok('con el texto de la casilla', c.t === 'Reponer el pan de molde', c.t);
ok('al puesto de la casilla', c.p === 'tienda', c.p);
ok('con el turno de la casilla', c.turno === 'tarde', c.turno);
ok('con el tipo de la casilla', c.tipo === 'urgente', c.tipo);
ok('para hoy', c.f === '2026-10-26', c.f);

const est = M.estado();
ok('la casilla se vacía', est.textoTarea === '', est.textoTarea);
ok('el formulario se cierra', est.formTarea === false, est.formTarea);
ok('el tipo vuelve a extra', est.tipoTarea === 'extra', est.tipoTarea);

const ultimo = avisos[avisos.length - 1] || [];
ok('avisa de a dónde ha ido', ultimo[0] === 'ok' && String(ultimo[1]).includes('Tienda'),
  ultimo);

console.log('\n   === y si está vacía, avisa (no se queda callada) ===');
const casillas2 = { 'tarea-txt': { value: '   ' } };
const F2 = new Function('CASILLAS', 'ENVIADO', 'AVISOS',
  entorno.replace('let formTarea = true;', 'let formTarea = true;') +
  sacar('valorDe') + sacar('anadirTareaExtra') +
  '\nreturn { anadirTareaExtra };');
const enviado2 = [], avisos2 = [];
await F2(casillas2, enviado2, avisos2).anadirTareaExtra();
ok('no manda nada', enviado2.length === 0, enviado2.length);
ok('y dice por qué', (avisos2[0] || [])[0] === 'error' &&
   String((avisos2[0] || [])[1]).includes('Escribe'), avisos2);

console.log('\n   === el encargo lee también sus casillas ===');
const casillas3 = {
  'enc-que': { value: '1 txapata' }, 'enc-cli': { value: 'Carmen' },
  'enc-tipo': { value: 'rango' }, 'enc-desde': { value: '2026-11-05' },
  'enc-hasta': { value: '2026-11-09' }, 'enc-antes': { value: '1' },
  'enc-pide': { value: 'coordinacion' },
};
const entorno3 = `
  let encQue = "", encCliente = "", encTipo = "dia", encDesde = "", encHasta = "";
  let encDias = [], encAntes = "1", encPide = "coordinacion";
  let formEncargo = true;
  const fechaSel = "2026-10-26";
  const quien = { id: "ge1" };
  const document = { getElementById: (id) => CASILLAS[id] || null };
  function ponerSync(a, b){ AVISOS.push([a, b]); }
  async function mandarEncargo(){}
  function pinta(){}
  let encargosFecha = [];
  async function fetch(){ return { ok: true, json: async () => ({ encargosFecha: [] }) }; }
`;
const enviado3 = [], avisos3 = [];
const F3 = new Function('CASILLAS', 'ENVIADO', 'AVISOS',
  entorno3 + sacar('valorDe') + sacar('guardarEncargo') +
  '\nreturn { guardarEncargo };');
await F3(casillas3, enviado3, avisos3).guardarEncargo();
ok('el encargo no se queda en silencio', avisos3.length > 0, avisos3);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
