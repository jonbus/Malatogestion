/* Comprueba que ya no aparecen tareas de antes del arranque.
   node .tools\probar-arranque.mjs
*/
import fs from 'node:fs';

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

console.log('   === la marca de arranque ===');
ok('existe ARRANQUE', js.includes('const ARRANQUE = "2026-10-26"'));
ok('«sin hacer» la respeta', js.includes('if(f < ARRANQUE) continue;'));

/* --- se simula el bloque «sin hacer» --- */
const entorno = `
  const DIA = "2026-10-26";
  let fechaSel = "2026-10-26";
  const DIAS_ATRAS = 7;
  const ARRANQUE = "2026-10-26";
  const quien = { puesto: "tienda" };
  const traslados = {};
  const marcas = {};
  function fechaBuena(f){ return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(f || "")) ? String(f) : DIA; }
  function sumarDias(f, n){
    const [a, m, d] = f.split("-").map(Number);
    const x = new Date(a, m - 1, d); x.setDate(x.getDate() + n);
    return x.toLocaleDateString("en-CA");
  }
  function semanaDe(f){
    const p = f.split("-").map(Number);
    return ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date(p[0], p[1]-1, p[2]).getDay()];
  }
  function claveEn(f, k){ return f + "|op|" + k; }
  function hechaEn(f, k){ return !!marcas[claveEn(f, k)]; }
  /* una tarea en todos los días de la semana, ninguna marcada */
  function tablaDia(){
    const t = {};
    ["LUN","MAR","MIE","JUE","VIE","SAB","DOM"].forEach(d => { t[d] = [{ t: "Algo" }]; });
    return t;
  }
`;
const F = new Function(entorno + sacar('sinDia') + '\nreturn sinDia;')();

const hoy = F('m');
console.log('\n   === «sin hacer» mirando desde el lunes 26 ===');
ok('no aparecen tareas de antes del arranque', hoy.length === 0,
  hoy.map(x => x.f));

/* y si el arranque fuera antes, sí aparecerían */
const F2 = new Function(entorno.replace('const ARRANQUE = "2026-10-26";',
  'const ARRANQUE = "2026-10-01";') + sacar('sinDia') + '\nreturn sinDia;')();
const antes = F2('m');
ok('con un arranque anterior sí se miran los días de atrás', antes.length > 0, antes.length);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
