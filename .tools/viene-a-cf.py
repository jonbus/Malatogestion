"""La prueba de «lo que viene», también contra Cloudflare."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-viene.mjs"
t = open(p, encoding="utf-8").read()

viejo = "const U = 'http://127.0.0.1:8100';"
nuevo = """const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';
const pedir = (ruta, opciones) => fetch(U + ruta, Object.assign({
  headers: Object.assign({ 'User-Agent': UA }, (opciones || {}).headers || {}) },
  opciones || {}));"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)
t = t.replace("await fetch(U + '/api/estado')", "await pedir('/api/estado')")
t = t.replace("await (await fetch(U + '/api/estado')).json()", "await (await pedir('/api/estado')).json()")
t = t.replace("await fetch(U + '/api/encargo-borrar'", "await pedir('/api/encargo-borrar'")
t = t.replace("await fetch(U + '/api/encargo'", "await pedir('/api/encargo'")
t = t.replace("(await (await fetch(U + '/api/estado')).json())", "(await (await pedir('/api/estado')).json())")

open(p, "w", encoding="utf-8").write(t)
print("  ok  «lo que viene» apunta a Cloudflare")
