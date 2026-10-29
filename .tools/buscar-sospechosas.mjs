/* Dónde aparecen exactamente «encargo(» y «opciones(». */
import fs from 'node:fs';

const html = fs.readFileSync('docs/nube/public/index.html', 'utf8');
const js = html.split('<script>').pop().split('</script>')[0];

for (const patron of ['encargo(', 'opciones(']) {
  console.log(`\n  === ${patron} ===`);
  let i = -1;
  let n = 0;
  while ((i = js.indexOf(patron, i + 1)) >= 0 && n < 4) {
    const antes = js[i - 1] || '';
    console.log(`   pos ${i} · carácter anterior: «${antes}»`);
    console.log(`     …${js.slice(Math.max(0, i - 70), i + 40).replace(/\n/g, ' ')}…`);
    n++;
  }
}
