"""Ajusta la prueba del menú al nuevo corte."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-menu.mjs"
t = open(p, encoding="utf-8").read()
viejo = "js.indexOf('function qui\u00e9nCorta')"
if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, "js.indexOf('function pintaPanes')", 1)
open(p, "w", encoding="utf-8").write(t)
print("  prueba ajustada")
