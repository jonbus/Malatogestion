/* Simula el bloque del recuento tal como se pinta en la mañana de tienda.
   node .tools\simular-recuento-manana.mjs
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
}
let fallos = 0;
const ok = (n, c, extra) => {
  console.log(`   ${c ? 'OK  ' : 'FALLO'}  ${n}${!c && extra !== undefined ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!c) fallos++;
};

/* --- se monta el bloque con un entorno mínimo, como en la mañana de tienda --- */
const entorno = `
  const DIA = "2026-10-26";
  let fechaSel = "2026-10-26";
  let recuentos = {};
  const quien = { id: "op2", puesto: "tienda", numero: 2 };
  function fechaBuena(f){ return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(f || "")) ? String(f) : DIA; }
  function bonito(f){ return f; }
  function nombreDe(id){
    const s = String(id || "");
    if(!s) return "";
    if(s.startsWith("ge")) return "Jefa";
    const m = s.match(/^([a-z]+)([0-9]+)$/);
    if(!m) return s;
    if(m[1] === "op") return "Tienda " + m[2];
    if(m[1] === "co") return "Coordinadora " + m[2];
    return s;
  }
`;

const fab = new Function(entorno + sacar('lunesDe') + sacar('ddmm') +
  sacar('bloqueRecuento') + '\nreturn { bloqueRecuento, lunesDe, ddmm };');
const F = fab();

console.log('   === utilidades ===');
ok('el lunes del 26/10 es el 26/10', F.lunesDe('2026-10-26') === '2026-10-26',
  F.lunesDe('2026-10-26'));
ok('el lunes del 29/10 es el 26/10', F.lunesDe('2026-10-29') === '2026-10-26',
  F.lunesDe('2026-10-29'));
ok('una fecha mala no revienta', F.lunesDe('basura') === '2026-10-26', F.lunesDe('basura'));
ok('ddmm', F.ddmm('2026-10-26') === '26/10', F.ddmm('2026-10-26'));

console.log('\n   === el bloque, sin recuento apuntado ===');
let salida = '';
try { salida = F.bloqueRecuento(true, false); } catch (e) { salida = 'EXCEPCION: ' + e.message; }
ok('no revienta', !salida.startsWith('EXCEPCION'), salida);
ok('sale el título', salida.includes('Recuento del lunes 26/10'));
ok('los cuatro campos', ['pollos','codillos','patatas','bravas'].every(k => salida.includes('data-rec="' + k + '"')));
ok('el botón de guardar', salida.includes('rec-guardar'));
ok('sin histórico para tienda', !salida.includes('Los lunes anteriores'));

console.log('\n   === con datos y sin poder editar (la Jefa) ===');
const entorno2 = entorno.replace('let recuentos = {};',
  'let recuentos = {"2026-10-26":{"pollos":3,"codillos":5,"patatas":1,"bravas":0,"q":"co1","h":"09:14"}};');
const F2 = new Function(entorno2 + sacar('lunesDe') + sacar('ddmm') +
  sacar('bloqueRecuento') + '\nreturn bloqueRecuento;')();
let s2 = '';
try { s2 = F2(false, true); } catch (e) { s2 = 'EXCEPCION: ' + e.message; }
ok('no revienta', !s2.startsWith('EXCEPCION'), s2);
ok('enseña los números', s2.includes('>3<') || s2.includes('> 3<') || s2.includes('3'));
ok('dice quién lo apuntó', s2.includes('Coordinadora 1'), s2.slice(0, 200));
ok('sale el histórico', s2.includes('Los lunes anteriores'));

console.log('\n   === sin recuentos, con histórico pedido ===');
const F3 = new Function(entorno + sacar('lunesDe') + sacar('ddmm') +
  sacar('bloqueRecuento') + '\nreturn bloqueRecuento;')();
let s3 = '';
try { s3 = F3(false, true); } catch (e) { s3 = 'EXCEPCION: ' + e.message; }
ok('no revienta aunque no haya nada', !s3.startsWith('EXCEPCION'), s3);

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
