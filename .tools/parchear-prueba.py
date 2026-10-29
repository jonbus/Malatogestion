"""Sustituye el bloque de fichar de prueba-en-vivo.mjs para que limpie lo suyo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

RUTA = "docs/nube/prueba-en-vivo.mjs"
t = open(RUTA, encoding="utf-8").read()

VIEJO = """/* 6 · fichar */
{
  const r = await fetch(BASE + '/api/fichar', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'op9', puesto: 'tienda' })
  });
  const d = await r.json();
  ok('ficha la entrada', /^\\d{2}:\\d{2}$/.test(d.entrada || ''), d);
  const d2 = await (await fetch(BASE + '/api/estado')).json();
  const mio = (d2.fichajes || []).find(f => f.q === 'op9');
  ok('el fichaje se guarda', !!mio, d2.fichajes);
}"""

NUEVO = """/* 6 · fichar — y BORRARLO, para no dejar un fichaje falso en los datos */
{
  const r = await fetch(BASE + '/api/fichar', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'prueba', puesto: 'tienda' })
  });
  const d = await r.json();
  ok('ficha la entrada', /^\\d{2}:\\d{2}$/.test(d.entrada || ''), d);
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
}"""

if VIEJO not in t:
    raise SystemExit("no encuentro el bloque a sustituir")
open(RUTA, "w", encoding="utf-8").write(t.replace(VIEJO, NUEVO))
print("  prueba-en-vivo.mjs: ahora limpia su fichaje")
