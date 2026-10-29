/* Prueba el cálculo de las ventanas del mes de gerencia,
   sacando las funciones del propio HTML.

   node .tools/probar-gerencia.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];

function sacar(nombre) {
  const i = script.indexOf('function ' + nombre + '(');
  if (i < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(i, k + 1); }
  }
  throw new Error('no cierro ' + nombre);
}
function sacarObjeto(marca) {
  const i = script.indexOf(marca);
  if (i < 0) throw new Error('no encuentro ' + marca);
  let prof = 0;
  for (let k = script.indexOf('{', i); k < script.length; k++) {
    if (script[k] === '{') prof++;
    else if (script[k] === '}') { prof--; if (prof === 0) return script.slice(script.indexOf('{', i), k + 1); }
  }
  throw new Error('no cierro ' + marca);
}

const DATOS = JSON.parse(sacarObjeto('const DATOS = '));
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];

const piezas = ['semanaDe', 'sumarDias', 'bonito', 'dosDig', 'esHabil',
                'ultimoHabilAntesDe', 'diasHasta', 'ventanasMes']
  .map(sacar).join('\n');

function cargar(DIA) {
  return new Function('DIA', 'DATOS', 'DIAS',
    piezas + `return { semanaDe, sumarDias, bonito, esHabil,
                       ultimoHabilAntesDe, diasHasta, ventanasMes };`
  )(DIA, DATOS, DIAS);
}

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

/* ---------------------------------------------------- días hábiles */
console.log('   === qué día es hábil ===');
{
  const F = cargar('2026-10-23');
  ok('un lunes normal lo es', F.esHabil('2026-10-19'));
  ok('un sábado NO', !F.esHabil('2026-10-17'));
  ok('un domingo NO', !F.esHabil('2026-10-18'));
  ok('el 12 de octubre (festivo, lunes) NO', !F.esHabil('2026-10-12'));
  ok('el 25 de julio (festivo) NO', !F.esHabil('2026-07-25'));
  ok('un viernes normal SÍ', F.esHabil('2026-10-16'));
}

/* ---------------------------------------------------- la hipoteca */
console.log('\n   === la hipoteca: el último hábil antes del 17 ===');
{
  const F = cargar('2026-11-02');
  /* noviembre 2026: el 17 es martes, el 16 lunes */
  ok('noviembre: el 16', F.ultimoHabilAntesDe(17, 11, 2026) === '2026-11-16',
     F.ultimoHabilAntesDe(17, 11, 2026));

  /* agosto 2026: el 17 es lunes, así que el 16 cae en domingo -> viernes 14 */
  ok('agosto: el 16 es domingo, se va al viernes 14',
     F.ultimoHabilAntesDe(17, 8, 2026) === '2026-08-14',
     F.ultimoHabilAntesDe(17, 8, 2026));

  /* comprobación de que el que devuelve siempre es hábil */
  let todos = true;
  for (let m = 1; m <= 12; m++) {
    const f = F.ultimoHabilAntesDe(17, m, 2026);
    if (!F.esHabil(f)) { todos = false; console.log(`      mes ${m} -> ${f} NO es hábil`); }
    if (f >= `2026-${String(m).padStart(2,'0')}-17`) { todos = false; }
  }
  ok('los 12 meses dan un día hábil anterior al 17', todos);
}

/* ---------------------------------------------------- las ventanas */
console.log('\n   === las ventanas, en dos días concretos ===');
{
  /* 23 de octubre: solo el extracto (del 20 al 30) */
  const F = cargar('2026-10-23');
  const v = F.ventanasMes();
  const porK = Object.fromEntries(v.map(x => [x.k, x]));
  ok('el 23/10 el extracto está abierto', porK.extracto.abierta === true, porK.extracto);
  ok('y la asesoría cerrada', porK.asesoria.abierta === false, porK.asesoria);
  ok('y la hipoteca cerrada', porK.hipoteca.abierta === false, porK.hipoteca);
  ok('y las horas cerradas', porK.horas.abierta === false, porK.horas);
  ok('el extracto vence el 30', porK.extracto.plazo === '2026-10-30', porK.extracto.plazo);

  /* 2 de noviembre: horas y asesoría e hipoteca abiertas */
  const F2 = cargar('2026-11-02');
  const v2 = F2.ventanasMes();
  const p2 = Object.fromEntries(v2.map(x => [x.k, x]));
  ok('el 2/11 las horas están abiertas', p2.horas.abierta === true, p2.horas);
  ok('y vencen el 3', p2.horas.plazo === '2026-11-03', p2.horas.plazo);
  ok('y la asesoría abierta', p2.asesoria.abierta === true, p2.asesoria);
  ok('y la hipoteca abierta', p2.hipoteca.abierta === true, p2.hipoteca);
  ok('y el extracto cerrado', p2.extracto.abierta === false, p2.extracto);

  /* 1 de diciembre: las horas siguen abiertas (hasta el 3) y la asesoría también */
  const F3 = cargar('2026-12-01');
  const v3 = Object.fromEntries(F3.ventanasMes().map(x => [x.k, x]));
  ok('el 1/12 las horas siguen abiertas', v3.horas.abierta === true, v3.horas);
  ok('y la asesoría también', v3.asesoria.abierta === true, v3.asesoria);
}

/* ---------------------------------------------------- los días que quedan */
console.log('\n   === cuántos días quedan ===');
{
  const F = cargar('2026-10-25');
  const v = Object.fromEntries(F.ventanasMes().map(x => [x.k, x]));
  ok('el 25/10 al extracto le quedan 5 días', v.extracto.dias === 5, v.extracto.dias);
  const G = cargar('2026-10-30');
  const w = Object.fromEntries(G.ventanasMes().map(x => [x.k, x]));
  ok('el 30/10 el extracto vence hoy', w.extracto.dias === 0, w.extracto.dias);
}

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
