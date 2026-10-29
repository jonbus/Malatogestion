"""Ajusta la comprobación del traslado a la clave real."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/prueba-usuario-completa.mjs"
t = open(p, encoding="utf-8").read()
t = t.replace(
    "ok('I', 'el traslado queda guardado', !!estT.traslados[clave + ':x']);",
    "ok('I', 'el traslado queda guardado',\n"
    "  !!estT.traslados[hoy + '|x|' + T], Object.keys(estT.traslados || {}));")
open(p, "w", encoding="utf-8").write(t)
print("  comprobación corregida")
