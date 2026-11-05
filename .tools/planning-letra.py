"""El planning apaisado, con la letra más grande."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\planning-apaisado.py"
t = open(p, encoding="utf-8").read()

CAMBIOS = [
    ("def cabecera(x, y, texto, tam=46):", "def cabecera(x, y, texto, tam=64):"),
    ("def hora(x, y, h, texto, ancho_texto, tam=40):", "def hora(x, y, h, texto, ancho_texto, tam=54):"),
    ('centro(80, "MALATO · 20 ANIVERSARIO", 96)', 'centro(50, "MALATO · 20 ANIVERSARIO", 132)'),
    ("centro(196, ", "centro(212, "),
    ('·  10:00 – 14:30", 46)', '·  10:00 – 14:30", 58)'),
    ("d.line([M, 300, W - M, 300], fill=NEGRO, width=10)",
     "d.line([M, 320, W - M, 320], fill=NEGRO, width=10)"),
    ("iy = 355", "iy = 380"),
    ("dy = 355", "dy = 380"),
    ('cabecera(IX, iy, "EL DÍA, HORA A HORA", 52)', 'cabecera(IX, iy, "EL DÍA, HORA A HORA", 70)'),
    ('cabecera(DX, dy, "LA MESA, EN ESTE ORDEN", 52)', 'cabecera(DX, dy, "LA MESA, EN ESTE ORDEN", 70)'),
    ('cabecera(DX, dy, "NO PUEDE FALLAR", 52)', 'cabecera(DX, dy, "NO PUEDE FALLAR", 70)'),
    ("font=f(ROUND, 40)", "font=f(ROUND, 52)"),
    ("dy + i * 46", "dy + i * 62"),
    ("dy += 46 * max(1, len(lineas)) + 6", "dy += 62 * max(1, len(lineas)) + 8"),
    ('centro(H - 122, "500 papeletas · 113 premios · 500 piruletas · 500 palmeritas · 2 niños", 38)',
     'centro(H - 130, "500 papeletas · 113 premios · 500 piruletas · 500 palmeritas · 2 niños", 56)'),
]

for viejo, nuevo in CAMBIOS:
    if viejo in t:
        t = t.replace(viejo, nuevo)
        print("  ok  " + viejo[:50])
    else:
        print("  NO ENCONTRADO: " + viejo[:50])

open(p, "w", encoding="utf-8").write(t)
print("\n  hecho")
