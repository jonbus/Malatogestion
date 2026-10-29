// Busca en el texto extraido del convenio los conceptos de jornada, vacaciones y descansos,
// e imprime el contexto alrededor de cada aparicion.
import { readFileSync } from 'node:fs';

const CLAVES = [
  'jornada anual', 'horas anuales', 'jornada ordinaria', 'jornada maxima', 'jornada maxima',
  'computo', 'distribucion', 'vacaciones', 'descanso', 'festivo', 'extraordinaria',
  'bolsa de horas', 'calendario', 'cuadrante', 'horario',
];

const archivos = ['convenio-ccoo-2024.pdf.txt', 'convenio-lab.pdf.txt'];

for (const f of archivos) {
  const txt = readFileSync(`.tools/docs/${f}`, 'utf8').replace(/\s+/g, ' ').replace(/­/g, '');
  console.log(`\n${'='.repeat(70)}\n${f}  (${txt.length} caracteres)\n${'='.repeat(70)}`);
  for (const clave of CLAVES) {
    const re = new RegExp(clave, 'gi');
    const vistas = new Set();
    let m;
    let n = 0;
    while ((m = re.exec(txt)) !== null && n < 3) {
      const ini = Math.max(0, m.index - 130);
      const frag = txt.slice(ini, m.index + 230);
      const huella = frag.slice(0, 60);
      if (vistas.has(huella)) continue;
      vistas.add(huella);
      n++;
      console.log(`\n  [${clave}] ...${frag.trim()}...`);
    }
    if (n === 0) console.log(`\n  [${clave}] SIN APARICIONES`);
  }
}
