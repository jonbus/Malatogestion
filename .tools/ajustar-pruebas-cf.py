"""Ajusta las pruebas a Cloudflare y a que ya hay datos de verdad."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0


def cambia(ruta, viejo, nuevo, etiqueta):
    global fallos
    t = open(ruta, encoding="utf-8").read()
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    open(ruta, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
    print(f"   ok  {etiqueta}")


# 1 · ya no se exige que el almacén esté vacío: la tienda está trabajando
cambia(".tools/probar-cloudflare.mjs",
       """ok('empieza vacío', Object.keys(e.marcas || {}).length === 0 &&
   (e.encargos || []).length === 0 &&
   Object.keys(e.recuentos || {}).length === 0,
   { marcas: Object.keys(e.marcas || {}).length, encargos: (e.encargos||[]).length });""",
       """ok('el estado trae las seis partes',
  ['marcas','traslados','notas','fichajes','encargos','recuentos']
    .every(k => e[k] !== undefined),
  Object.keys(e));""",
       "cloudflare: se comprueba la forma, no que esté vacío")

# 2 · la prueba de los tres perfiles, contra Cloudflare
cambia(".tools/probar-tres-perfiles.mjs",
       "const U = 'http://127.0.0.1:8100';",
       """const U = 'https://app.supermalato.workers.dev';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/131.0 Safari/537.36';""",
       "tres perfiles: apunta a Cloudflare")

cambia(".tools/probar-tres-perfiles.mjs",
       """const post = (r, c) => fetch(U + r, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));""",
       """const post = (r, c) => fetch(U + r, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'User-Agent': UA },
  body: JSON.stringify(c ?? {})
}).then(async x => ({ status: x.status, body: await x.json().catch(() => ({})) }));""",
       "tres perfiles: manda el navegador simulado")

# 3 · las lecturas sueltas del estado
cambia(".tools/probar-tres-perfiles.mjs",
       "await (await fetch(U + '/api/estado')).json()",
       "await (await fetch(U + '/api/estado', { headers: { 'User-Agent': UA } })).json()",
       "tres perfiles: lecturas con navegador")

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
