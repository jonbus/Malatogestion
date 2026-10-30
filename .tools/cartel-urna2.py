"""El cartel de la urna, dibujado a mano: una persona metiendo la mano.

300 ppp, A4. Letra divertida y dibujo de verdad, todo en blanco y negro.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

W, H = 2480, 3508            # A4 a 300 ppp
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

img = Image.new("RGB", (W, H), BLANCO)
d = ImageDraw.Draw(img)

COMIC = "C:\Windows\Fonts\comicbd.ttf"
ROUND = "C:\Windows\Fonts\ARLRDBD.TTF"


def fuente(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def centro(y, texto, tam, ruta=COMIC, color=NEGRO):
    f = fuente(ruta, tam)
    caja = d.textbbox((0, 0), texto, font=f)
    d.text(((W - (caja[2] - caja[0])) / 2 - caja[0], y), texto, font=f, fill=color)
    return caja[3] - caja[1]


def centro_en(x0, ancho, y, texto, tam, ruta=COMIC, color=NEGRO):
    f = fuente(ruta, tam)
    caja = d.textbbox((0, 0), texto, font=f)
    d.text((x0 + (ancho - (caja[2] - caja[0])) / 2 - caja[0], y), texto, font=f, fill=color)


# ---------------------------------------------------------------- el logotipo
logo = Image.open(".tmp-logo/marca-negro.png").convert("L")
ancho_logo = 900
alto_logo = int(ancho_logo * logo.size[1] / logo.size[0])
logo = logo.resize((ancho_logo, alto_logo), Image.LANCZOS)
img.paste(logo, ((W - ancho_logo) // 2, 110))

centro(110 + alto_logo + 45, "2006. urtetik ZUREKIN", 104, COMIC)

# ---------------------------------------------------------------- el titulo
centro(640, "CAMBIA TU TICKET", 168)
centro(815, "POR UNA PAPELETA", 168)

# ---------------------------------------------------------------- el dibujo
G = 11                       # grosor de las lineas


def estrella(cx, cy, r, rellena=True, grosor=G):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.44
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=NEGRO if rellena else BLANCO)
    if not rellena:
        d.line(pts + [pts[0]], fill=NEGRO, width=grosor)


# --- la urna
UX, UTOP, UBOT = 1390, 2020, 2900
UW_TOP, UW_BOT = 730, 800
cuerpo = [
    (UX - UW_TOP // 2, UTOP), (UX + UW_TOP // 2, UTOP),
    (UX + UW_BOT // 2, UBOT - 150), (UX + UW_BOT // 2 - 90, UBOT),
    (UX - UW_BOT // 2 + 90, UBOT), (UX - UW_BOT // 2, UBOT - 150),
]
d.polygon(cuerpo, fill=BLANCO, outline=NEGRO)
d.line(cuerpo + [cuerpo[0]], fill=NEGRO, width=G, joint="curve")

# boca de la urna
d.rounded_rectangle([UX - UW_TOP // 2 - 34, UTOP - 46, UX + UW_TOP // 2 + 34, UTOP + 46],
                    radius=34, fill=BLANCO, outline=NEGRO, width=G)

# los papelitos que asoman
for (px, py, ang, w, h) in [(-210, -150, -22, 120, 190), (-90, -190, 9, 118, 200),
                            (40, -175, -14, 118, 185), (170, -140, 26, 115, 175),
                            (250, -95, -34, 112, 160)]:
    papel = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    dp = ImageDraw.Draw(papel)
    dp.rectangle([20, 20, 20 + w, 20 + h], fill=BLANCO, outline=NEGRO, width=G)
    dp.line([20 + w * 0.22, 20 + h * 0.3, 20 + w * 0.78, 20 + h * 0.3], fill=NEGRO, width=6)
    dp.line([20 + w * 0.22, 20 + h * 0.55, 20 + w * 0.78, 20 + h * 0.55], fill=NEGRO, width=6)
    papel = papel.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.paste(papel, (UX + px - papel.size[0] // 2, UTOP + py - papel.size[1] // 2), papel)

# --- la persona, a la izquierda, inclinada hacia la urna
HX, HY, HR = 800, 1640, 232

# cuerpo
d.rounded_rectangle([HX - 200, HY + 230, HX + 200, HY + 850], radius=100,
                    fill=BLANCO, outline=NEGRO, width=G)
# cuello
d.rectangle([HX - 40, HY + 150, HX + 40, HY + 240], fill=BLANCO, outline=BLANCO)
# cabeza
d.ellipse([HX - HR, HY - HR, HX + HR, HY + HR], fill=BLANCO, outline=NEGRO, width=G)

# pelo
for k in range(5):
    a0 = 200 + k * 28
    d.arc([HX - HR - 6, HY - HR - 6, HX + HR + 6, HY + HR + 6], a0, a0 + 26, fill=NEGRO, width=G)
d.arc([HX - HR, HY - HR, HX + HR, HY + HR], 185, 355, fill=NEGRO, width=G + 4)

# ojos contentos (dos arcos)
d.arc([HX - 110, HY - 80, HX - 30, HY], 200, 340, fill=NEGRO, width=G + 2)
d.arc([HX + 30, HY - 80, HX + 110, HY], 200, 340, fill=NEGRO, width=G + 2)

# sonrisa grande
d.arc([HX - 95, HY - 10, HX + 95, HY + 120], 15, 165, fill=NEGRO, width=G + 2)
# mofletes
d.ellipse([HX - 150, HY + 20, HX - 105, HY + 65], outline=NEGRO, width=6)
d.ellipse([HX + 105, HY + 20, HX + 150, HY + 65], outline=NEGRO, width=6)

# --- el brazo que entra en la urna
hombro = (HX + 150, HY + 300)
codo = (HX + 430, HY + 210)
mano = (UX - 120, UTOP + 210)
d.line([hombro, codo, mano], fill=NEGRO, width=G + 30, joint="curve")
d.line([hombro, codo, mano], fill=BLANCO, width=G + 8, joint="curve")
d.ellipse([mano[0] - 62, mano[1] - 50, mano[0] + 62, mano[1] + 50],
          fill=BLANCO, outline=NEGRO, width=G)

# el otro brazo, colgando
d.line([HX - 150, HY + 330, HX - 265, HY + 640], fill=NEGRO, width=G + 30, joint="curve")
d.line([HX - 150, HY + 330, HX - 265, HY + 640], fill=BLANCO, width=G + 8, joint="curve")

# piernas
for dx in (-90, 90):
    d.rectangle([HX + dx - 62, HY + 830, HX + dx + 62, HY + 1075], fill=BLANCO,
                outline=NEGRO, width=G)

# --- adornos
estrella(1180, 1160, 62)
estrella(1600, 1120, 44)
estrella(430, 1240, 40)
estrella(2000, 1500, 52)
estrella(1830, 1000, 34)
estrella(2150, 1180, 30, rellena=False)
estrella(330, 1680, 28, rellena=False)

for (cx, cy, r) in [(600, 1080, 14), (2050, 1750, 16), (250, 1450, 12), (1900, 880, 12)]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NEGRO)

# ---------------------------------------------------------------- el texto de abajo
centro(3000, "Mete la mano en la urna.", 94)
centro(3115, "Si sale premio, te lo llevas.", 94)

f = fuente(COMIC, 78)
caja = d.textbbox((0, 0), "Una compra, una papeleta.", font=f)
d.text(((W - (caja[2] - caja[0])) / 2 - caja[0], 3228), "Una compra, una papeleta.",
       font=f, fill=(70, 70, 70))

# la «o» ya esta en el logotipo de arriba: no hace falta repetirla

centro(3382, "Gracias por estos 20 años a tu lado.", 64, ROUND)

img.save("CARTEL-URNA.pdf", "PDF", resolution=300.0)
print(f"  CARTEL-URNA.pdf · {round(__import__('os').path.getsize('CARTEL-URNA.pdf')/1024,1)} KB")
img.resize((W // 3, H // 3), Image.LANCZOS).save(".tmp-cart/URNA-vista.png")
print("  vista previa hecha")
