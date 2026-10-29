/* Verifica el arreglo del nombre de la Jefa. */
const U = 'https://detect-engineers-chuck-jobs.trycloudflare.com';

const t = await (await fetch(U + '/', { signal: AbortSignal.timeout(25000) })).text();
console.log(`  KB: ${Math.round(t.length / 1024)}`);
console.log(`  versión -18: ${t.includes('v-2026-10-23-18')}`);
console.log(`  la Jefa tiene nombre propio: ${t.includes('gerencia: "Jefa"')}`);
console.log(`  ya no cae en Coordinadora: ${!t.includes('? "Tienda " : "Coordinadora "')}`);
console.log(`  título por tabla: ${t.includes('COMO_SE_LLAMA_PUESTO')}`);
