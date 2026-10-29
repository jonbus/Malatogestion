"""La prueba de ofertas también contra Cloudflare."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-ofertas-en-bloque.mjs"
t = open(p, encoding="utf-8").read()

viejo = "const U = 'http://127.0.0.1:8100';"
nuevo = """const U = 'https://app.supermalato.workers.dev';
/* Cloudflare rechaza a los programas que no se identifican como navegador */
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta, Object.assign({
  headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
  opciones || {}));"""

if viejo not in t:
    print("  NO ENCONTRADO el U")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)

# todas las llamadas pasan por pedir()
t = t.replace("await fetch(U + '/api/estado')", "await pedir('/api/estado')")
t = t.replace("await (await fetch(U + '/api/estado')).json()", "await (await pedir('/api/estado')).json()")
t = t.replace("""await fetch(U + '/api/encargo', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA OFERTA · del 16/11 al 30/11',
      p: 'gerencia', f: '2026-10-26', clave: CLAVE })
  });""",
"""await pedir('/api/encargo', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quien: 'ge1', t: 'PRUEBA OFERTA · del 16/11 al 30/11',
      p: 'gerencia', f: '2026-10-26', clave: CLAVE })
  });""")
t = t.replace("""await fetch(U + '/api/encargo-borrar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: x.id })
    });""",
"""await pedir('/api/encargo-borrar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: x.id })
    });""")

open(p, "w", encoding="utf-8").write(t)
print("  ok  la prueba de ofertas apunta a Cloudflare")
