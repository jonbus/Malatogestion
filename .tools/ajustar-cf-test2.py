"""Pone al día la comprobación de la Jefa."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-cloudflare.mjs"
lineas = open(p, encoding="utf-8").read().split("\n")

cambiadas = 0
for i, l in enumerate(lineas):
    if "pesta\u00f1as de la Jefa" in l:
        lineas[i] = "ok('trae los botones de la Jefa', html.includes('gerencia: ['));"
        cambiadas += 1

if not cambiadas:
    print("  NO ENCONTRADO")
    sys.exit(1)

open(p, "w", encoding="utf-8").write("\n".join(lineas))
print(f"  {cambiadas} comprobación puesta al día")
