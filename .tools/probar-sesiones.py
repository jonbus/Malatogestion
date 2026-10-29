"""Comprueba si las sesiones de Netlify siguen valiendo."""
import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BASES = [
    ("APPDATA normal", os.environ["APPDATA"]),
    ("copia del proyecto", r"C:\Users\Usuario\Desktop\APP Malato\.tools\appdata"),
]

for etiqueta, base in BASES:
    ruta = os.path.join(base, "netlify", "Config", "config.json")
    if not os.path.exists(ruta):
        print(f"  {etiqueta}: no hay fichero")
        continue
    cfg = json.load(open(ruta, encoding="utf-8"))
    toks = [d["auth"]["token"] for d in cfg.get("users", {}).values()
            if d.get("auth", {}).get("token")]
    if not toks:
        print(f"  {etiqueta}: sin token")
        continue
    req = urllib.request.Request("https://api.netlify.com/api/v1/user",
                                 headers={"Authorization": "Bearer " + toks[0]})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            u = json.loads(r.read())
        print(f"  {etiqueta}: VALIDO -> {u.get('email')}")
    except urllib.error.HTTPError as e:
        print(f"  {etiqueta}: HTTP {e.code}")
    except Exception as e:
        print(f"  {etiqueta}: {e}")
