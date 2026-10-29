/* Prueba de verdad, contra la aplicación publicada.
   node docs/nube/prueba-en-vivo.mjs
*/
const BASE = process.env.BASE || 'https://tienda-malato.netlify.app';
let fallos = 0;
const ok = (nombre, cond, extra) => {
  console.log(`   ${cond ? 'OK  ' : 'FALLO'}  ${nombre}${!cond && extra ? '  -> ' + JSON.stringify(extra) : ''}`);
  if (!cond) fallos++;
};

console.log(`   probando ${BASE}\n`);

/* 1 · la página */
{
  const r = await fetch(BASE + '/', { redirect: 'manual' });
  const t = await r.text();
  ok('la página responde', r.status === 200, r.status);
  ok('trae el login', t.includes('En qué puesto estás'));
  ok('lleva el logo', t.includes('data:image/png;base64'));
  console.log(`   (${Math.round(t.length / 1024)} KB)`);
}

/* 2 · el estado */
let dia;
{
  const r = await fetch(BASE + '/api/estado');
  const d = await r.json();
  ok('la función responde', r.status === 200, { status: r.status, d });
  ok('devuelve el día', /^\d{4}-\d{2}-\d{2}$/.test(d.dia || ''), d.dia);
  ok('devuelve la versión', typeof d.version === 'number', d.version);
  ok('devuelve marcas', typeof d.marcas === 'object', typeof d.marcas);
  dia = d.dia;
}

/* 3 · marcar */
{
  const k1 = `${dia}|op|mr0`, k2 = `${dia}|op|mr0.0`, k3 = `${dia}|co|dr1`;
  const r = await fetch(BASE + '/api/marcas', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'op1', cambios: { [k1]: true, [k2]: true, [k3]: true } })
  });
  const d = await r.json();
  ok('se marcan 3', d.aplicados === 3, d);
}

/* 4 · se han guardado */
{
  const d = await (await fetch(BASE + '/api/estado')).json();
  const claves = Object.keys(d.marcas).filter(k => k.startsWith(dia));
  ok('están guardadas', claves.length >= 3, claves);
  const primera = d.marcas[`${dia}|op|mr0`];
  ok('con autor', primera && primera.q === 'op1', primera);
  ok('con hora', primera && /^\d{2}:\d{2}$/.test(primera.h), primera);
}

/* 5 · desmarcar */
{
  const k1 = `${dia}|op|mr0`;
  await fetch(BASE + '/api/marcas', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'op1', cambios: { [k1]: false } })
  });
  const d = await (await fetch(BASE + '/api/estado')).json();
  ok('se desmarca', !d.marcas[k1], d.marcas[k1]);
  ok('quedan las otras', !!d.marcas[`${dia}|op|mr0.0`]);
}

/* 6 · fichar — y BORRARLO, para no dejar un fichaje falso en los datos */
{
  const r = await fetch(BASE + '/api/fichar', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'prueba', puesto: 'tienda' })
  });
  const d = await r.json();
  ok('ficha la entrada', /^\d{2}:\d{2}$/.test(d.entrada || ''), d);
  const d2 = await (await fetch(BASE + '/api/estado')).json();
  const mio = (d2.fichajes || []).find(f => f.q === 'prueba');
  ok('el fichaje se guarda', !!mio, d2.fichajes);
  if (mio) {
    const b = await fetch(BASE + '/api/olvidar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fichaje: { q: mio.q, dia: mio.dia, e: mio.e } })
    }).then(x => x.json());
    ok('y se borra para no ensuciar', b.borrados === 1, b);
  }
}

/* 7 · dos personas distintas ven lo mismo (la prueba de la nube) */
{
  const d = await (await fetch(BASE + '/api/estado')).json();
  ok('las marcas son de todos (no por persona)',
     Object.keys(d.marcas).some(k => k.includes('|op|')) &&
     Object.keys(d.marcas).some(k => k.includes('|co|')));
}

console.log(`\n   ${fallos === 0 ? 'TODO BIEN' : 'FALLOS: ' + fallos}`);
process.exit(fallos === 0 ? 0 : 1);
