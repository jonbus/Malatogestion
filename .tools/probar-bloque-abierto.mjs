/* Llama al bloque de verdad y mira qué devuelve: cerrado o abierto.
   node .tools\probar-bloque-abierto.mjs
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
  let marcas = {};
  const REG = {}, ENC = {}, OPC = {}, PICK = {};
  const DATOS = { tienda: { productos: ["AL28"] } };
  const quien = { puesto: "tienda", id: "op1" };
  let PLEGADOS = {};
  let PINTADOS = 0;
  function hecha(k){ return !!marcas[k]; }
  function clave(k){ return k; }
  function claveEn(f, k){ return k; }
  function pinta(){ PINTADOS++; }
  function nombreDe(x){ return x; }
  function bonito(f){ return f; }
  ${sacar('claveBloque')}
  ${sacar('plegar')}
  ${sacar('cuentaBloque')}
  ${sacar('bloque')}
  return { bloque, PLEGADOS, pintados: ()=> PINTADOS,
           marcar: (k)=>{ marcas[k] = true; },
           plegarAqui: (c)=>{ PLEGADOS[c] = false; } };
`)();

const tareas = [{ t: "Frentear y reponer" }, { t: "Subir monta" }, { t: "Cocina: fregar" }];

console.log('   === tal como entra, sin tocar nada ===');
const cerrado = G.bloque("LO DE HOY", tareas, "m1");
console.log("   " + cerrado.slice(0, 220).replace(/\n/g, " "));

ok('sale el título', cerrado.includes('LO DE HOY'));
ok('dice cómo va', cerrado.includes('0 de 3'), cerrado.match(/<small>[^<]*<\/small>/));
ok('lleva la flecha de cerrado', cerrado.includes('▸'));
ok('NO lleva la lista', !cerrado.includes('class="lista"'), 'sí la lleva');
ok('NO lleva las tareas', !cerrado.includes('Frentear y reponer'), 'sí las lleva');
ok('el título se puede tocar', cerrado.includes('onclick="plegar('));

console.log('\n   === y cuando se abre ===');
G.plegarAqui('m1|LO DE HOY');
const abierto = G.bloque("LO DE HOY", tareas, "m1");
ok('ahora sí lleva la lista', abierto.includes('class="lista"'));
ok('y las tareas', abierto.includes('Frentear y reponer'));
ok('con la flecha abierta', abierto.includes('▾'));

console.log('\n   === y cuando está completo ===');
G.PLEGADOS = {};
['m10', 'm11', 'm12'].forEach(k => G.marcar(k));
const completo = G.bloque("LO DE HOY", tareas, "m1");
ok('lo dice', completo.includes('completo'));
ok('en verde', completo.includes('bloque-ok'));
ok('y se queda cerrado', !completo.includes('class="lista"'));
ok('aunque se hubiera abierto antes',
   (() => { G.PLEGADOS = { 'm1|LO DE HOY': false };
            const x = G.bloque("LO DE HOY", tareas, "m1");
            return !x.includes('class="lista"'); })());

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
