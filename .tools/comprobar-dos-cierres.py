"""Muestra los dos «antes de irse» y comprueba que no hay repetidos."""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/momentos/tienda.html", encoding="utf-8").read()
d = json.loads(re.search(r"const D = (\{.*?\});\n", h, re.S).group(1))

for clave, etiqueta in (("manana", "MAÑANA · antes de irse (cierre del mediodía)"),
                        ("tarde", "TARDE · antes de irse (antes del cierre de la noche)")):
    print(f"  === {etiqueta} ===")
    for i, t in enumerate(d[clave]["antes"], 1):
        extra = ""
        if t.get("partes"):
            extra = f"   [{len(t['partes'])} partes]"
        if t.get("n"):
            extra += f"   ({t['n'][:50]})"
        print(f"    {i:>2}. {t['t']}{extra}")
    print()

# comprobar que no se repite nada entre el «antes de irse» de la tarde y el cierre
print("  === REPETIDOS entre la tarde-antes y el cierre ===")
cierre = [x["t"] for s in d["cierre"] for x in s["tareas"]]
rep = 0
for t in d["tarde"]["antes"]:
    for c in cierre:
        if t["t"].lower() in c.lower() or c.lower() in t["t"].lower():
            print(f"    «{t['t']}»  ~  «{c}»")
            rep += 1
print("    ninguno" if not rep else "")
