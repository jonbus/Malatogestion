"""Comprueba la integridad del catalogo y de la vista HTML."""
import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

cat = json.load(open("docs/tareas-catalogo.json", encoding="utf-8"))
tot = 0
for p in cat["puestos"]:
    n = len(p["tareas"])
    tot += n
    c = Counter(t["importancia"] for t in p["tareas"])
    print(f"  {p['etiqueta']:<15} {n:>3} tareas  |  "
          f"criticas={c['critica']} alta={c['alta']} media={c['media']} baja={c['baja']}")
print(f"  TOTAL: {tot}")

ids = [t["id"] for p in cat["puestos"] for t in p["tareas"]]
print(f"  ids unicos: {len(set(ids)) == len(ids)}  ({len(ids)} ids)")
fams = {(p["etiqueta"], t["familia"]) for p in cat["puestos"] for t in p["tareas"]}
print(f"  familias distintas: {len(fams)}")
sin_critica = [p["etiqueta"] for p in cat["puestos"] if not any(t["importancia"] == "critica" for t in p["tareas"])]
print(f"  puestos sin ninguna tarea critica: {sin_critica or 'ninguno'}")

html = open("docs/vista-tareas.html", encoding="utf-8").read()
m = re.search(r"const CATALOGO = (\{.*?\});\n", html, re.S)
d = json.loads(m.group(1))
print(f"  tareas dentro del HTML: {sum(len(p['tareas']) for p in d['puestos'])}")
print(f"  HTML sin recursos externos: {'http' not in html.split('<script>')[0].replace('http-equiv','')}")
