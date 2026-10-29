"""Saca exactamente qué envía la app a cada ruta."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/nube/public/index.html", encoding="utf-8").read()

for m in re.finditer(r'/api/[a-zA-Z-]+', h):
    ini = m.start()
    trozo = h[ini:ini + 420].replace("\n", " ")
    print(f"\n  --- {m.group(0)} ---")
    print("   " + trozo[:300])
