/* Caza llamadas a funciones que no existen.
   Este fallo ya nos ha costado dos veces: `enganchar()` no estaba definida
   y la pantalla de la Jefa se cortaba en silencio.

   node .tools\probar-funciones.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];
    // el último <script> es el del programa

/* --- lo que se define --- */
const definidas = new Set();
for (const m of js.matchAll(/function\s+([A-Za-z_$][\w$]*)/g)) definidas.add(m[1]);
for (const m of js.matchAll(/(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\(|function)/g))
  definidas.add(m[1]);

/* --- lo que hay dentro de cada función --- */
function cuerpo(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) return '';
  let prof = 0;
  for (let x = js.indexOf('{', k); x < js.length; x++) {
    if (js[x] === '{') prof++;
    else if (js[x] === '}') { prof--; if (prof === 0) return js.slice(k, x + 1); }
  }
  return '';
}

/* --- lo que llama --- */
const llamadas = new Map();   // nombre -> en qué función se llama
for (const nombre of definidas) {
  const c = cuerpo(nombre);
  for (const m of c.matchAll(/(?<![.\w$])([a-z_$][\w$]*)\s*\(/g)) {
    const n = m[1];
    if (['if', 'for', 'while', 'switch', 'catch', 'return', 'typeof', 'function'].includes(n)) continue;
    if (!llamadas.has(n)) llamadas.set(n, new Set());
    llamadas.get(n).add(nombre);
  }
}

/* --- lo que existe fuera: del navegador o del lenguaje --- */
const NATIVAS = new Set([
  'parseInt', 'parseFloat', 'isNaN', 'String', 'Number', 'Boolean', 'Array', 'Object',
  'Date', 'JSON', 'Math', 'Set', 'Map', 'Promise', 'fetch', 'decodeURIComponent',
  'encodeURIComponent', 'setTimeout', 'clearTimeout', 'setInterval', 'alert', 'confirm',
  'prompt', 'RegExp', 'Error', 'Symbol', 'structuredClone', 'requestAnimationFrame',
]);

let fallos = 0;
const sospechosas = [];
for (const [nombre, desde] of [...llamadas].sort()) {
  if (definidas.has(nombre) || NATIVAS.has(nombre)) continue;
  sospechosas.push({ nombre, desde: [...desde] });
}

if (sospechosas.length === 0) {
  console.log(`  ${definidas.size} funciones definidas · ninguna llamada suelta`);
  console.log('\n  TODO BIEN');
} else {
  console.log(`  llamadas a funciones que NO existen:\n`);
  for (const s of sospechosas) {
    console.log(`   FALLO  ${s.nombre}()  ·  se llama desde ${s.desde.join(', ')}`);
    fallos++;
  }
  console.log(`\n  FALLOS: ${fallos}`);
}
process.exit(fallos === 0 ? 0 : 1);
