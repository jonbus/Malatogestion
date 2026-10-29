/* El desplegable por letras: primero la letra, luego sus contactos.
   node .tools\probar-letras.mjs
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
  const proveedores = [
    { n: "Cadagua", cs: [{p:"Oficina", t:"946798229"}, {p:"Almudena", t:"600599840"}] },
    { n: "Campofrío", cs: [{p:"Ane", t:"677406795"}] },
    { n: "Digasa / Coaliment", cs: [{p:"Mikel", t:"670480183"}] },
    { n: "El Pozo", cs: [{p:"Manu", t:"656752003"}] },
    { n: "Nestlé (Ariza)", cs: [{p:"David", t:"653831646"}] },
    { n: "Vizcaína Alimentación", cs: [{p:"Mikel", t:"678281049"}] }
  ];
  let llamLetra = "", llamProv = "", llamCont = "";
  let PINTADOS = 0;
  function pinta(){ PINTADOS++; }
  ${sacar('letraDe')}
  ${sacar('letrasDisponibles')}
  ${sacar('contactosTodos')}
  ${sacar('elegirLetra')}
  return { letraDe, letrasDisponibles, contactosTodos, elegirLetra,
           pon: (l)=>{ llamLetra = l; },
           pintados: ()=> PINTADOS };
`)();

console.log('   === la letra de cada uno ===');
ok('Cadagua → C', G.letraDe('Cadagua') === 'C');
ok('Nestlé → N (sin tilde)', G.letraDe('Nestlé (Ariza)') === 'N', G.letraDe('Nestlé (Ariza)'));
ok('El Pozo → E', G.letraDe('El Pozo') === 'E');
ok('Vizcaína → V', G.letraDe('Vizcaína Alimentación') === 'V');

console.log('\n   === las letras que hay, en orden ===');
const letras = G.letrasDisponibles();
console.log('    ' + letras.join(' · '));
ok('salen las que existen', letras.join('') === 'CDENV', letras);
ok('en orden alfabético', letras.join('') === letras.slice().sort().join(''));

console.log('\n   === sin letra, no sale ningún contacto ===');
ok('la lista está vacía', G.contactosTodos().length === 0, G.contactosTodos().length);

console.log('\n   === con la C, solo los de la C ===');
G.pon('C');
const conC = G.contactosTodos();
ok('salen los de la C', conC.every(x => x.prov.n.charAt(0) === 'C'), conC.map(x => x.prov.n));
ok('Cadagua aporta sus dos contactos',
   conC.filter(x => x.prov.n === 'Cadagua').length === 2,
   conC.filter(x => x.prov.n === 'Cadagua').length);
ok('Campofrío aporta uno', conC.some(x => x.prov.n === 'Campofrío'));
ok('no se cuela ninguno de otra letra', !conC.some(x => x.prov.n === 'El Pozo'));

console.log('\n   === con la N ===');
G.pon('N');
ok('solo Nestlé', G.contactosTodos().every(x => x.prov.n === 'Nestlé (Ariza)'),
   G.contactosTodos().map(x => x.prov.n));

console.log('\n   === y en la pantalla ===');
ok('el desplegable de la letra', js.includes('id="ll-letra"'));
ok('la pista para elegirla', js.includes('Elige la letra y saldrán sus contactos'));
ok('el contacto solo tras la letra', js.includes('llamLetra') && js.includes('id="ll-prov"'));
ok('elegir letra repinta', js.includes('function elegirLetra'));

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
