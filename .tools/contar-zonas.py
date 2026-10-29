"""Cuenta las zonas por accion, para ver la granularidad del dia."""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/mi-dia.html", encoding="utf-8").read()
d = json.loads(re.search(r"const D = (\{.*?\});\n", h, re.S).group(1))
tot = 0
for a in d["acciones"]:
    n = len(a["zonas"])
    tot += n
    print(f"  {a['nombre']:<34} {n:>2} zonas")
print(f"  {'TOTAL':<34} {tot:>2} zonas al dia")
