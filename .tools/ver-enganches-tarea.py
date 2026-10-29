"""Dónde se engancha cada campo del formulario de tareas extra."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

funciones = [(m.start(), m.group(1)) for m in re.finditer(r"function (pinta\w+)", js)]

for clave in ("tarea-txt", "tarea-puesto", "tarea-turno", "tarea-tipo", "tarea-add"):
    i = js.find('getElementById("' + clave + '")')
    if i < 0:
        print(f"  {clave}: NO se engancha por id")
        continue
    antes = [n for p, n in funciones if p < i]
    print(f"  {clave}: dentro de {antes[-1] if antes else '?'}")

# y el inline
for clave in ("tarea-add",):
    if 'onclick="anadirTareaExtra()"' in js:
        print("  el botón de añadir lleva su propia orden: SÍ")
    else:
        print("  el botón de añadir lleva su propia orden: NO")

i = js.find("function pintaTareasExtra")
if i < 0:
    i = js.find("btn-nueva-tarea")
print("\n  el formulario de tareas extra vive en:", js[max(0, i - 200):i + 120].replace("\n", " ")[:300])
