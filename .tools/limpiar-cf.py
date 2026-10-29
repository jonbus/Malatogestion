"""Deja el almacén de Cloudflare completamente vacío."""
import json
import re
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = __import__("os").environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = __import__("os").environ.get("CLOUDFLARE_ACCOUNT_ID", "")
KV = "544a4e67fd9c4acaab5a0e7d2dcfbd35"
API = "https://api.cloudflare.com/client/v4"

t = open("docs/nube/cloudflare/nucleo.js", encoding="utf-8").read()
m = re.search(r"const CLAVE = '([^']+)'", t)
clave = m.group(1) if m else "estado"
print("  clave del almacén:", clave)


def pide(metodo, ruta):
    req = urllib.request.Request(API + ruta, method=metodo, headers={
        "Authorization": "Bearer " + TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()


c, _ = pide("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/keys")
print(f"  claves antes: HTTP {c} {_.decode('utf-8', 'replace')[:120]}")

c, b = pide("DELETE",
            f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{clave}")
print(f"  borrar «{clave}»: HTTP {c}")

c, b = pide("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/keys")
print(f"  claves después: {b.decode('utf-8', 'replace')[:160]}")
