"""Compara con el sitio de la agenda, que sí funciona."""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
API = "https://api.netlify.com/api/v1"


def token():
    ruta = os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json")
    with open(ruta, encoding="utf-8") as f:
        cfg = json.load(f)
    for _u, d in (cfg.get("users") or {}).items():
        t = (d.get("auth") or {}).get("token")
        if t:
            return t


T = token()


def get(ruta):
    req = urllib.request.Request(API + ruta, headers={"Authorization": f"Bearer {T}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


for nombre in ("mi-agenda-kika", "tienda-malato"):
    print(f"\n=== {nombre} ===")
    try:
        s = next(x for x in get("/sites?per_page=100") if x.get("name") == nombre)
    except StopIteration:
        print("  no existe")
        continue
    print(f"  sso_login={s.get('sso_login')}  contexto={s.get('sso_login_context')}")
    print(f"  password={'SI' if s.get('password') else 'no'}  plan={s.get('plan')}")
    ds = get(f"/sites/{s['id']}/deploys?per_page=3")
    for d in ds[:2]:
        print(f"  deploy {d['id'][:12]}  estado={d['state']}")
        fns = d.get("available_functions") or []
        print(f"     funciones: {len(fns)}")
        for f in fns:
            print(f"        {f.get('n')}  runtime={f.get('runtime')}")
