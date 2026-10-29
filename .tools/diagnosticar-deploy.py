"""Diagnostica el Forbidden del despliegue."""
import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
API = "https://api.netlify.com/api/v1"
SITIO = "8c31f843-9327-40af-ac66-ae1de35f5740"

cfg = json.load(open(os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json"),
                     encoding="utf-8"))
T = [d["auth"]["token"] for d in cfg["users"].values() if d.get("auth", {}).get("token")][0]


def pedir(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    h = {"Authorization": f"Bearer {T}"}
    if datos:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + ruta, data=datos, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:200]
    except Exception as e:
        return 0, str(e)


print("  GET /user          ->", pedir("GET", "/user")[0])
print("  GET /sites/{id}    ->", pedir("GET", f"/sites/{SITIO}")[0])
codigo, cuerpo = pedir("GET", f"/sites/{SITIO}/deploys?per_page=3")
print(f"  GET /deploys       -> {codigo}")
if codigo == 200 and isinstance(cuerpo, list):
    for d in cuerpo:
        print(f"      {d['id'][:12]} estado={d['state']} origen={d.get('deploy_source')}")

# ¿puede crear un despliegue vacío? (solo comprobación, no sube nada)
codigo, cuerpo = pedir("POST", f"/sites/{SITIO}/deploys", {})
print(f"\n  POST /deploys      -> {codigo}")
print(f"      {str(cuerpo)[:180]}")
