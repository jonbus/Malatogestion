"""La prueba del recuento, contra Cloudflare y con fecha de mentira."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-recuento.mjs"
t = open(p, encoding="utf-8").read()

viejo = "const U = 'http://127.0.0.1:8100';"
nuevo = """const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36';"""
if viejo not in t:
    print("  NO ENCONTRADO el U")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)

t = t.replace(
    "const post = (r, c) => fetch(U + r, {\n  method: 'POST', headers: { 'Content-Type': 'application/json' },",
    "const post = (r, c) => fetch(U + r, {\n  method: 'POST', headers: { 'Content-Type': 'application/json', 'User-Agent': UA },")
t = t.replace("const get = (r) => fetch(U + r).then(x => x.json());",
              "const get = (r) => fetch(U + r, { headers: { 'User-Agent': UA } }).then(x => x.json());")

open(p, "w", encoding="utf-8").write(t)
print("  ok  la prueba del recuento apunta a Cloudflare")
