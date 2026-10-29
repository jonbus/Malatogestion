/* Comprueba que las ofertas dadas de alta van DENTRO del bloque «Las ofertas». */
import fs from 'node:fs';

const U = 'https://app.supermalato.workers.dev';
/* Cloudflare rechaza a los programas que no se identifican como navegador */
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta, Object.assign({
  headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
  opciones || {}));
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

/* --- 1 · está dentro del bloque, no en uno aparte --- */
ok('el bloque «Las ofertas» recibe su lista',
  html.includes('bloque("Las ofertas", DATOS.gerencia.ofertas, "go", listaOfertas())'));
ok('ya no hay bloque suelto de ofertas', !html.includes('Ofertas dadas de alta</h2>'));
ok('existe listaOfertas', js.includes('function listaOfertas'));

/* --- 2 · con los datos reales --- */
const estado = await (await pedir('/api/estado')).json();
const entorno = `
  const encargos = ${JSON.stringify(estado.encargos || [])};
  const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],
                ["JUE","Jueves"],["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
  const DIA = "2026-10-23";
  function fechaBuena(f){ return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(f||"")) ? String(f) : DIA; }
  function semanaDe(f){
    f = fechaBuena(f);
    const [a, m, d] = f.split("-").map(Number);
    return ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date(a, m - 1, d).getDay()];
  }
`;
const listaOfertas = new Function(entorno + sacar('listaOfertas') + '\nreturn listaOfertas;')();
/* la prueba crea su propia oferta: no depende de que haya datos */
const CLAVE = 'ofertas:2026-11-16:prep';
await fetch(U + '/api/encargo', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA OFERTA · del 16/11 al 30/11',
    p: 'gerencia', f: '2026-10-26', clave: CLAVE })
});
const estado2 = await (await pedir('/api/estado')).json();
const entorno2 = entorno.replace(
  'const encargos = ' + JSON.stringify(estado.encargos || []),
  'const encargos = ' + JSON.stringify(estado2.encargos || []));
const salida = new Function(entorno2 + sacar('listaOfertas') +
  '\nreturn listaOfertas;')()();

console.log('\n   === lo que sale hoy ===');
console.log('   ' + (salida.replace(/\s+/g, ' ').slice(0, 500) || '(vacío)'));

console.log('\n   === comprobaciones con datos reales ===');
ok('sale la oferta creada, con su fecha de inicio', salida.includes('16/11'));
ok('sale con su título', /del \d\d\/\d\d al \d\d\/\d\d/.test(salida));
ok('dice si está preparada o pendiente',
  salida.includes('preparada') || salida.includes('pendiente'));
ok('no es marcable', !salida.includes('cab-item') && !salida.includes('data-k'));
ok('lleva su cabecera', salida.includes('Dadas de alta'));

/* --- 3 · orden cronológico --- */
const fechas = [...salida.matchAll(/viene-dia">[^<]*?(\d\d\/\d\d)/g)].map(m => m[1]);
const ordenadas = [...fechas].sort((a, b) => {
  const [da, ma] = a.split('/').map(Number);
  const [db, mb] = b.split('/').map(Number);
  return ma - mb || da - db;
});
ok('van en orden de fecha', JSON.stringify(fechas) === JSON.stringify(ordenadas),
  { fechas, ordenadas });

/* limpieza */
for (const x of ((await (await pedir('/api/estado')).json()).encargos || [])) {
  if (String(x.clave || '') === CLAVE) {
    await pedir('/api/encargo-borrar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: x.id })
    });
  }
}

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
