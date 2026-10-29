/* El menú de botones: simula entrar, abrir una sección y volver.
   node .tools\probar-menu.mjs
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

/* el trozo del menú, tal cual está en la aplicación */
const cuerpo = js.slice(js.indexOf('const MENU_POR_PUESTO'),
                        js.indexOf('function pintaPanes'));

const G = new Function('PINTADO', `
  const quien = { puesto: "tienda" };
  let tab = "";
  let encargos = [{ t: "Una extra", p: "tienda", f: "2026-10-26", hecho: false }];
  let tahona = {}, encargosFecha = [], recuentos = {};
  const DIA = "2026-10-26";
  let fechaSel = "2026-10-26";
  const NOMBRE_PUESTO = { tienda: "Tienda 1", coordinacion: "Coordinadora 1", gerencia: "Jefa" };
  function bonito(f){ return f; }
  function pinta(){ PINTADO.n++; }
  function bloqueEncargosAviso(){ return "AVISO-ENCARGO"; }
  function avisoExtras(){ return "AVISO-EXTRA"; }
  function bloqueArreglar(){ return "ARREGLAR"; }
  const CREADOS = [];
  const document = {
    getElementById: (id) => {
      if (id === "cuerpo") return { set innerHTML(v){ CREADOS.push(v); }, get innerHTML(){ return ""; } };
      return { textContent: "" };
    }
  };
  ${cuerpo}
  return { pintaMenu, abrirSeccion, MENU_POR_PUESTO, extrasPendientes,
           creados: CREADOS, tab: ()=> tab };
`) ({ n: 0 });

/* se necesita el contador dentro, se pasa por closure */
const contador = { n: 0 };
const H = new Function('C', `
  const quien = { puesto: "tienda" };
  let tab = "";
  let encargos = [{ t: "Una extra", p: "tienda", f: "2026-10-26", hecho: false }];
  let tahona = {}, encargosFecha = [], recuentos = {};
  const DIA = "2026-10-26";
  let fechaSel = "2026-10-26";
  const NOMBRE_PUESTO = { tienda: "Tienda 1", coordinacion: "Coordinadora 1", gerencia: "Jefa" };
  function bonito(f){ return f; }
  function pinta(){ C.n++; }
  function pintaTabs(){}
  function bloqueEncargosAviso(){ return "AVISO-ENCARGO"; }
  function avisoExtras(){ return "AVISO-EXTRA"; }
  function bloqueArreglar(){ return "ARREGLAR"; }
  const CREADOS = [];
  const document = {
    getElementById: (id) => {
      if (id === "cuerpo") return { set innerHTML(v){ CREADOS.push(v); }, get innerHTML(){ return ""; } };
      return { textContent: "" };
    }
  };
  ${cuerpo}
  return { pintaMenu, abrirSeccion, MENU_POR_PUESTO, extrasPendientes,
           creados: CREADOS, tab: ()=> tab };
`)(contador);

H.pintaMenu();
const salida = H.creados[0] || "";

console.log('   === el menú ===');
ok('los avisos, lo primero', salida.startsWith('AVISO-ENCARGOAVISO-EXTRAARREGLAR'),
   salida.slice(0, 40));
ok('tienda tiene seis botones', H.MENU_POR_PUESTO.tienda.length === 6,
   H.MENU_POR_PUESTO.tienda);
ok('coordinación tiene seis', H.MENU_POR_PUESTO.coordinacion.length === 6);

console.log('\n   === sus nombres ===');
['Calendario', 'Registro de panes', 'Tareas extra', 'Mañana', 'Tarde', 'Cierre']
  .forEach(n => ok('«' + n + '»', salida.includes(n)));
['Apertura', 'El día'].forEach(n =>
  ok('coordinación: «' + n + '»', H.MENU_POR_PUESTO.coordinacion.some(x => x[1] === n)));

console.log('\n   === cada botón funciona ===');
ok('seis órdenes dentro', (salida.match(/onclick="abrirSeccion\(/g) || []).length === 6,
   (salida.match(/onclick="abrirSeccion\(/g) || []).length);
ok('cuenta las extra pendientes', salida.includes('menu-num') && salida.includes('>1<'));
ok('y el botón cambia de color', salida.includes('con-pendientes'));

console.log('\n   === abrir y volver ===');
H.abrirSeccion('manana');
ok('cambia de sección', H.tab() === 'manana', H.tab());
ok('y repinta', contador.n >= 1, contador.n);
ok('hay vuelta al menú', js.includes('◀ Menú'));
ok('vuelve al menú', js.includes('tab = "menu"; pintaTabs(); pinta();'));

console.log('\n   === el pan, en su sitio ===');
ok('fuera de la apertura', !js.includes('bloqueTahona("entrada")'));
ok('fuera del cierre', !js.includes('bloqueTahona("devolucion")'));
ok('la sección del pan existe', js.includes('function pintaPanes'));
ok('la de las extra también', js.includes('function pintaExtra'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
