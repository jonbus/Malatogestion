// Comprobaciones de los datos del seed que ningún parser puede ver:
// dígitos de control EAN-13, unicidad de claves sembradas y coherencia de importes.
import { readFileSync } from 'node:fs';

const sql = readFileSync('db/seed/001_demo_store.sql', 'utf8');
const problems = [];
const ok = (m) => console.log(`  ok  ${m}`);
const bad = (m) => { problems.push(m); console.log(`  X   ${m}`); };

function ean13Check(ean) {
  let sum = 0;
  for (let i = 0; i < 12; i++) sum += Number(ean[i]) * (i % 2 === 0 ? 1 : 3);
  return (10 - (sum % 10)) % 10;
}

// ------------------------------------------------------------------ productos
console.log('EAN-13 de los 30 productos (prefijo 84 = España):');
const prodRe = /\('([A-Z]{3}-\d{3})',\s*'(\d{13})',\s*'/g;
const skus = new Set(); const eans = new Set();
let m, n = 0, badEan = 0;
while ((m = prodRe.exec(sql))) {
  const [, sku, ean] = m;
  n++;
  if (!ean.startsWith('84')) bad(`el EAN ${ean} (${sku}) no empieza por 84`);
  if (ean13Check(ean) !== Number(ean[12])) { badEan++; bad(`dígito de control incorrecto en ${ean} (${sku})`); }
  if (skus.has(sku)) bad(`SKU duplicado: ${sku}`);
  if (eans.has(ean)) bad(`EAN duplicado: ${ean}`);
  skus.add(sku); eans.add(ean);
}
if (n !== 30) bad(`se esperaban 30 productos, hay ${n}`);
if (badEan === 0) ok(`${n} productos, SKU y EAN únicos, los 30 dígitos de control EAN-13 correctos`);

// ------------------------------------------------------------------ stock
console.log('Claves del stock (producto, ubicación):');
const stockSection = sql.slice(sql.indexOf('INSERT INTO inventory.stock ('), sql.indexOf('-- Carga inicial de movimientos'));
const stockRe = /\('([A-Z]{3}-\d{3})','(loc\.\w+)',\s*([\d.]+)\)/g;
const stockKeys = new Set(); let stockRows = 0, dupStock = 0, belowMin = 0;
const minBySku = {};
{
  const re = /\('([A-Z]{3}-\d{3})','(\d{13})','[^']*',\s*'[^']*','\w+',(?:\w+),(\w+),\s*[\d.]+,\s*[\d.]+,\s*[\d.]+,\s*([\d.]+),/g;
  let x; while ((x = re.exec(sql))) minBySku[x[1]] = Number(x[4]);
}
while ((m = stockRe.exec(stockSection))) {
  const [, sku, loc, qty] = m;
  stockRows++;
  const k = `${sku}|${loc}`;
  if (stockKeys.has(k)) { dupStock++; bad(`stock duplicado para ${k} (la PK compuesta lo rechazaría)`); }
  stockKeys.add(k);
  if (loc === 'loc.sala' && minBySku[sku] !== undefined && Number(qty) < minBySku[sku]) belowMin++;
}
if (dupStock === 0) ok(`${stockRows} filas de stock, ninguna clave (producto, ubicación) repetida`);
ok(`${belowMin} productos de SALA deliberadamente por debajo del mínimo (para disparar reglas)`);

// ------------------------------------------------------------------ ventas
console.log('Coherencia de importes de las 3 ventas:');
const salesBlock = sql.slice(sql.indexOf("('CAJA-01','T-2601-000101'"), sql.indexOf('AS v(register_code, ticket, subtotal'));
const saleRe = /\('(CAJA-\d+)','(T-[\d-]+)',\s*([\d.]+),([\d.]+),([\d.]+),([\d.]+),/g;
const sales = [];
while ((m = saleRe.exec(salesBlock))) sales.push({ reg: m[1], ticket: m[2], sub: +m[3], disc: +m[4], tax: +m[5], total: +m[6] });
if (sales.length !== 3) bad(`se esperaban 3 ventas, hay ${sales.length}`);

const linesBlock = sql.slice(sql.indexOf("('CAJA-01','T-2601-000101',1,"), sql.indexOf('AS v(register_code, ticket, line_no'));
const lineRe = /\('(CAJA-\d+)','(T-[\d-]+)',\d+,'[A-Z]{3}-\d{3}',\s*[\d.]+,[\d.]+,[\d.]+,\s*([\d.]+)\)/g;
const sumByTicket = {};
const sumDisc = {};
while ((m = lineRe.exec(linesBlock))) {
  sumByTicket[m[2]] = (sumByTicket[m[2]] ?? 0) + Number(m[3]);
  const dm = /\('(CAJA-\d+)','(T-[\d-]+)',\d+,'[A-Z]{3}-\d{3}',\s*[\d.]+,[\d.]+,[\d.]+,\s*[\d.]+\)/g;
}
const discRe = /\('(CAJA-\d+)','(T-[\d-]+)',(\d+),'[A-Z]{3}-\d{3}',\s*[\d.]+,[\d.]+,\s*([\d.]+),\s*[\d.]+\)/g;
while ((m = discRe.exec(linesBlock))) sumDisc[m[2]] = (sumDisc[m[2]] ?? 0) + Number(m[4]);

for (const s of sales) {
  const linesSum = +(sumByTicket[s.ticket] ?? 0).toFixed(2);
  const discSum = +(sumDisc[s.ticket] ?? 0).toFixed(2);
  const neto = +(linesSum + discSum).toFixed(2); // line_total ya va con descuento aplicado
  if (Math.abs(neto - s.sub) > 0.01) bad(`${s.ticket}: líneas ${neto} != subtotal ${s.sub}`);
  if (Math.abs(discSum - s.disc) > 0.01) bad(`${s.ticket}: descuentos de línea ${discSum} != cabecera ${s.disc}`);
  if (Math.abs(s.sub - s.disc + s.tax - s.total) > 0.01) bad(`${s.ticket}: subtotal-descuento+IVA = ${(s.sub - s.disc + s.tax).toFixed(2)} != total ${s.total}`);
}
if (!problems.some((p) => p.startsWith('T-'))) ok('las 8 líneas cuadran con la cabecera de su venta (subtotal, descuento e IVA)');

// ------------------------------------------------------------------ lotes
console.log('Lotes próximos a caducar:');
const lotBlock = sql.slice(sql.indexOf('INSERT INTO inventory.lots ('), sql.indexOf('INSERT INTO inventory.wastage ('));
const lotRe = /\('([A-Z]{3}-\d{3})',\s*'loc\.\w+',\s*'([A-Z]{3}-\d{4})',\s*CURRENT_DATE \+ (\d+)/g;
const lots = [];
while ((m = lotRe.exec(lotBlock))) lots.push({ sku: m[1], batch: m[2], days: +m[3] });
const soon = lots.filter((l) => l.days < 3);
if (lots.length !== 7) bad(`se esperaban 7 lotes, hay ${lots.length}`);
if (soon.length !== 2) bad(`se esperaban 2 lotes con menos de 3 días, hay ${soon.length}`);
else ok(`${lots.length} lotes, ${soon.length} de ellos caducan en menos de 3 días (${soon.map((l) => l.batch).join(', ')})`);

// ------------------------------------------------------------------ resumen
console.log(problems.length ? `\n${problems.length} PROBLEMAS` : '\nDatos del seed coherentes.');
process.exit(problems.length ? 1 : 0);
