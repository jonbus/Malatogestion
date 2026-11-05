"""La piruleta: el agradecimiento en euskera, y unos globos al lado del logo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cartel-piruleta.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    elif t.count(v) == 0:
        print("  NO ENCONTRADO: " + e)
    else:
        print(f"  OJO, aparece {t.count(v)} veces: " + e)


# 1 · el agradecimiento, solo en euskera
rep('centro(2810, "¡GRACIAS POR VENIR!", 120, ROUND)',
    'centro(2800, "ESKERRIK ASKO ETORTZEAGATIK!", 96, ROUND)',
    "el agradecimiento en euskera")

# 2 · los globos, al lado derecho del logotipo
rep('centro(90 + la + 30, "2006. urtetik ZUREKIN", 64)',
    '''centro(90 + la + 30, "2006. urtetik ZUREKIN", 64)

# --- unos globos al lado del logotipo, para que se vea fiesta desde arriba
def _globo(cx, cy, r, largo=1.0):
    d.ellipse([cx - r, cy - r * 1.15, cx + r, cy + r * 1.15],
              fill=BLANCO, outline=NEGRO, width=G)
    d.polygon([(cx - r * 0.16, cy + r * 1.12), (cx + r * 0.16, cy + r * 1.12), (cx, cy + r * 1.3)],
              fill=NEGRO)
    pts = [(cx, cy + r * 1.3)]
    for k in range(1, max(3, int(6 * largo))):
        pts.append((cx + (16 if k % 2 else -16), cy + r * 1.3 + k * r * 0.3 * largo))
    d.line(pts, fill=NEGRO, width=6, joint="curve")


_globo(2010, 260, 118, 0.65)
_globo(2240, 165, 84, 0.5)
_globo(1880, 420, 62, 0.45)''',
    "los globos, al lado del logotipo")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
