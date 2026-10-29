"""Comprueba los permisos del token y el formato del núcleo."""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = __import__("os").environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = __import__("os").environ.get("CLOUDFLARE_ACCOUNT_ID", "")
API = "https://api.cloudflare.com/client/v4"


def pide(ruta):
    req = urllib.request.Request(API + ruta, headers={
        "Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
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


print("  === permisos ===")
for nombre, ruta in [
    ("Workers KV", f"/accounts/{CUENTA}/storage/kv/namespaces"),
    ("Pages", f"/accounts/{CUENTA}/pages/projects"),
    ("Workers scripts", f"/accounts/{CUENTA}/workers/scripts"),
]:
    c, d = pide(ruta)
    bien = c == 200 and d.get("success")
    print(f"   {'OK   ' if bien else 'NO   '}{nombre} (HTTP {c})")
    if not bien:
        err = (d.get("errors") or [{}])[0]
        print(f"         {err.get('message', '')[:100]}")

print("\n  === el núcleo: cómo exporta ===")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
print("   primeras líneas:")
for l in t.splitlines()[:6]:
    print("     " + l[:100])
print("   últimas líneas:")
for l in t.splitlines()[-8:]:
    print("     " + l[:100])
print(f"   tamaño: {len(t)} caracteres")
