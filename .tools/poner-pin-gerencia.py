"""Pone la clave de gerencia como variable de entorno del sitio en Netlify.

No la imprime. Uso:  python .tools\\poner-pin-gerencia.py 583104
"""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 2:
    raise SystemExit("uso: poner-pin-gerencia.py <clave>")
PIN = sys.argv[1].strip()
if len(PIN) < 4:
    raise SystemExit("la clave tiene que tener al menos 4 caracteres")

API = "https://api.netlify.com/api/v1"
cfg = json.load(open(os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json"),
                     encoding="utf-8"))
T = [d["auth"]["token"] for d in cfg["users"].values() if d.get("auth", {}).get("token")][0]


def pedir(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    h = {"Authorization": f"Bearer {T}"}
    if datos:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + ruta, data=datos, headers=h, method=metodo)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"{}")


sitio = next(s for s in pedir("GET", "/sites?per_page=100") if s.get("name") == "tienda-malato")
print(f"  sitio: {sitio['name']}  ({sitio['id']})")

actuales = (sitio.get("build_settings") or {}).get("env") or {}
print(f"  variables que ya había: {list(actuales.keys()) or 'ninguna'}")

nuevas = dict(actuales)
nuevas["GERENCIA_PIN"] = PIN

pedir("PATCH", f"/sites/{sitio['id']}", {"build_settings": {"env": nuevas}})
print("  GERENCIA_PIN puesta")

# comprobar que quedó
otra = pedir("GET", f"/sites/{sitio['id']}")
env = (otra.get("build_settings") or {}).get("env") or {}
print(f"  comprobado: {'SÍ' if env.get('GERENCIA_PIN') else 'NO'} "
      f"· longitud {len(env.get('GERENCIA_PIN') or '')}")
print("\n  Para cambiarla más adelante, vuelve a lanzar esto con la clave nueva.")
