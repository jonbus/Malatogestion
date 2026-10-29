/* Comprueba, a través del túnel, que la versión nueva está servida. */
const U = 'https://gathered-daughters-attorney-cons.trycloudflare.com';

const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(25000) })).text();
console.log(`  KB: ${Math.round(t.length / 1024)}`);
console.log(`  tarea «Fichar» en el catálogo: ${t.includes('"t": "Fichar"') ? 'SÍ (mal)' : 'no'}`);
console.log(`  llamada al reloj (/api/fichar): ${t.includes('/api/fichar') ? 'SÍ (mal)' : 'no'}`);

const ls = t.match(/src="data:image\/png;base64,[^"]+"/g) || [];
console.log(`  imágenes incrustadas: ${ls.length}`);
console.log(`  son distintas: ${new Set(ls).size === ls.length}`);
console.log(`  tareas extra: ${t.includes('Añadir una tarea extra') ? 'sí' : 'no'}`);
console.log(`  pollos: ${t.includes('Limpiar pollos') ? 'sí' : 'no'}`);

const e = await (await fetch(U + '/api/estado', { signal: AbortSignal.timeout(20000) })).json();
console.log(`  API: día=${e.dia}`);
