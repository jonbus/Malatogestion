"""Despliega la app de la tienda en Netlify, usando la sesión ya guardada en el PC.

No hace falta que nadie pegue ningún token: se lee de
    %APPDATA%\\netlify\\Config\\config.json
y nunca se imprime.

Uso:  python .tools/desplegar-tienda.py
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

API = "https://api.netlify.com/api/v1"
RAIZ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "nube")
NOMBRE = "tienda-malato"


def token():
    ruta = os.path.join(os.environ["APPDATA"], "netlify", "Config", "config.json")
    with open(ruta, encoding="utf-8") as f:
        cfg = json.load(f)
    for _usuario, datos in (cfg.get("users") or {}).items():
        t = (datos.get("auth") or {}).get("token")
        if t:
            return t
    raise SystemExit("no hay token en la sesión de Netlify")


def pedir(metodo, ruta, cuerpo=None, cabeceras=None, datos=None, tipo=None):
    h = {"Authorization": f"Bearer {TOKEN}"}
    if cabeceras:
        h.update(cabeceras)
    if cuerpo is not None:
        datos = json.dumps(cuerpo).encode("utf-8")
        h["Content-Type"] = "application/json"
    if tipo:
        h["Content-Type"] = tipo
    req = urllib.request.Request(API + ruta, data=datos, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            texto = r.read()
            return json.loads(texto) if texto else {}
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")[:300]
        raise SystemExit(f"  Netlify dice {e.code}: {detalle}")


TOKEN = token()

print("\n  1) Comprobando la cuenta...")
yo = pedir("GET", "/user")
print(f"     {yo.get('email')}")

print("\n  2) Buscando el sitio (o creándolo)...")
sitios = pedir("GET", "/sites?per_page=100")
sitio = next((s for s in sitios if s.get("name") == NOMBRE), None)
if sitio:
    print(f"     ya existe: {sitio['name']}")
else:
    sitio = pedir("POST", "/sites", {"name": NOMBRE})
    print(f"     creado: {sitio['name']}")
SITIO = sitio["id"]

print("\n  3) Montando el paquete...")
buf = io.BytesIO()
incluidos = 0
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    # la web
    publico = os.path.join(RAIZ, "public")
    for base, _dirs, ficheros in os.walk(publico):
        for f in ficheros:
            ruta = os.path.join(base, f)
            z.write(ruta, os.path.relpath(ruta, publico))
            incluidos += 1
    # la función
    # OJO: NO se mete ningún package.json dentro de netlify/functions/ —
    # si lo hay, Netlify deja de detectar las funciones (0 funciones).
    fn = os.path.join(RAIZ, "netlify", "functions")
    for f in ("api.mjs", "nucleo.js"):
        ruta = os.path.join(fn, f)
        z.write(ruta, f"netlify/functions/{f}")
        incluidos += 1
    # la configuración, para que Netlify sepa dónde están las funciones
    z.write(os.path.join(RAIZ, "netlify.toml"), "netlify.toml")
    incluidos += 1
    # las dependencias
    nm = os.path.join(RAIZ, "node_modules")
    for base, _dirs, ficheros in os.walk(nm):
        for f in ficheros:
            ruta = os.path.join(base, f)
            z.write(ruta, os.path.relpath(ruta, RAIZ))
            incluidos += 1
datos_zip = buf.getvalue()
print(f"     {incluidos} ficheros, {len(datos_zip)/1024:.0f} KB")

print("\n  4) Subiendo...")
despliegue = pedir("POST", f"/sites/{SITIO}/deploys", datos=datos_zip,
                   tipo="application/zip")
print(f"     despliegue {despliegue['id']}")

print("\n  5) Esperando a que esté listo...")
for i in range(60):
    time.sleep(5)
    estado = pedir("GET", f"/deploys/{despliegue['id']}")
    print(f"     {estado.get('state')}")
    if estado.get("state") == "ready":
        break
    if estado.get("state") == "error":
        raise SystemExit(f"  falló: {estado.get('error_message')}")
else:
    print("     sigue en curso; se puede comprobar en Netlify")

url = (sitio.get("ssl_url") or sitio.get("url") or "").rstrip("/")
print("\n  ============================================================")
print("   LISTO")
print("  ============================================================")
print(f"   Dirección:  {url}")
print(f"   Panel:      https://app.netlify.com/sites/{sitio.get('name')}")
print()
