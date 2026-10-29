"""La prueba esperaba pestañas de la Jefa; ahora son botones."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-cloudflare.mjs"
t = open(p, encoding="utf-8").read()

viejo = "ok('trae las pestañas de la Jefa', html.includes('[\"general\",\"El día\"]')"
nuevo = "ok('trae los botones de la Jefa', html.includes('gerencia: [')"

if viejo not in t:
    # se busca la línea por su texto
    for linea in t.split("\n"):
        if "pestañas de la Jefa" in linea:
            print("  la línea es:", linea.strip())
    sys.exit(1)

t = t.replace(viejo, nuevo, 1)
open(p, "w", encoding="utf-8").write(t)
print("  prueba al día")
