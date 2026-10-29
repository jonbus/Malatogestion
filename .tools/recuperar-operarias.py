"""Recupera las tareas de tienda del catalogo archivado y las agrupa."""
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
cat = json.load(open("docs/archivo/tareas-catalogo.json", encoding="utf-8"))
p = next(x for x in cat["puestos"] if x["clave"] == "tienda")
print(f"  tareas de tienda recuperadas: {len(p['tareas'])}")
DIAS = {"LUN": "lun", "MAR": "mar", "MIE": "mié", "JUE": "jue", "VIE": "vie", "SAB": "sáb", "DOM": "dom"}

por_dias = defaultdict(list)
for t in p["tareas"]:
    d = t.get("dias", [])
    por_dias[len(d)].append(t)

print("\n  === LAS QUE TOCAN LOS 7 DÍAS (candidatas a RUTINA) ===")
for t in sorted(por_dias.get(7, []), key=lambda x: x["nombre"].lower()):
    print(f"    · {t['nombre']}")

print("\n  === LAS QUE TOCAN DE 2 A 6 DÍAS ===")
for n in (6, 5, 4, 3, 2):
    for t in sorted(por_dias.get(n, []), key=lambda x: x["nombre"].lower()):
        print(f"    {n}d {'/'.join(DIAS.get(d, d) for d in t['dias']):<22} · {t['nombre']}")

print("\n  === LAS QUE TOCAN 1 DÍA ===")
for t in sorted(por_dias.get(1, []), key=lambda x: x["nombre"].lower()):
    print(f"    {DIAS.get(t['dias'][0], t['dias'][0]):<4} · {t['nombre']}")
