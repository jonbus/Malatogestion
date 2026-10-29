/* ¿Se abre el panel de modificar? Y que la pantalla suba.
   node .tools\probar-modificar.mjs
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
  let editando = "";
  let encargos = [{ id: "abc", t: "Tarea de prueba", p: "coordinacion", turno: "tarde", tipo: "extra", f: "2026-10-28" }];
  const fechaSel = "2026-10-28";
  let PINTADOS = 0;
  function pinta(){ PINTADOS++; }
  const window = { scrollTo(){} };
  ${sacar('abrirEdicion')}
  ${sacar('panelEdicion')}
  return { abrirEdicion, panelEdicion, estado: ()=> editando, pintados: ()=> PINTADOS };
`)();

console.log('   === al tocar «✎ modificar» ===');
ok('antes no hay panel', G.panelEdicion() === "");
G.abrirEdicion('abc');
ok('se abre', G.estado() === 'abc', G.estado());
ok('repinta', G.pintados() >= 1, G.pintados());

const panel = G.panelEdicion();
console.log('   ' + panel.slice(0, 200).replace(/\n/g, ' '));
ok('sale el panel', panel.includes('MODIFICAR LA TAREA') || panel.includes('Modificar la tarea'));
ok('con el texto actual', panel.includes('Tarea de prueba'));
ok('con el puesto', panel.includes('id="ed-p"'));
ok('con el turno', panel.includes('id="ed-turno"'));
ok('con el tipo', panel.includes('id="ed-tipo"'));
ok('con el día', panel.includes('id="ed-f"'));
ok('y el botón de guardar', panel.includes('Guardar los cambios'));

console.log('\n   === y la pantalla sube sola ===');
ok('abrirEdicion sube arriba', js.includes('window.scrollTo') || js.includes('scrollTo(0'));
ok('abrirCascadaDe sube arriba',
   sacar('abrirCascadaDe').includes('scrollTo') || js.includes('window.scrollTo'));

console.log('\n   === en la pantalla de la Jefa ===');
const i = js.indexOf('function pintaGerencia');
ok('el panel está en la Jefa', js.indexOf('panelEdicion()', i) > i);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
