"""Prueba la app en Cloudflare como lo haría un navegador."""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
BASE = "https://app.supermalato.workers.dev"


def pide(ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    h = {"User-Agent": UA, "Accept": "*/*"}
    if datos:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + ruta, data=datos, headers=h,
                                 method="POST" if datos else "GET")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return 0, {}, str(e).encode()


c, h, b = pide("/api/estado")
print(f"  /api/estado -> HTTP {c}")
print(f"     servidor: {h.get('Server', '?')}")
print(f"     cuerpo: {b[:200].decode('utf-8', 'replace')}")

c, h, b = pide("/")
print(f"\n  / -> HTTP {c}  ({len(b)} bytes)")
print(f"     {b[:120].decode('utf-8', 'replace')}")
