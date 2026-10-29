"""El ✎ en cada tarea del día, buscándolo por posición."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

i = t.find("function bloque(titulo, tareas, pre, extra){")
if i < 0:
    print("  NO ENCONTRADO bloque()")
    sys.exit(1)

marca = "lineaCascada(k, t.t) + `</div>`;"
j = t.find(marca, i)
if j < 0:
    print("  NO ENCONTRADO el sitio")
    sys.exit(1)

if "abrirPlantilla" in t[i:j]:
    print("  ya estaba")
    sys.exit(0)

nuevo = ("lineaCascada(k, t.t) + `<div class=\"casc-linea\">` +\n"
         "           `<button class=\"btn-add-2\" type=\"button\" onclick=\"abrirPlantilla('${k}')\">` +\n"
         "           `✎ cambiar</button></div>` + `</div>`;")

t = t[:j] + nuevo + t[j + len(marca):]
t = t.replace("v-2026-10-26-73", "v-2026-10-26-74")
open(p, "w", encoding="utf-8").write(t)
print("  ok  el ✎ en cada tarea del día")
