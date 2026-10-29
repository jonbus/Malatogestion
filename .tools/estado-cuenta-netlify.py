"""Mira el estado de la cuenta de Netlify: plan, uso y créditos."""
import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
API = "https://api.netlify.com/api/v1"

cfg = json.load(open(os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json"),
                     encoding="utf-8"))
T = [d["auth"]["token"] for d in cfg["users"].values() if d.get("auth", {}).get("token")][0]


def get(ruta):
    req = urllib.request.Request(API + ruta, headers={"Authorization": f"Bearer {T}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_cuerpo": e.read().decode("utf-8", "replace")[:200]}


sitio = next(s for s in get("/sites?per_page=100") if s.get("name") == "tienda-malato")
slug = sitio.get("account_slug")
print(f"  sitio: {sitio['name']}  ·  cuenta: {slug}")

cuenta = get(f"/accounts/{slug}")
if "_error" in cuenta:
    print(f"  cuenta: error {cuenta['_error']} {cuenta['_cuerpo']}")
else:
    for k in ("name", "type_name", "plan_name", "billing_period_start", "billing_period_end"):
        if k in cuenta:
            print(f"    {k:<24} {cuenta[k]}")
    cap = cuenta.get("capabilities") or {}
    for k, v in cap.items():
        if "deploy" in k or "build" in k or "bandwidth" in k:
            print(f"    {k:<24} {v}")

print("\n  uso de este mes:")
uso = get(f"/accounts/{slug}/usage")
if "_error" in uso:
    print(f"    error {uso['_error']}")
else:
    print("    " + json.dumps(uso)[:400])

print("\n  despliegues de los últimos 14 días (cada uno cuenta):")
dep = get(f"/sites/{sitio['id']}/deploys?per_page=100")
if isinstance(dep, list):
    fechas = {}
    for d in dep:
        f = str(d.get("created_at", ""))[:10]
        fechas[f] = fechas.get(f, 0) + 1
    for f in sorted(fechas, reverse=True)[:14]:
        print(f"    {f}: {fechas[f]}")
    print(f"    TOTAL: {len(dep)}")
