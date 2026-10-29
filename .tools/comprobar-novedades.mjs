/* Comprueba que las novedades están en la versión publicada. */
const URL = 'https://tienda-malato.netlify.app';

const r = await fetch(URL + '/');
const t = await r.text();

const cosas = [
  ['Frentear los yogures (apertura)', 'Frentear los yogures'],
  ['Frentear el congelado (apertura)', 'Frentear el congelado'],
  ['selector de fecha', 'fecha-inp'],
  ['botón de día anterior / siguiente', 'sumarDias(fechaSel, -1)'],
  ['botón Hoy', 'textContent = "Hoy"'],
  ['vista de mes', 'function verMes'],
  ['bloque SIN HACER', 'SIN HACER'],
  ['menú ¿para cuándo lo pasas?', '¿Para cuándo lo pasas?'],
  ['«la próxima vez que yo vuelva»', 'La próxima vez que yo vuelva'],
  ['pasadas a este día', 'Pasadas a este día'],
  ['cada tarea del día depende de la fecha', 'semanaDe(fechaSel)'],
];

console.log(`   HTTP ${r.status} · ${Math.round(t.length / 1024)} KB\n`);
let faltan = 0;
for (const [nombre, busca] of cosas) {
  const esta = t.includes(busca);
  if (!esta) faltan++;
  console.log(`   ${esta ? 'OK   ' : 'FALTA'}  ${nombre}`);
}

const e = await (await fetch(URL + '/api/estado')).json();
console.log(`\n   la función responde: dia=${e.dia} version=${e.version}`);
console.log(`   ${faltan === 0 ? 'TODO PUBLICADO' : faltan + ' sin publicar'}`);
process.exit(faltan === 0 ? 0 : 1);
