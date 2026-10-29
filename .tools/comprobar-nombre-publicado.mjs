/* Comprueba que la app publicada ya usa «Tienda» y no «Operaria». */
const URL = 'https://tienda-malato.netlify.app';

const r = await fetch(URL + '/');
const t = await r.text();

const puestos = t.match(/const PUESTOS = .*?;/);
console.log(`   HTTP ${r.status} · ${Math.round(t.length / 1024)} KB`);
console.log(`   ${puestos ? puestos[0] : 'no encuentro PUESTOS'}`);
console.log(`   dice «Operaria»:  ${/Operaria/i.test(t) ? 'SÍ (mal)' : 'no'}`);
console.log(`   dice «operaria»:  ${/operaria/i.test(t) ? 'SÍ (mal)' : 'no'}`);
console.log(`   dice «Tienda»:    ${/Tienda/.test(t) ? 'SÍ' : 'no'}`);
console.log(`   dice «tienda»:    ${/tienda/.test(t) ? 'SÍ' : 'no'}`);

/* El estado de la API sigue funcionando */
const e = await (await fetch(URL + '/api/estado')).json();
console.log(`   la función responde: dia=${e.dia} version=${e.version}`);
