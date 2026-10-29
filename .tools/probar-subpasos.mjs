/* Demuestra que la Jefa puede marcar los sub-pasos.
   node .tools\probar-subpasos.mjs
*/
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

function sacar(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  if (k < 0) throw new Error('no encuentro ' + nombre);
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
  throw new Error('no cierro ' + nombre);
}

let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

const entorno = `
  const ARR = {}; const PAS = {}; const REG = {}; const ENC = {}; const PICK = {};
  const tocados = [];
  function tocar(k, v){ tocados.push(["tocar", k, v]); }
  function tocarEn(f, k, v){ tocados.push(["tocarEn", f, k, v]); }
  function hecha(k){ return false; }
  function hechaEn(f, k){ return false; }
  function pinta(){ tocados.push(["pinta"]); }
  function ponerSync(){}
  function origenDe(k){ return PAS[k] || null; }
  function encargoHecho(id){ tocados.push(["encargoHecho", id]); }
`;

const fabrica = new Function(entorno + sacar('atenderClic') +
  '\nreturn { atenderClic, tocados };');
const E = fabrica();

/* nodos falsos, con closest de verdad */
const nodo = (sel, dataset, padre) => ({
  sel,
  dataset: dataset || {},
  padre: padre || null,
  closest(s) {
    let n = this;
    while (n) { if (n.sel === s) return n; n = n.padre; }
    return null;
  }
});
const evento = (target) => ({ target, stopPropagation() {}, preventDefault() {} });

const item = nodo('.item', { k: 'gh0' });
const cab = nodo('.cab-item', {}, item);
const partes = nodo('.partes', {}, cab);
const parte = nodo('.parte', { parte: 'gh0.2' }, partes);

console.log('   === clic en un sub-paso (entrando como Jefa) ===');
E.tocados.length = 0;
E.atenderClic(evento(parte));
ok('el sub-paso se marca', E.tocados.some(t => t[0] === 'tocar' && t[1] === 'gh0.2'), E.tocados);
ok('no marca la tarea entera', !E.tocados.some(t => t[0] === 'tocar' && t[1] === 'gh0'), E.tocados);

console.log('\n   === clic en el título de la tarea ===');
const item2 = nodo('.item', { k: 'gh0' });
const cab2 = nodo('.cab-item', {}, item2);
E.tocados.length = 0;
E.atenderClic(evento(cab2));
ok('la tarea entera responde', E.tocados.length > 0, E.tocados);

console.log('\n   === un clic en un desplegable NO marca nada ===');
const sel = nodo('select', {}, cab2);
E.tocados.length = 0;
E.atenderClic(evento(sel));
ok('el desplegable no toca la tarea', E.tocados.length === 0, E.tocados);

console.log('\n   === un clic en el menú de pasar tampoco ===');
const menu = nodo('.menu-pasar', {}, cab2);
E.tocados.length = 0;
E.atenderClic(evento(menu));
ok('el menú no toca la tarea', E.tocados.length === 0, E.tocados);

console.log('\n   === abrir el menú de pasar sí funciona ===');
const btn = nodo('.btn-pasar', { pasar: 'sd0' }, cab2);
E.tocados.length = 0;
E.atenderClic(evento(btn));
ok('el menú se abre', E.tocados.some(t => t[0] === 'pinta'), E.tocados);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
