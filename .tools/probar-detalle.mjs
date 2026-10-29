/* Prueba del detalle para el proveedor.
   node .tools\probar-detalle.mjs
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
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
}

const entorno = `
  const DIA = "2026-10-26";
  const MESES_LARGOS = ["enero","febrero","marzo","abril","mayo","junio","julio",
                        "agosto","septiembre","octubre","noviembre","diciembre"];
  const PANES_TAHONA = [["txapata","Txapata"],["txapatita","Txapatita"],
    ["barra","Barra"],["cuarto","Cuarto"],["txoripan","Txoripan"]];
  function fechaBuena(f){ return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(f||"")) ? String(f) : "2026-10-26"; }
  let panDesde = "", panHasta = "";
  const tahona = {
    "2026-10-02": { entrada: {txapata:20, barra:40}, devolucion: {txapata:3, barra:5} },
    "2026-10-03": { entrada: {txapata:10, barra:20}, devolucion: {txapata:1, barra:2} },
    "2026-10-20": { entrada: {txapata:7}, devolucion: {} }
  };
`;
const F = new Function(entorno +
  sacar('mesPan') + sacar('rangoPan') + sacar('diasPan') + sacar('filasPan') +
  sacar('csvDetalle') +
  '\nreturn { csvDetalle, poner: (a,b)=>{ panDesde=a; panHasta=b; } };')();

console.log('   === el detalle para el proveedor ===');
F.poner('2026-10-02', '2026-10-20');
const csv = F.csvDetalle();
console.log(csv.split('\n').map(l => '     | ' + l).join('\n'));

ok('lleva la cabecera de la tienda', csv.includes('Malato · La tahona'));
ok('lleva el rango de fechas', csv.includes('Detalle del 02/10/2026 al 20/10/2026'));
ok('columnas: día, pan, entra, sale', csv.includes('DIA;PAN;ENTRA;SALE'));
ok('una línea por día y pan', csv.includes('02/10/2026;Txapata;20;3'));
ok('la barra del día 3', csv.includes('03/10/2026;Barra;20;2'));
ok('solo los días con algo', csv.includes('20/10/2026;Txapata;7;0'));
ok('no hay días vacíos',
  csv.split('\n').filter(l => /^\d\d\/\d\d\/\d{4};/.test(l)).length === 5,
  csv.split('\n').filter(l => /^\d\d\/\d\d\/\d{4};/.test(l)).length);
ok('lleva el total', csv.includes('TOTAL;;97;11'), csv.split('\n').find(l => l.startsWith('TOTAL')));
ok('dice el neto', csv.includes('Entradas menos devoluciones: 86'));
ok('y el resumen por pan al final', csv.includes('PAN;ENTRA;SALE;QUEDA'));

console.log('\n   === los botones ===');
ok('Resumen para Excel', js.includes('onclick="descargarPan()"'));
ok('Detalle por día para el proveedor', js.includes('onclick="descargarDetalle()"'));
ok('el nombre del archivo lleva el rango',
  js.includes('tahona-detalle-') && js.includes('a-'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
