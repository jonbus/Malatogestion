"""Revisa el catalogo: agrupa por familia para detectar clasificaciones raras."""
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
cat = json.load(open("docs/tareas-catalogo.json", encoding="utf-8"))

for p in cat["puestos"]:
    print("=" * 76)
    print(f"{p['etiqueta'].upper()}")
    print("=" * 76)
    fam = defaultdict(list)
    for t in p["tareas"]:
        fam[t["familia"]].append(t)
    for f in sorted(fam):
        print(f"\n  [{f}]  ({len(fam[f])})")
        for t in sorted(fam[f], key=lambda x: x["nombre"].lower()):
            print(f"     {t['nombre']}")
