/* ¿Qué pasa al tocar «cuando se haga, crear…»?
   node .tools\probar-boton-cascada.mjs
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

const G = new Function(`
  const REG = {};
  const NOMBRE_PUESTO = { tienda: "Tienda", coordinacion: "Coordinación", gerencia: "Jefa" };
  const quien = { puesto: "coordinacion" };
  let cascadas = { "limpiar pollos": [{ que: "Reponer", p: "tienda" }] };
  let cascPara = "", cascHijos = [];
  let PINTADOS = 0;
  function hijoNuevo(){ return { que: "", p: "tienda", turno: "", cuando: "0" }; }
  function filaHijo(h, i){ return "FILA:" + (h.que || "") + ";"; }
  function pinta(){ PINTADOS++; }
  ${sacar('normNombre')}
  ${sacar('cascadaDe')}
  ${sacar('abrirCascadaDe')}
  ${sacar('cerrarCascada')}
  ${sacar('panelCascada')}
  return { abrirCascadaDe, panelCascada, cerrarCascada,
           reg: REG, estado: ()=>({ cascPara, cascHijos: cascHijos.length }),
           pintados: ()=> PINTADOS };
`)();

console.log('   === al tocar el botón de una tarea del día ===');
G.reg['mr3'] = { t: "Limpiar pollos" };
ok('antes no hay panel', G.panelCascada() === "");
G.abrirCascadaDe('mr3');
const est = G.estado();
ok('se abre la cascada de esa tarea', est.cascPara === 'Limpiar pollos', est.cascPara);
ok('y repinta la pantalla', G.pintados() >= 1, G.pintados());
ok('trae lo que ya tenía', est.cascHijos === 1, est.cascHijos);

const panel = G.panelCascada();
ok('sale el panel', panel.includes('CASCADA DE') || panel.includes('Limpiar pollos'));
ok('con su fila para escribir', panel.includes('FILA:'));
ok('y el botón de guardar', panel.includes('Guardar la cascada'));
ok('y el de cancelar', panel.includes('Cancelar'));

console.log('\n   === si la tarea no existe, no rompe ===');
G.cerrarCascada();
G.abrirCascadaDe('noexiste');
ok('no se abre nada', G.estado().cascPara === '', G.estado().cascPara);

console.log('\n   === en la pantalla ===');
ok('el botón lleva su orden', js.includes('abrirCascadaDe('));
ok('el panel está arriba del día', js.includes('let html = panelCascada()'));
ok('la función existe', js.includes('function abrirCascadaDe'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
