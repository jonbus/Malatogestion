"""Arregla la comprobación antigua de ver-pestanas."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/ver-pestanas.mjs"
t = open(p, encoding="utf-8").read()
t = t.replace("t.includes('Ofertas dadas de alta')", "t.includes('Dadas de alta \u00b7 ')")
open(p, "w", encoding="utf-8").write(t)
print("  comprobación actualizada")
