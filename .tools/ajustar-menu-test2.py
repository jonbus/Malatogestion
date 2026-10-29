"""La prueba del menú necesita fechaSel."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-menu.mjs"
t = open(p, encoding="utf-8").read()
viejo = '  const DIA = "2026-10-26";'
nuevo = '  const DIA = "2026-10-26";\n  let fechaSel = "2026-10-26";'
cuantos = t.count(viejo)
if not cuantos:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo)
open(p, "w", encoding="utf-8").write(t)
print(f"  fechaSel añadido ({cuantos} sitios)")
