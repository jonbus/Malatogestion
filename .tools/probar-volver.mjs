/* Simula la barra de arriba: abrir una sección debe crear «◀ Menú».
   node .tools\probar-volver.mjs
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

/* una barra de mentira, como la de verdad */
const contenedor = { hijos: [], innerHTML: "", appendChild(b) { this.hijos.push(b); } };
const creados = [];
const H = new Function('C', 'CREADOS', `
  const quien = { puesto: "tienda" };
  let tab = "";
  const document = {
    getElementById: (id) => {
      if (id === "tabs") return C;
      return { innerHTML: "", textContent: "" };
    },
    createElement: () => {
      const b = { className: "", type: "", textContent: "", listeners: [],
                  setAttribute(){}, addEventListener(e, f){ this.listeners.push(f); },
                  click(){ this.listeners.forEach(f => f()); } };
      CREADOS.push(b);
      return b;
    }
  };
  let pintados = 0;
  function pinta(){ pintados++; }
  ${sacar('pintaTabs')}
  return { pintaTabs, tab: ()=> tab, pon: (v)=>{ tab = v; }, pintados: ()=> pintados };
`)(contenedor, creados);

console.log('   === en el menú, no hay barra ===');
H.pon('menu');
H.pintaTabs();
ok('no se crea ningún botón', creados.length === 0, creados.length);

console.log('\n   === al abrir una sección, sale «◀ Menú» ===');
H.pon('manana');
H.pintaTabs();
ok('se crea un botón', creados.length === 1, creados.length);
ok('dice «◀ Menú»', creados[0] && creados[0].textContent === '◀ Menú',
   creados[0] && creados[0].textContent);
ok('se pone en la barra', contenedor.hijos.length === 1, contenedor.hijos.length);

console.log('\n   === y al tocarlo, vuelve al menú ===');
creados[0].click();
ok('vuelve al menú', H.tab() === 'menu', H.tab());
ok('y repinta la pantalla', H.pintados() >= 1, H.pintados());
ok('la barra se vacía', contenedor.hijos.length === 1 && contenedor.innerHTML === "",
   { hijos: contenedor.hijos.length });

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
