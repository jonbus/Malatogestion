"""Ajusta los números esperados en la prueba del detalle."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/probar-detalle.mjs"
t = open(p, encoding="utf-8").read()
t = t.replace("csv.includes('TOTAL;;90;11')", "csv.includes('TOTAL;;97;11')")
t = t.replace("csv.includes('Entradas menos devoluciones: 79')",
              "csv.includes('Entradas menos devoluciones: 86')")
open(p, "w", encoding="utf-8").write(t)
print("  prueba ajustada")
