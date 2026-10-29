"""Lista las rutas del núcleo y qué nombre usa la app."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

n = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
rutas = sorted(set(re.findall(r"['\"](/api/[a-zA-Z-]+)['\"]", n)))
print("  RUTAS DEL SERVIDOR (nucleo.js):")
for r in rutas:
    print("    " + r)

a = open("docs/nube/public/index.html", encoding="utf-8").read()
usadas = sorted(set(re.findall(r"['\"](/api/[a-zA-Z-]+)['\"]", a)))
print("\n  RUTAS QUE LLAMA LA APP:")
for r in usadas:
    marca = "" if r in rutas else "   <<< NO EXISTE EN EL SERVIDOR"
    print("    " + r + marca)

faltan = [r for r in usadas if r not in rutas]
print(f"\n  rutas que la app llama y el servidor no tiene: {len(faltan)}")
for r in faltan:
    print("    " + r)
