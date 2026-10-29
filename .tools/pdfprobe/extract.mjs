import { readFileSync, writeFileSync } from 'node:fs';
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';
for (const f of ['convenio-ccoo-2024.pdf','convenio-lab.pdf']) {
  try {
    const data = new Uint8Array(readFileSync('.tools/docs/' + f));
    const doc = await pdfjs.getDocument({ data, useSystemFonts: false }).promise;
    let out = '';
    for (let i = 1; i <= doc.numPages; i++) {
      const page = await doc.getPage(i);
      const tc = await page.getTextContent();
      out += tc.items.map((it) => it.str).join(' ') + '\n';
    }
    writeFileSync('.tools/docs/' + f + '.txt', out);
    console.log(f, '->', doc.numPages, 'paginas,', out.length, 'caracteres');
  } catch (e) {
    console.log(f, 'ERROR', String(e.message).slice(0, 120));
  }
}
