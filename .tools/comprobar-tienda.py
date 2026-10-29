"""Comprueba el orden de lo de siempre en la tarde y las fregonas."""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/momentos/tienda.html", encoding="utf-8").read()
d = json.loads(re.search(r"const D = (\{.*?\});\n", h, re.S).group(1))

print("  === LO DE SIEMPRE · TARDE ===")
for i, t in enumerate(d["tarde"]["rutina"], 1):
    nota = t.get("n")
    linea = f"    {i:>2}. {t['t']}"
    if nota:
        linea += f"   [{nota[:58]}]"
    print(linea)

print("\n  === LO DE SIEMPRE · MAÑANA ===")
for i, t in enumerate(d["manana"]["rutina"], 1):
    print(f"    {i:>2}. {t['t']}")

print("\n  === LUNES MAÑANA · fregonas ===")
for t in d["manana"]["porDia"]["LUN"]:
    if "fregona" in t["t"].lower():
        print(f"    {t['t']}  ->  {t.get('n')}")

print("\n  === producto de limpieza ===")
print(f"    opciones: {d['productos']}")

print("\n  === tareas que preguntan producto (solo desinfectar) ===")
todas = (d["manana"]["rutina"] + d["manana"]["antes"]
         + [x for v in d["manana"]["porDia"].values() for x in v]
         + d["tarde"]["rutina"] + d["tarde"]["antes"]
         + [x for v in d["tarde"]["porDia"].values() for x in v])
con = [t["t"] for t in todas if t.get("producto")]
sin = [t["t"] for t in todas if t.get("t") and not t.get("producto") and "limpiar" in t["t"].lower()]
print(f"    CON producto ({len(con)}):")
for x in con:
    print(f"      · {x}")
print(f"    SIN producto, y son limpiezas normales ({len(sin)}):")
for x in sin:
    print(f"      · {x}")
