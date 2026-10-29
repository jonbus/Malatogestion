"""Pone al día la comprobación del «volver al menú»."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-menu.mjs"
t = open(p, encoding="utf-8").read()
viejo = 'ok(\'vuelve al menú\', js.includes(\'tab = "menu"; pinta();\'));'
nuevo = 'ok(\'vuelve al menú\', js.includes(\'tab = "menu"; pintaTabs(); pinta();\'));'
if viejo not in t:
    # por si lleva otras comillas
    for cand in t.split("\n"):
        if "vuelve al men" in cand:
            print("  la línea es:", cand)
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
print("  comprobación al día")
