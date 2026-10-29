"""Pone el navegador simulado en la prueba de Cloudflare."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-cloudflare.mjs"
t = open(p, encoding="utf-8").read()

viejo = "const U = 'https://app.supermalato.workers.dev';"
nuevo = """const U = 'https://app.supermalato.workers.dev';

/* Cloudflare rechaza a los programas que no se identifican como navegador,
   así que las pruebas se presentan como tal. Un móvil de verdad no tiene
   este problema. */
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta,
  Object.assign({ headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
                opciones || {}));"""

t = t.replace(viejo, nuevo, 1)
t = t.replace("fetch(U + ruta, {\n  method: 'POST'", "pedir(ruta, {\n  method: 'POST'")
t = t.replace("const r = await fetch(U + '/');", "const r = await pedir('/');")
t = t.replace("await fetch(U + '/api/estado')", "await pedir('/api/estado')")
t = t.replace("await (await fetch(U + '/api/estado')).json()", "await (await pedir('/api/estado')).json()")
t = t.replace("(await (await fetch(U + '/api/estado')).json())", "(await (await pedir('/api/estado')).json())")

open(p, "w", encoding="utf-8").write(t)
print("  prueba con navegador simulado")
