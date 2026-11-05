"""El cartel de la piruleta: la papeleta que no ha sido premiada se cambia.

Blanco y negro, para imprimir en la impresora de la tienda.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

W, H = 2480, 3508
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

img = Image.new("RGB", (W, H), BLANCO)
d = ImageDraw.Draw(img)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
G = 12


def f(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def centro(y, texto, tam, ruta=COMIC):
    ft = f(ruta, tam)
    c = d.textbbox((0, 0), texto, font=ft)
    d.text(((W - (c[2] - c[0])) / 2 - c[0], y), texto, font=ft, fill=NEGRO)
    return c[3] - c[1]


# --- el logotipo
logo = Image.open(".tmp-logo/marca-negro.png").convert("L")
al = 880
la = int(al * logo.size[1] / logo.size[0])
logo = logo.resize((al, la), Image.LANCZOS)
mascara = logo.convert("L").point(lambda p: 255 if p < 245 else 0)
img.paste(logo, ((W - al) // 2, 90), mascara)
centro(90 + la + 30, "2006. urtetik ZUREKIN", 64)

# --- la frase
centro(560, "HOY NO HA SIDO", 150, ROUND)
centro(730, "…pero te llevas una", 108)
centro(870, "PIRULETA", 250, ROUND)

# --- la piruleta
CX, CY, R = 1240, 1620, 300
# el palo
d.rounded_rectangle([CX - 26, CY + R - 20, CX + 26, CY + R + 380], radius=26,
                    fill=BLANCO, outline=NEGRO, width=G)
# el caramelo
d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=BLANCO, outline=NEGRO, width=G + 4)
# la espiral
pts = []
for k in range(220):
    t = k / 219.0
    ang = t * math.pi * 7
    rr = R * 0.84 * (1 - t * 0.92)
    pts.append((CX + rr * math.cos(ang), CY + rr * math.sin(ang)))
d.line(pts, fill=NEGRO, width=G, joint="curve")

# --- el resto
centro(2380, "Cambia tu papeleta en la caja", 96, ROUND)
centro(2520, "y te damos una piruleta.", 96, ROUND)

d.line([200, 2740, W - 200, 2740], fill=NEGRO, width=12)
centro(2810, "¡GRACIAS POR VENIR!", 120, ROUND)
d.line([200, 3000, W - 200, 3000], fill=NEGRO, width=12)

centro(3080, "Gracias por estos 20 años a tu lado.", 64, ROUND)

# --- margen y centrado, como los demás
caja = img.convert("L").point(lambda p: 0 if p > 250 else 255).getbbox()
contenido = img.crop(caja)
MARGEN = 177
cabe = H - 2 * MARGEN
esc = cabe / contenido.size[1]
nw = int(contenido.size[0] * esc)
contenido = contenido.resize((nw, cabe), Image.LANCZOS)
lienzo = Image.new("RGB", (W, H), BLANCO)
lienzo.paste(contenido, ((W - nw) // 2, MARGEN))

lienzo.save("Kartel Piruleta.pdf", "PDF", resolution=300.0)
lienzo.save("Kartel Piruleta.jpg", "JPEG", quality=93, optimize=True)
print(f"  Kartel Piruleta.pdf · {round(__import__('os').path.getsize('Kartel Piruleta.pdf')/1024,1)} KB")
print(f"  Kartel Piruleta.jpg · {round(__import__('os').path.getsize('Kartel Piruleta.jpg')/1024,1)} KB")
lienzo.resize((W // 3, H // 3), Image.LANCZOS).save(".tmp-cart/PIRULETA-vista.png")
print("  vista previa hecha")
