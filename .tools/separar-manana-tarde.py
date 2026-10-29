"""Separa las tareas de tienda en MAÑANA y TARDE usando el turno del catalogo archivado."""
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
cat = json.load(open("docs/archivo/tareas-catalogo.json", encoding="utf-8"))
op = next(x for x in cat["puestos"] if x["clave"] == "tienda")
por_id = {t["id"]: t for t in op["tareas"]}

manana = defaultdict(list)
tarde = defaultdict(list)
sin = defaultdict(list)
for dia, items in op["semana"].items():
    for x in items:
        t = por_id.get(x["id"])
        if not t:
            continue
        if x["t"] == "M":
            manana[dia].append(t["nombre"])
        elif x["t"] == "T":
            tarde[dia].append(t["nombre"])
        else:
            sin[dia].append(t["nombre"])

print("  === MAÑANA (turno M) ===")
for d in ("LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"):
    print(f"    {d}: {len(manana[d])} tareas")
print(f"  === TARDE (turno T) ===")
for d in ("LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"):
    print(f"    {d}: {len(tarde[d])} tareas")
print(f"  === SIN TURNO ===")
for d in ("LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"):
    if sin[d]:
        print(f"    {d}: {len(sin[d])} tareas")

print("\n  === TAREAS DISTINTAS DE LA TARDE ===")
distintas = sorted({n for v in tarde.values() for n in v}, key=str.lower)
for n in distintas:
    print(f"    · {n}")
