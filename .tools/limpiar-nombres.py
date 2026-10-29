"""Quita de la memoria los nombres de prueba."""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = __import__("os").environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = __import__("os").environ.get("CLOUDFLARE_ACCOUNT_ID", "")
KV = "544a4e67fd9c4acaab5a0e7d2dcfbd35"
API = "https://api.cloudflare.com/client/v4"
CLAVE = "estado"


def cf(metodo, ruta, datos=None):
    h = {"Authorization": "Bearer " + TOKEN}
    if datos is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + ruta, data=datos, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            bruto = r.read()
            try:
                return r.status, json.loads(bruto)
            except Exception:
                return r.status, {"_bruto": bruto}
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode("utf-8", "replace")[:300]}


c, estado = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
if c != 200:
    print("  no se pudo leer:", estado)
    sys.exit(1)

antes = list(estado.get("nombres") or [])
fuera = [n for n in antes if n.upper().startswith("PRUEBA") or "CF-" in n or " 17" in n[-14:]]
estado["nombres"] = [n for n in antes if n not in fuera]

c, d = cf("PUT", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}",
          json.dumps(estado).encode())
print(f"  escribir -> HTTP {c}")

c, d = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
nombres = d.get("nombres") or []
print(f"  nombres: {len(antes)} -> {len(nombres)}")
print(f"  quitados: {len(fuera)}")
print("\n  los que quedan:")
for n in sorted(nombres):
    print("   ", n)
print(f"\n  cascadas: {len(d.get('cascadas') or {})}")
print(f"  y lo vuestro intacto: marcas {len(d.get('marcas') or {})} · "
      f"encargos {len(d.get('encargos') or [])} · pan {len(d.get('tahona') or {})}")
