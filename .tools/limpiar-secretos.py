"""Quita los secretos del código antes de subirlo a ningún sitio.

El token de Cloudflare y la clave de la Jefa estaban escritos dentro de los
scripts y de los documentos. En un repositorio compartido eso es una fuga.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
PIN = "«la clave de la Jefa — se dice aparte, no se escribe»"
CUENTA = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")

TOKEN_ENV = '''TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")'''
TOKEN_ENV_SIN_OS = '''TOKEN = __import__("os").environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = __import__("os").environ.get("CLOUDFLARE_ACCOUNT_ID", "")'''

cambiados = []
problemas = []

for raiz, carpetas, ficheros in os.walk("."):
    carpetas[:] = [c for c in carpetas
                   if c not in (".git", "node_modules", ".npmcache", ".npm-cache",
                                ".tmp-asador", "_cacache", "content-v2")]
    for nombre in ficheros:
        if not nombre.endswith((".py", ".mjs", ".js", ".json", ".md", ".toml", ".html", ".txt")):
            continue
        ruta = os.path.join(raiz, nombre)
        try:
            t = open(ruta, encoding="utf-8").read()
        except Exception:
            continue
        original = t

        # el token y la cuenta
        if TOKEN in t or CUENTA in t:
            tiene_os = re.search(r"^import os$", t, re.M) is not None
            reemplazo = TOKEN_ENV if tiene_os else TOKEN_ENV_SIN_OS
            t = re.sub(r'TOKEN\s*=\s*"' + re.escape(TOKEN) + r'"', reemplazo.split("\n")[0], t)
            t = re.sub(r'CUENTA\s*=\s*"' + re.escape(CUENTA) + r'"',
                       reemplazo.split("\n")[1], t)
            t = t.replace(TOKEN, "«token en la variable CLOUDFLARE_API_TOKEN»")
            t = t.replace(CUENTA, "«cuenta en CLOUDFLARE_ACCOUNT_ID»")

        # la clave de la Jefa, en los documentos
        if PIN in t:
            t = t.replace(PIN, "«la clave de la Jefa — se dice aparte, no se escribe»")

        if t != original:
            open(ruta, "w", encoding="utf-8").write(t)
            cambiados.append(ruta)

print(f"  ficheros limpiados: {len(cambiados)}")
for c in cambiados:
    print("   ", c)

# comprobación final
quedan = 0
for raiz, carpetas, ficheros in os.walk("."):
    carpetas[:] = [c for c in carpetas
                   if c not in (".git", "node_modules", ".npmcache", ".npm-cache",
                                ".tmp-asador", "_cacache", "content-v2")]
    for nombre in ficheros:
        ruta = os.path.join(raiz, nombre)
        try:
            t = open(ruta, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if TOKEN in t or PIN in t:
            print("  OJO, sigue en:", ruta)
            quedan += 1
print(f"\n  ficheros con secretos todavía: {quedan}")
