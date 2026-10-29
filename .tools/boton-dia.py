"""El «＋» en las tareas del día: se busca por posición y se inserta."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("function bloque(titulo, tareas, pre, extra){")
if i < 0:
    print("  NO ENCONTRADO bloque()")
    sys.exit(1)

marca = "${sub}</div>`;"
j = t.find(marca, i)
if j < 0:
    print("  NO ENCONTRADO el cierre del item")
    sys.exit(1)

if "lineaCascada(k, t.t)" in t[i:j]:
    print("  ya estaba puesto")
    sys.exit(0)

t = t[:j] + "${sub}` + lineaCascada(k, t.t) + `</div>`;" + t[j + len(marca):]
t = t.replace("v-2026-10-26-63", "v-2026-10-26-64")
open(p, "w", encoding="utf-8").write(t)
print("  ok  el botón en las tareas del día")
