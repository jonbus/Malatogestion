/* El mensaje del pedido, comprobado con datos de mentira. */
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

function trozo(nombre) {
  const k = js.indexOf('function ' + nombre + '(');
  let prof = 0;
  for (let i = js.indexOf('{', k); i < js.length; i++) {
    if (js[i] === '{') prof++;
    else if (js[i] === '}') { prof--; if (prof === 0) return js.slice(k, i + 1); }
  }
  throw new Error('no encuentro ' + nombre);
}

const G = new Function(`
  const DIA = "2026-11-04";
  const encargosFecha = [
    { que: "Zuaza", producto: "Casero", cantidad: 20, nota: "", desde: "2026-11-05" },
    { que: "Zuaza", producto: "Barra Casera", cantidad: 60, nota: "antes de las 9", desde: "2026-11-05" },
    { que: "Zuaza", producto: "Molde", cantidad: 10, nota: "", desde: "2026-11-06" },
    { que: "Tahona", producto: "Txapata", cantidad: 10, nota: "", desde: "2026-11-05" },
    { que: "25 pollos", producto: null, cantidad: null, nota: "", desde: "2026-11-05" }
  ];
  ${trozo('diaDeManana')}
  ${trozo('textoPedidoProveedor')}
  return { diaDeManana, textoPedidoProveedor };
`)();

console.log('   mañana es:', G.diaDeManana());
console.log('');
console.log('   === el mensaje a Zuaza (Patxi) ===');
console.log(G.textoPedidoProveedor('Zuaza').split('\n').map(l => '   | ' + l).join('\n') || '   (vacío)');
console.log('');
console.log('   === el mensaje a la Tahona (Jon) ===');
console.log(G.textoPedidoProveedor('Tahona').split('\n').map(l => '   | ' + l).join('\n') || '   (vacío)');

const zu = G.textoPedidoProveedor('Zuaza');
console.log('');
const ok = (n, c) => console.log(`   ${c ? 'OK   ' : 'FALLO'} ${n}`);
ok('solo lo de mañana (no el Molde del 6)', !zu.includes('Molde'));
ok('la cantidad va delante', zu.includes('20 Casero'));
ok('la nota va entre paréntesis', zu.includes('(antes de las 9)'));
ok('no se cuela un encargo de Varios', !zu.includes('pollos'));
ok('lleva la cabecera', zu.startsWith('Kaixo, tenemos encargado para mañana:'));
ok('lleva la despedida', zu.includes('Mila esker,') && zu.trim().endsWith('Malato'));
