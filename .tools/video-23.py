"""La foto «23» va en el segundo 23.

Se saca del barajado y se coloca en su sitio. El resto no cambia.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cuadros-video.py"
t = open(p, encoding="utf-8").read()

ANCLA = "fotos = primero + resto"

NUEVO = """fotos = primero + resto

# la foto «23», clavada en el segundo 23
_f23 = [f for f in fotos if os.path.splitext(f)[0].strip() == "23"]
if _f23:
    fotos.remove(_f23[0])
    # 2 cartelas del principio + 3 del cierre + «Todas» + las fotos
    _total = 2 + 3 + 1 + len(fotos) + 1
    _dur = 124.36 / _total
    _idx = max(0, min(len(fotos), int(round(23 / _dur)) - 2))
    fotos.insert(_idx, _f23[0])
    print(f"  la «23» va en el puesto {_idx + 1} de las fotos (sobre el segundo {round((_idx + 2) * _dur, 1)})")
else:
    print("  no hay ninguna foto que se llame 23")"""

if ANCLA not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(ANCLA, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  la «23», en el segundo 23")
