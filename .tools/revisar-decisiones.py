"""Busca identificadores de decision duplicados o fuera de secuencia."""
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
txt = open("docs/DECISIONES.md", encoding="utf-8").read()

ids = re.findall(r"^\|\s*(D-\d+)\s*\|", txt, re.M)
c = Counter(ids)
dup = {k: v for k, v in c.items() if v > 1}
print(f"  filas de decision: {len(ids)}  ·  identificadores unicos: {len(c)}")
if dup:
    print("  DUPLICADOS:")
    for k, v in sorted(dup.items()):
        print(f"    {k} aparece {v} veces")
        for m in re.finditer(r"^\|\s*" + k + r"\s*\|(.{0,80})", txt, re.M):
            print(f"       -> {m.group(1).strip()[:74]}")
else:
    print("  sin duplicados")

# secuencia esperada hasta el maximo
nums = sorted({int(i.split("-")[1]) for i in c})
faltan = [n for n in range(1, max(nums) + 1) if n not in nums]
print(f"  rango: {min(nums)} a {max(nums)}")
print(f"  numeros que faltan: {faltan or 'ninguno'}")
