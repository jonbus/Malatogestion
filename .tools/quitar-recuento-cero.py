"""Quita el recuento de prueba (todo a cero) y deja lo demás intacto."""
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


def cf(metodo, ruta, datos=None, tipo="application/json"):
    h = {"Authorization": "Bearer " + TOKEN}
    if datos is not None:
        h["Content-Type"] = tipo
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
    except Exception as e:
        return 0, {"_error": str(e)}


c, d = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
print(f"  leer el estado -> HTTP {c}")
if c != 200:
    print("  ", d)
    sys.exit(1)

estado = d
antes = {k: (len(v) if isinstance(v, (dict, list)) else v) for k, v in estado.items()}
print("  antes:", json.dumps(antes))

# se quitan solo los recuentos a cero (los de prueba)
rec = estado.get("recuentos") or {}
limpios = {}
for f, v in rec.items():
    numeros = [v.get("pollos", 0), v.get("codillos", 0),
               v.get("patatas", 0), v.get("bravas", 0)]
    if any(n for n in numeros):
        limpios[f] = v
    else:
        print(f"  quitado el recuento de {f} (todo a cero)")
estado["recuentos"] = limpios

c, d = cf("PUT", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}",
          json.dumps(estado).encode())
print(f"\n  escribir el estado -> HTTP {c}")

c, d = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
despues = {k: (len(v) if isinstance(v, (dict, list)) else v) for k, v in d.items()}
print("  después:", json.dumps(despues))
