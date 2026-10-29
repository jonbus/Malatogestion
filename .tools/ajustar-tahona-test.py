"""La prueba del pan, al día: ahora vive en «Registro de panes»."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\probar-tahona.mjs"
t = open(p, encoding="utf-8").read()

cambios = 0
for viejo, nuevo in (
    ("ok('coordinación tiene la entrada', html.includes('bloqueTahona(\"entrada\")'));",
     "ok('la sección del pan existe', html.includes('function pintaPanes'));"),
    ("ok('tienda tarde tiene la devolución', html.includes('bloqueTahona(\"devolucion\")'));",
     "ok('el pan tiene su botón en el menú', html.includes('Registro de panes'));"),
):
    if viejo in t:
        t = t.replace(viejo, nuevo, 1)
        cambios += 1
        print("  ok  ajustada una comprobación")
    else:
        print("  (no estaba):", viejo[:60])

open(p, "w", encoding="utf-8").write(t)
print(f"  cambios: {cambios}")
