"""Siembra los 16 nombres y monta las 8 cascadas de cortar → envasar.

Va directo al almacén, sin crear tareas de mentira: solo apunta los nombres
en la memoria y las cascadas. No toca nada más.
"""
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

PAREJAS = [
    "chorizo ibérico",
    "chorizo ELE dulce",
    "chorizo ELE picante",
    "salchichón ibérico",
    "salchichón ELE",
    "queso",
    "panceta ELE",
    "Extremadura",
]


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


def limpia(x):
    return " ".join(x.lower().strip().split())


c, estado = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
print(f"  leer el estado -> HTTP {c}")
if c != 200:
    print("  ", estado)
    sys.exit(1)

antes_nombres = len(estado.get("nombres") or [])
antes_cascadas = len(estado.get("cascadas") or {})

# --- 1 · los nombres
nombres = list(estado.get("nombres") or [])
for trozo in PAREJAS:
    for n in (f"Cortar {trozo}", f"Envasar {trozo}"):
        if n not in nombres:
            nombres.append(n)
estado["nombres"] = nombres

# --- 2 · las cascadas
cascadas = dict(estado.get("cascadas") or {})
for trozo in PAREJAS:
    cascadas[limpia(f"Cortar {trozo}")] = [{
        "que": f"Envasar {trozo}",
        "p": "tienda",
        "turno": None,
        "cuando": 0,
    }]
estado["cascadas"] = cascadas

c, d = cf("PUT", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}",
          json.dumps(estado).encode())
print(f"  escribir -> HTTP {c}")
if c != 200:
    print("  ", d)
    sys.exit(1)

c, d = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
print(f"\n  nombres: {antes_nombres} -> {len(d.get('nombres') or [])}")
print(f"  cascadas: {antes_cascadas} -> {len(d.get('cascadas') or {})}")
print("\n  las ocho cascadas:")
for k, v in sorted((d.get("cascadas") or {}).items()):
    if k.startswith("cortar "):
        print(f"    «{k}»  ->  {v[0]['que']}  ({v[0]['p']})")
print("\n  y lo demás intacto:")
print(f"    marcas {len(d.get('marcas') or {})} · encargos {len(d.get('encargos') or [])} · "
      f"recuentos {len(d.get('recuentos') or {})} · pan {len(d.get('tahona') or {})}")
