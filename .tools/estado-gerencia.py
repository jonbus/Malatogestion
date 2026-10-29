"""Estado de la pantalla de gerencia."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

h = open("docs/nube/public/index.html", encoding="utf-8").read()
m = re.search(r"const PUESTOS = .*?;", h)
print("  puestos en el login:", m.group(0) if m else "?")
print("  aparece «gerencia» en la app:", "gerencia" in h.lower())
print()
print("  pantallas que hay:")
print("    Tienda        -> Mañana / Tarde / Cierre")
print("    Coordinación  -> Apertura / El día / Cierre")
print("    Gerencia      -> NO HAY")
