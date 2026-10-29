/* Prueba del informe con rango y corrección.
   node .tools\probar-informe-rango.mjs
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
    "2026-10-20": { entrada: {txapata:7}, devolucion: {} },
    "2026-09-30": { entrada: {txapata:99} }
  };
`;
const F = new Function(entorno +
  sacar('mesPan') + sacar('rangoPan') + sacar('diasPan') + sacar('filasPan') +
  sacar('nombreRango') + sacar('textoPan') + sacar('csvPan') +
  '\nreturn { mesPan, rangoPan, diasPan, filasPan, nombreRango, textoPan, csvPan,' +
  '\n         poner: (a,b)=>{ panDesde=a; panHasta=b; } };')();

console.log('   === por defecto, el mes entero ===');
const mes = F.mesPan();
ok('octubre de 2026', mes.nombre === 'octubre de 2026', mes.nombre);
ok('del 1 al 31', mes.desde === '2026-10-01' && mes.hasta === '2026-10-31',
  [mes.desde, mes.hasta]);

console.log('\n   === un rango a mano ===');
F.poner('2026-10-02', '2026-10-03');
ok('el rango es el pedido', F.nombreRango() === 'del 02/10 al 03/10', F.nombreRango());
const dias = F.diasPan();
ok('solo esos dos días', dias.length === 2, dias);
const tx = F.filasPan().find(f => f.nombre === 'Txapata');
ok('la txapata suma 30', tx.entra === 30, tx);
ok('no entra el día 20 ni septiembre',
  !dias.includes('2026-10-20') && !dias.includes('2026-09-30'));

console.log('\n   === un rango al revés se ordena solo ===');
F.poner('2026-10-20', '2026-10-02');
ok('desde el 2 hasta el 20', F.nombreRango() === 'del 02/10 al 20/10', F.nombreRango());
ok('entran tres días', F.diasPan().length === 3, F.diasPan());

console.log('\n   === el texto para WhatsApp, sin columnas ===');
F.poner('2026-10-02', '2026-10-03');
const texto = F.textoPan();
console.log(texto.split('\n').map(l => '     | ' + l).join('\n'));
ok('una línea por pan, más el total',
  texto.split('\n').filter(l => l.includes(': ')).length === 6,
  texto.split('\n').filter(l => l.includes(': ')).length);
ok('lleva el neto', texto.includes('Txapata: 26'), texto);
ok('y el desglose', texto.includes('(30 − 4)'));
ok('lleva el rango', texto.includes('del 02/10 al 03/10'));
ok('no hay columnas de espacios', !/ {4,}Entra/.test(texto));

console.log('\n   === el csv lleva el detalle por día ===');
const csv = F.csvPan();
ok('la tabla resumen', csv.includes('Pan;Entra;Sale;Queda'));
ok('el detalle día a día', csv.includes('Día;Pan;Entra;Sale'));
ok('una línea del 2/10', csv.includes('2026-10-02;Txapata;20;3'),
  csv.split('\n').filter(l => l.startsWith('2026-10-02')));

console.log('\n   === la pantalla ===');
ok('los dos campos de fecha', js.includes('id="pan-desde"') && js.includes('id="pan-hasta"'));
ok('el botón «Este mes»', js.includes('Este mes'));
ok('corregir un día', js.includes('Corregir un día'));
ok('las diez casillas', js.includes('data-pane') && js.includes('data-pand'));
ok('guardar ese día', js.includes('guardarPanDia'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
