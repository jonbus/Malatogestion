/* Comprueba el título de la oferta: lo que se manda al dar de alta.
   node .tools\probar-titulo-oferta.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

function sacar(nombre) {
  let k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  if (js.slice(Math.max(0, k - 6), k) === 'async ') k -= 6;   // conservar el async
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

/* se ejecuta darAltaOfertas con el entorno mínimo y se captura lo que manda */
function probar(titulo, desde, hasta) {
  const entorno = `
    const DIA = "2026-10-23";
    let formOfertas = true, ofertasDesde = ${JSON.stringify(desde)},
        ofertasHasta = ${JSON.stringify(hasta)}, ofertasTitulo = ${JSON.stringify(titulo)};
    let capturado = null;
    async function mandarEncargo(c){ capturado = c; }
    function pinta(){}
    function proximoLunes(){ return "2026-10-26"; }
  `;
  const cuerpo = entorno + sacar('darAltaOfertas') +
    '\nreturn (async () => { await darAltaOfertas();' +
    ' return { capturado, formOfertas, ofertasTitulo }; })();';
  return new Function(cuerpo)();
}

console.log('   === con título ===');
const r1 = await probar('Vuelta al cole', '2026-11-09', '2026-11-22');
const c1 = r1.capturado;
ok('la tarea lleva el título y las fechas',
  c1 && c1.t === 'Vuelta al cole · del 09/11 al 22/11', c1 && c1.t);
ok('va para la Jefa', c1 && c1.p === 'gerencia');
ok('tiene los 4 pasos', c1 && c1.partes.length === 4, c1 && c1.partes.length);
ok('el primer paso lleva las fechas',
  c1 && c1.partes[0] === 'Dar de alta las ofertas y poner el hasta · del 09/11 al 22/11',
  c1 && c1.partes[0]);
ok('nacen 2 hijas', c1 && c1.cascada.length === 2, c1 && c1.cascada.length);
ok('la de coordinación lleva título y fechas',
  c1 && c1.cascada[0].t === 'Vuelta al cole · cambiar los lineales · del 09/11 al 22/11',
  c1 && c1.cascada[0].t);
ok('la de la cartelería también',
  c1 && c1.cascada[1].t === 'Vuelta al cole · cartelería grande · del 09/11 al 22/11',
  c1 && c1.cascada[1].t);
ok('las dos van para el día de inicio', c1 && c1.cascada.every(x => x.f === '2026-11-09'));
ok('el formulario se cierra', r1.formOfertas === false);
ok('el título se limpia', r1.ofertasTitulo === '');

console.log('\n   === sin título (usa el de siempre) ===');
const r2 = await probar('', '2026-11-09', '2026-11-22');
ok('usa «Ofertas nuevas»',
  r2.capturado && r2.capturado.t === 'Ofertas nuevas · del 09/11 al 22/11',
  r2.capturado && r2.capturado.t);

console.log('\n   === sin fecha de fin ===');
const r3 = await probar('Navidad', '2026-12-21', '');
ok('dice solo el inicio',
  r3.capturado && r3.capturado.t === 'Navidad · desde el 21/12', r3.capturado && r3.capturado.t);

console.log('\n   === el formulario tiene el campo del título ===');
ok('existe el campo', html.includes('id="of-titulo"'));
ok('existe su manejador', html.includes('of-titulo") && document.getElementById') ||
  html.includes('getElementById("of-titulo")'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
