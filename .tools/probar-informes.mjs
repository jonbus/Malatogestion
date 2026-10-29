/* Prueba del informe del pan: compartir y descargar.
   node .tools\probar-informes.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

console.log('   === las funciones están ===');
['mesPan', 'filasPan', 'textoPan', 'csvPan', 'compartirPan', 'descargarPan']
  .forEach(f => ok(f, js.includes('function ' + f) || js.includes('async function ' + f)));

console.log('\n   === los dos botones ===');
ok('Compartir', js.includes('onclick="compartirPan()"'));
ok('Descargar para Excel', js.includes('onclick="descargarPan()"'));

console.log('\n   === y el informe sale de verdad ===');
/* se ejecutan las funciones con unos datos de mentira */
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
  const tahona = {
    "2026-10-02": { entrada: {txapata:20, barra:40}, devolucion: {txapata:3, barra:5} },
    "2026-10-03": { entrada: {txapata:10, barra:20}, devolucion: {txapata:1, barra:2} },
    "2026-09-30": { entrada: {txapata:99} }
  };
`;
const F = new Function(entorno +
  sacar('mesPan') + sacar('filasPan') + sacar('textoPan') + sacar('csvPan') +
  '\nreturn { mesPan, filasPan, textoPan, csvPan };')();

const mes = F.mesPan();
console.log('\n   === el mes ===');
ok('octubre de 2026', mes.nombre === 'octubre de 2026', mes.nombre);

const filas = F.filasPan();
ok('salen los cinco panes', filas.length === 5, filas.length);
const tx = filas.find(f => f.nombre === 'Txapata');
ok('la txapata suma los dos días (30)', tx && tx.entra === 30, tx);
ok('y las devoluciones (4)', tx && tx.sale === 4, tx);
ok('queda 26', tx && tx.queda === 26, tx);
ok('no cuenta el pan de septiembre',
  filas.find(f => f.nombre === 'Txapata').entra === 30);

console.log('\n   === el texto para WhatsApp ===');
const texto = F.textoPan();
console.log(texto.split('\n').map(l => '     | ' + l).join('\n'));
ok('lleva el nombre de la tienda', texto.includes('MALATO'));
ok('lleva el mes', texto.includes('octubre de 2026'));
ok('lleva los cinco panes',
  ['Txapata','Txapatita','Barra','Cuarto','Txoripan'].every(p => texto.includes(p)));
ok('lleva el total', texto.includes('TOTAL'));
ok('lleva líneas de verdad', texto.split('\n').length >= 12, texto.split('\n').length);

console.log('\n   === el csv para Excel ===');
const csv = F.csvPan();
ok('lleva cabecera con punto y coma', csv.includes('Pan;Entra;Sale;Queda'));
ok('una fila por pan', csv.split('\n').filter(l => l.startsWith('Txapata')).length === 1);
ok('lleva el total', csv.includes('TOTAL;'));
ok('las cifras van con ;', csv.includes('Txapata;30;4;26'), csv.split('\n')[2]);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
