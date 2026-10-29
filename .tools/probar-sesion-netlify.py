"""Comprueba si la sesión de Netlify guardada en el PC todavía vale.

No imprime el token. Solo dice si funciona y con qué cuenta.
"""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ruta = os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json")
with open(ruta, encoding="utf-8") as f:
    cfg = json.load(f)

print(f"  claves del fichero: {sorted(cfg.keys())}")

token = None
for usuario, datos in (cfg.get("users") or {}).items():
    token = datos.get("auth", {}).get("token")
    print(f"  usuario guardado: {datos.get('email', '(sin correo)')}")
    print(f"  token presente: {'SI' if token else 'NO'}  "
          f"(longitud {len(token) if token else 0})")

if not token:
    print("  NO HAY TOKEN UTILIZABLE")
    sys.exit(1)

req = urllib.request.Request(
    "https://api.netlify.com/api/v1/user",
    headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        u = json.loads(r.read())
    print(f"\n  TOKEN VALIDO  ->  cuenta: {u.get('email')}  (id {u.get('id')})")
except Exception as e:
    print(f"\n  TOKEN NO VALE: {e}")
    sys.exit(1)
