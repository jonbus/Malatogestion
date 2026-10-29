"""Comprueba el token de Cloudflare y saca la cuenta."""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
API = "https://api.cloudflare.com/client/v4"


def pide(ruta, token=None):
    req = urllib.request.Request(API + ruta, headers={
        "Authorization": "Bearer " + (token or TOKEN),
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"_error": str(e)}


codigo, d = pide("/user/tokens/verify")
print(f"  1) verificar el token -> HTTP {codigo}")
if codigo == 200 and d.get("success"):
    print("     VÁLIDO · estado:", (d.get("result") or {}).get("status"))
else:
    print("     NO VÁLIDO:", json.dumps(d.get("errors") or d)[:300])

codigo, d = pide("/accounts")
print(f"\n  2) cuentas -> HTTP {codigo}")
if codigo == 200 and d.get("success"):
    for a in d.get("result") or []:
        print(f"     · {a.get('name')}   id={a.get('id')}")
else:
    print("     ", json.dumps(d.get("errors") or d)[:300])

codigo, d = pide("/user")
print(f"\n  3) usuario -> HTTP {codigo}")
if codigo == 200 and d.get("success"):
    u = d.get("result") or {}
    print(f"     {u.get('email')}")
else:
    print("     ", json.dumps(d.get("errors") or d)[:300])
