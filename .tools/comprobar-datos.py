"""Comprueba que TODO lo que la app lee de DATOS existe de verdad.

Este fallo (leer una clave que no está) tumba la pantalla entera y no dice dónde.
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/nube/public/index.html", encoding="utf-8").read()
js = h.split("<script>")[-1].split("</script>")[0]

i = js.find("const DATOS = ")
prof = 0
for k in range(js.find("{", i), len(js)):
    if js[k] == "{":
        prof += 1
    elif js[k] == "}":
        prof -= 1
        if prof == 0:
            DATOS = json.loads(js[js.find("{", i):k + 1])
            break

fallos = 0
print("  === lo que la app lee de DATOS ===")
for m in sorted(set(re.findall(r"DATOS\.(\w+)\.(\w+)", js))):
    grupo, clave = m
    existe = grupo in DATOS and clave in DATOS[grupo]
    marca = "OK   " if existe else "FALTA"
    print(f"   {marca} DATOS.{grupo}.{clave}")
    if not existe:
        fallos += 1

print("\n  === lo que la app lee de DATOS.turnos ===")
for m in sorted(set(re.findall(r"T\.(\w+)", js))):
    if m in ("coord", "oficina", "tienda", "tiendaSemanas", "ausencias",
             "tiendaAncla", "tiendaSemanaAncla", "cicloAncla", "tiendaSemana1", "rota"):
        existe = m in DATOS.get("turnos", {})
        print(f"   {'OK   ' if existe else 'FALTA'} T.{m}")
        if not existe:
            fallos += 1

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
