"""Deja el pan de hoy vacío: todo lo que hay era de las pruebas."""
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
        return e.code, {"_error": e.read().decode("utf-8", "replace")[:200]}


c, estado = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
print(f"  leer -> HTTP {c}")
if c != 200:
    print("  ", estado)
    sys.exit(1)

print("  el pan que había:")
print("   ", json.dumps(estado.get("tahona") or {}, ensure_ascii=False))

# se vacía el pan: era todo de las pruebas
estado["tahona"] = {}

c, d = cf("PUT", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}",
          json.dumps(estado).encode())
print(f"\n  escribir -> HTTP {c}")
if c != 200:
    print("  ", d)

c, d = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
print("  el pan ahora:", json.dumps(d.get("tahona") or {}, ensure_ascii=False))
print("  y no se ha tocado nada más:",
      f"marcas {len(d.get('marcas') or {})} ·",
      f"encargos {len(d.get('encargos') or [])} ·",
      f"recuentos {len(d.get('recuentos') or {})}")
