"""La prueba del menú necesita pintaTabs en su entorno."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-menu.mjs"
t = open(p, encoding="utf-8").read()
viejo = "  function pinta(){ C.n++; }"
nuevo = "  function pinta(){ C.n++; }\n  function pintaTabs(){}"
if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)
open(p, "w", encoding="utf-8").write(t)
print("  prueba ajustada")
