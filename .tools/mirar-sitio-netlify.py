"""Mira por qué el sitio devuelve 401: protección, contraseña, etc."""
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
    raise SystemExit("sin token")


T = token()


def get(ruta):
    req = urllib.request.Request(API + ruta, headers={"Authorization": f"Bearer {T}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


sitios = get("/sites?per_page=100")
sitio = next(s for s in sitios if s.get("name") == "tienda-malato")
print("  claves interesantes del sitio:")
for k in ("name", "state", "ssl_url", "url", "password", "sso_login", "sso_login_context",
          "account_type", "account_slug", "plan", "published_deploy_id", "custom_domain",
          "domain_aliases", "claimed", "prevent_non_admin_deploys"):
    if k in sitio:
        v = sitio[k]
        if isinstance(v, str) and len(v) > 70:
            v = v[:70] + "…"
        print(f"    {k:<24} {v}")

print("\n  despliegue publicado:")
d = get(f"/sites/{sitio['id']}/deploys?per_page=3")
for x in d[:3]:
    print(f"    {x['id']}  estado={x['state']}  contexto={x.get('context')}  "
          f"funciones={len(x.get('available_functions') or [])}")
    for f in (x.get("available_functions") or []):
        print(f"        funcion: {f.get('n')}  ({f.get('runtime')})")

print("\n  ¿el plan del equipo limita algo?")
try:
    cuenta = get(f"/accounts/{sitio['account_slug']}")
    print(f"    tipo={cuenta.get('type_name')}  nombre={cuenta.get('name')}")
    for k in ("capabilities",):
        if k in cuenta:
            print(f"    {k}: {json.dumps(cuenta[k])[:200]}")
except Exception as e:
    print(f"    no se pudo leer: {e}")
