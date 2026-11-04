"""Copia los tres campos al alta de encargos (encargo-fecha)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r"docs\nube\netlify\functions\nucleo.js"
t = open(p, encoding="utf-8").read()

ANCLA = "        que: que,"
NUEVO = ("        que: que,\n"
         "        producto: c.producto ? String(c.producto).slice(0, 40) : undefined,\n"
         "        cantidad: Number.isFinite(Number(c.cantidad)) ? Number(c.cantidad) : undefined,\n"
         "        nota: c.nota ? String(c.nota).slice(0, 300) : undefined,")

veces = t.count(ANCLA)
print(f"  la línea aparece {veces} vez/veces")

if veces != 1:
    print("  NO ES ÚNICA: no se toca")
    sys.exit(1)

t = t.replace(ANCLA, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  el alta de encargos guarda producto, cantidad y nota")
