"""Registra el subdominio de workers.dev de la cuenta."""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = __import__("os").environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = __import__("os").environ.get("CLOUDFLARE_ACCOUNT_ID", "")
API = "https://api.cloudflare.com/client/v4"


def pide(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(API + ruta, data=datos, method=metodo, headers={
        "Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"_error": str(e)}


c, d = pide("GET", f"/accounts/{CUENTA}/workers/subdomain")
print(f"  subdominio actual -> HTTP {c}  {json.dumps(d.get('result'))[:120]}")

for candidato in ("supermalato", "supermalato-tienda", "malato", "malatosupermercado"):
    c, d = pide("PUT", f"/accounts/{CUENTA}/workers/subdomain", {"subdomain": candidato})
    if c == 200 and d.get("success"):
        print(f"\n  REGISTRADO: {candidato}.workers.dev")
        print("  ", json.dumps(d.get("result"))[:200])
        break
    err = (d.get("errors") or [{}])[0]
    print(f"  '{candidato}' no: {err.get('message', '')[:110]}")
