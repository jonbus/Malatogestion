"""La prueba de las extra, con una fecha de mentira."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-extra-urgente.mjs"
t = open(p, encoding="utf-8").read()
viejo = "const dosDias = '2026-10-28';"
if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(viejo, "const dosDias = '2099-06-15';", 1))
print("  la prueba usa una fecha de mentira")
