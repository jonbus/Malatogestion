"""Compara de dónde vienen los despliegues de los dos sitios."""
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


for nombre in ("mi-agenda-kika", "tienda-malato"):
    s = next(x for x in get("/sites?per_page=100") if x.get("name") == nombre)
    d = get("/sites/" + s["id"] + "/deploys?per_page=1")[0]
    print(f"  {nombre}")
    for k in ("deploy_source", "manual_deploy", "framework", "build_id",
              "functions_region", "entry_path", "has_source_zip"):
        print(f"     {k:<18} {d.get(k)}")
