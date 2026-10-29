/* Los bloques plegados: cerrados con su progreso, y se abren al tocarlos.
   node .tools\probar-plegables.mjs
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

const trozo = js.slice(js.indexOf('let PLEGADOS'), js.indexOf('function bloque('));

const G = new Function(`
  let marcas = {};
  let PINTADOS = 0;
  function hecha(k){ return !!marcas[k]; }
  function pinta(){ PINTADOS++; }
  ${trozo}
  return { plegar, cuentaBloque, PLEGADOS, pintados: ()=> PINTADOS,
           marcar: (k)=>{ marcas[k] = true; }, limpiar: ()=>{ marcas = {}; } };
`)();

console.log('   === cuenta cuántas van ===');
const tareas = [{ t: "a" }, { t: "b" }, { t: "c" }];
let c = G.cuentaBloque(tareas, "x");
ok('al principio, 0 de 3', c.hec === 0 && c.tot === 3, c);
G.marcar('x1');
c = G.cuentaBloque(tareas, "x");
ok('con una hecha, 1 de 3', c.hec === 1 && c.tot === 3, c);

console.log('\n   === las tareas por partes cuentan una a una ===');
G.limpiar();
const conPartes = [{ t: "limpiar", partes: ["suelo", "puertas", "baldas"] }];
c = G.cuentaBloque(conPartes, "y");
ok('son tres partes', c.tot === 3, c);
G.marcar('y0.0');
c = G.cuentaBloque(conPartes, "y");
ok('con una parte hecha, 1 de 3', c.hec === 1, c);

console.log('\n   === los avisos no cuentan ===');
G.limpiar();
const conAviso = [{ t: "a" }, { aviso: "esto es un cartel" }, { t: "b" }];
c = G.cuentaBloque(conAviso, "z");
ok('el cartel no es tarea', c.tot === 2, c);

console.log('\n   === se abre y se cierra ===');
ok('al principio está cerrado', G.PLEGADOS['p|Título'] === undefined);
G.plegar('p|Título');
ok('al tocarlo, abierto', G.PLEGADOS['p|Título'] === true, G.PLEGADOS['p|Título']);
ok('y repinta', G.pintados() >= 1, G.pintados());
G.plegar('p|Título');
ok('al volver a tocarlo, cerrado', G.PLEGADOS['p|Título'] === false,
   G.PLEGADOS['p|Título']);

console.log('\n   === en la pantalla ===');
ok('el bloque es tocable', js.includes('onclick="plegar(') && js.includes('class="bloque plega'));
ok('la flecha dice si está abierto', js.includes('class="flecha"'));
ok('dice cuántas van', js.includes('de ${cuenta.tot}'));
ok('y cuando está completo lo dice', js.includes('✓ completo'));
ok('el completo se cierra solo', js.includes('completo ? true :'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
