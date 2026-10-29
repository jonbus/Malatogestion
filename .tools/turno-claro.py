"""El turno, escrito claro: «por la tarde» / «por la mañana»."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

viejo = '      `${e.turno ? " · " + (e.turno === "tarde" ? "tarde" : "mañana") : ""}</span>` +'
nuevo = ('      `${e.turno === "tarde" ? " · por la tarde" : '
         'e.turno === "manana" ? " · por la mañana" : ""}</span>` +')

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)
t = t.replace("v-2026-10-26-31", "v-2026-10-26-32")
open(p, "w", encoding="utf-8").write(t)
print("  ok  el turno se lee claro")
