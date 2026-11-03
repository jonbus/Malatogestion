"""Cambia la banda coral por una nube verde, y la caja amarilla por verde."""
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

# --- el verde exacto de la «o» del logotipo
o = Image.open("docs/marca/logo-o-verde.png").convert("RGBA")
pixeles = [p[:3] for p in o.getdata() if p[3] > 200 and not (p[0] > 240 and p[1] > 240 and p[2] > 240)]
if pixeles:
    r = sum(p[0] for p in pixeles) // len(pixeles)
    g = sum(p[1] for p in pixeles) // len(pixeles)
    b = sum(p[2] for p in pixeles) // len(pixeles)
    verde = (r, g, b)
else:
    verde = (0, 120, 110)
print(f"  verde del logotipo: {verde}")

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


# el verde, como constante
rep('ROSA = (250, 190, 205)',
    f'ROSA = (250, 190, 205)\nVERDE_MALATO = {verde}      # el de la «o» del logotipo',
    "el verde del logotipo")

# la funcion de la nube
rep("    def estrella(cx, cy, r, color=AMARILLO):",
    '''    def nube(x0, y0, x1, y1, color):
        """Una nube: varios bollos unidos por la base, todo del mismo color."""
        alto = y1 - y0
        ancho = x1 - x0
        # la base
        d.rounded_rectangle([x0 + ancho * 0.04, y0 + alto * 0.34,
                             x1 - ancho * 0.04, y1 - alto * 0.06],
                            radius=alto * 0.42, fill=color)
        # los bollos de arriba
        for fx, fy, fr in [(0.10, 0.44, 0.20), (0.24, 0.30, 0.24), (0.40, 0.38, 0.21),
                           (0.52, 0.24, 0.25), (0.66, 0.34, 0.22), (0.79, 0.28, 0.23),
                           (0.91, 0.46, 0.19)]:
            cx = x0 + ancho * fx
            cy = y0 + alto * fy
            r = alto * fr
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        # y dos bollos pequenos a los lados, para que no parezca un rectangulo
        for fx, fy, fr in [(0.02, 0.62, 0.13), (0.98, 0.64, 0.12)]:
            cx = x0 + ancho * fx
            cy = y0 + alto * fy
            r = alto * fr
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    def estrella(cx, cy, r, color=AMARILLO):''',
    "la funcion de la nube")

# la banda se convierte en nube
rep("    # --- la banda del coral, con la fecha en blanco\n    d.rectangle([0, 530, W, 1470], fill=CORAL)",
    "    # --- la nube verde con la fecha en blanco\n    nube(120, 470, W - 120, 1520, VERDE_MALATO)",
    "la nube en vez de la banda")

# la caja de abajo, en verde y con letra blanca
rep('''    d.rectangle([(W - ancho) / 2, caja_y, (W + ancho) / 2, caja_y + alto_caja],
                fill=AMARILLO, outline=NEGRO, width=14)
    centro(caja_y + 40, T["gancho1"], 104)
    if T["gancho2"]:
        centro(caja_y + 165, T["gancho2"], 104)''',
'''    nube((W - ancho) / 2 - 40, caja_y - 40, (W + ancho) / 2 + 40, caja_y + alto_caja + 20,
         VERDE_MALATO)
    centro(caja_y + 40, T["gancho1"], 104, COMIC, BLANCO)
    if T["gancho2"]:
        centro(caja_y + 165, T["gancho2"], 104, COMIC, BLANCO)''',
    "la caja de abajo, en verde y blanca")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
