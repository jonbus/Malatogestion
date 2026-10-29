"""Comprueba el cierre y busca duplicados con el «antes de irse» de la tarde."""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/momentos/tienda.html", encoding="utf-8").read()
d = json.loads(re.search(r"const D = (\{.*?\});\n", h, re.S).group(1))

tot = 0
print("  === EL CIERRE ===")
for s in d["cierre"]:
    marcas = sum(len(t.get("partes", [])) or 1 for t in s["tareas"])
    tot += marcas
    print(f"    {s['sec'][:52]:<54} {len(s['tareas']):>2} tareas, {marcas:>2} marcas")
print(f"    {'TOTAL':<54} {tot:>2} marcas")

print("\n  === «ANTES DE IRSE» DE LA TARDE ===")
for t in d["tarde"]["antes"]:
    print(f"    · {t['t']}")


def norm(s):
    s = s.lower()
    for ch in "áéíóúü.,()¿?":
        s = s.replace(ch, "")
    return set(w for w in s.split() if len(w) > 3)


print("\n  === POSIBLES REPETIDOS: «antes de irse» de la tarde vs cierre ===")
cierre_todo = []
for s in d["cierre"]:
    for t in s["tareas"]:
        cierre_todo.append((s["sec"], t["t"]))

for t in d["tarde"]["antes"]:
    a = norm(t["t"])
    for sec, ct in cierre_todo:
        b = norm(ct)
        comunes = a & b
        if len(comunes) >= 2:
            print(f"    «{t['t']}»")
            print(f"        ~ cierre [{sec[:30]}] {ct}")
            print(f"          palabras en común: {', '.join(sorted(comunes))}")
