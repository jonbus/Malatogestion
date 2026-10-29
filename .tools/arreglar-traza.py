"""Deja la traza del error sin saltos de línea problemáticos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

ini = t.find("  const traza = String(r.stack")
if ini < 0:
    print("  no encuentro la línea de la traza")
    sys.exit(0)
fin = t.find("\n", t.find("ensenarFallo", ini))
fin2 = t.find("\n", fin + 1)
bloque = t[ini:fin2]
print("  --- antes ---")
print(bloque)

nuevo = (
    '  const traza = String(r.stack || "").replace(/\\s+/g, " ").slice(0, 150);\n'
    '  ensenarFallo("promesa: " + (r.message || r) + (traza ? "   [" + traza + "]" : ""));'
)
t = t[:ini] + nuevo + t[fin2:]
open(p, "w", encoding="utf-8").write(t)

print("  --- después ---")
i = t.find("  const traza")
print(t[i:i + 200])
