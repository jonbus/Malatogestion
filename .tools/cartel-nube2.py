"""La letra tiene que quedar DENTRO de la nube, y la caja de abajo verde y limpia."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\cartel-color.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# --- los bollos, solo en el borde de arriba
rep('''        # los bollos de arriba
        for fx, fy, fr in [(0.10, 0.44, 0.20), (0.24, 0.30, 0.24), (0.40, 0.38, 0.21),
                           (0.52, 0.24, 0.25), (0.66, 0.34, 0.22), (0.79, 0.28, 0.23),
                           (0.91, 0.46, 0.19)]:
            cx = x0 + ancho * fx
            cy = y0 + alto * fy
            r = alto * fr
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)''',
'''        # los bollos, asomando solo por el borde de arriba
        for fx, fr in [(0.12, 0.17), (0.26, 0.20), (0.41, 0.18), (0.55, 0.21),
                       (0.69, 0.19), (0.83, 0.20), (0.94, 0.16)]:
            cx = x0 + ancho * fx
            r = alto * fr
            cy = y0 + r * 0.92
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)''',
    "los bollos, al borde")

# --- la base, mas alta, para que el texto quede dentro
rep('''        d.rounded_rectangle([x0 + ancho * 0.04, y0 + alto * 0.34,
                             x1 - ancho * 0.04, y1 - alto * 0.06],
                            radius=alto * 0.42, fill=color)''',
    '''        d.rounded_rectangle([x0 + ancho * 0.03, y0 + alto * 0.10,
                             x1 - ancho * 0.03, y1 - alto * 0.04],
                            radius=alto * 0.30, fill=color)''',
    "la base, mas alta")

# --- la nube, mas alta
rep("    nube(120, 470, W - 120, 1520, VERDE_MALATO)",
    "    nube(110, 430, W - 110, 1590, VERDE_MALATO)", "la nube, mas alta")

# --- la fecha, dentro
rep('centro(560, T["domingo"], 140, ROUND, BLANCO)', 'centro(650, T["domingo"], 140, ROUND, BLANCO)', "domingo")
rep('centro(700, T["ocho"], 372, ROUND, BLANCO)', 'centro(790, T["ocho"], 360, ROUND, BLANCO)', "el 8")
rep('centro(1112, T["noviembre"], 124, ROUND, BLANCO)', 'centro(1180, T["noviembre"], 124, ROUND, BLANCO)', "el mes")
rep('centro(1252, T["aniversario"], 94, ROUND, BLANCO)', 'centro(1310, T["aniversario"], 94, ROUND, BLANCO)', "20 aniversario")
rep('centro(1364, T["manana"], 90, COMIC, BLANCO)', 'centro(1420, T["manana"], 90, COMIC, BLANCO)', "por la manana")

# --- y la caja de abajo: cuadrada y verde, con letra blanca
rep('''    nube((W - ancho) / 2 - 40, caja_y - 40, (W + ancho) / 2 + 40, caja_y + alto_caja + 20,
         VERDE_MALATO)''',
    '''    d.rounded_rectangle([(W - ancho) / 2, caja_y, (W + ancho) / 2, caja_y + alto_caja],
                        radius=48, fill=VERDE_MALATO)''',
    "la caja de abajo, verde y limpia")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
