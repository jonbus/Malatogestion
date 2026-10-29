"""Mira el detalle del despliegue: por qué no ve las funciones."""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
API = "https://api.netlify.com/api/v1"
cfg = json.load(open(os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json"),
                     encoding="utf-8"))
T = [d["auth"]["token"] for d in cfg["users"].values() if d.get("auth", {}).get("token")][0]


def get(ruta):
    req = urllib.request.Request(API + ruta, headers={"Authorization": f"Bearer {T}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


s = next(x for x in get("/sites?per_page=100") if x.get("name") == "tienda-malato")
d = get(f"/sites/{s['id']}/deploys?per_page=1")[0]

print("  claves del despliegue:")
for k in sorted(d.keys()):
    v = d[k]
    if isinstance(v, (str, int, bool, type(None))) and len(str(v)) < 80:
        print(f"    {k:<26} {v}")

print("\n  funciones:", d.get("available_functions"))
print("  errores:", d.get("error_message"))
print("  resumen:", json.dumps(d.get("summary") or {})[:400])

print("\n  ficheros publicados (primeros 20):")
try:
    arbol = get(f"/deploys/{d['id']}/files")
    for f in arbol[:20]:
        print(f"    {f.get('path')}")
    print(f"    ... total {len(arbol)}")
except Exception as e:
    print(f"    no se pudo: {e}")
