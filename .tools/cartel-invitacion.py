"""El cartel de la tienda: invita al domingo 8.

Se imprime en papel fosforito amarillo: aquí va TODO en negro y el blanco
se queda sin tinta, así que el amarillo del papel hace de fondo.
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


def estrella(cx, cy, r, rellena=True):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.44
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=NEGRO if rellena else BLANCO)
    if not rellena:
        d.line(pts + [pts[0]], fill=NEGRO, width=G)


def globo(cx, cy, r):
    d.ellipse([cx - r, cy - r * 1.18, cx + r, cy + r * 1.18], fill=BLANCO, outline=NEGRO, width=G)
    d.polygon([(cx - r * 0.16, cy + r * 1.12), (cx + r * 0.16, cy + r * 1.12), (cx, cy + r * 1.32)],
              fill=NEGRO)
    # el hilo, ondulado
    pts = [(cx, cy + r * 1.32)]
    for k in range(1, 7):
        pts.append((cx + (18 if k % 2 else -18), cy + r * 1.32 + k * r * 0.32))
    d.line(pts, fill=NEGRO, width=6, joint="curve")


def tarta(cx, cy, w, h):
    # dos pisos
    d.rounded_rectangle([cx - w / 2, cy, cx + w / 2, cy + h * 0.55], radius=40,
                        fill=BLANCO, outline=NEGRO, width=G)
    d.rounded_rectangle([cx - w * 0.34, cy - h * 0.42, cx + w * 0.34, cy + h * 0.06], radius=36,
                        fill=BLANCO, outline=NEGRO, width=G)
    # las velas
    for k in (-1, 0, 1):
        x = cx + k * w * 0.18
        d.line([x, cy - h * 0.42, x, cy - h * 0.60], fill=NEGRO, width=10)
        d.ellipse([x - 16, cy - h * 0.68, x + 16, cy - h * 0.56], fill=NEGRO)


def tambor(cx, cy, w, h):
    d.ellipse([cx - w / 2, cy, cx + w / 2, cy + h * 0.22], fill=BLANCO, outline=NEGRO, width=G)
    d.rectangle([cx - w / 2, cy + h * 0.11, cx + w / 2, cy + h * 0.72], fill=BLANCO,
                outline=NEGRO, width=G)
    d.ellipse([cx - w / 2, cy + h * 0.61, cx + w / 2, cy + h * 0.83], fill=BLANCO,
              outline=NEGRO, width=G)
    for k in range(1, 4):
        y = cy + h * (0.11 + k * 0.15)
        d.line([cx - w / 2, y, cx + w / 2, y - h * 0.04], fill=NEGRO, width=6)
    # las baquetas
    d.line([cx + w * 0.42, cy + h * 0.10, cx + w * 0.86, cy - h * 0.16], fill=NEGRO, width=9)
    d.line([cx + w * 0.30, cy + h * 0.14, cx + w * 0.66, cy - h * 0.26], fill=NEGRO, width=9)


def ticket(cx, cy, w, h, ang):
    t = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    dt = ImageDraw.Draw(t)
    dt.rectangle([30, 30, 30 + w, 30 + h], fill=BLANCO, outline=NEGRO, width=G)
    dt.line([30 + w * 0.12, 30 + h * 0.35, 30 + w * 0.88, 30 + h * 0.35], fill=NEGRO, width=7)
    dt.line([30 + w * 0.12, 30 + h * 0.62, 30 + w * 0.7, 30 + h * 0.62], fill=NEGRO, width=7)
    t = t.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.paste(t, (cx - t.size[0] // 2, cy - t.size[1] // 2), t)


# ---------------------------------------------------------------- arriba
logo = Image.open(".tmp-logo/marca-negro.png").convert("L")
al = 760
la = int(al * logo.size[1] / logo.size[0])
logo = logo.resize((al, la), Image.LANCZOS)
img.paste(logo, ((W - al) // 2, 110))
centro(110 + la + 26, "2006. urtetik ZUREKIN", 74)

# ---------------------------------------------------------------- la fecha
centro(542, "DOMINGO", 142, ROUND)
centro(700, "8", 392, ROUND)
centro(1105, "DE NOVIEMBRE", 126, ROUND)
centro(1252, "20 ANIVERSARIO", 96)
centro(1372, "por la mañana", 92)

# ---------------------------------------------------------------- los dibujos
star_x = [(330, 1330), (2160, 1330), (250, 1600), (2240, 1610)]
for (sx, sy) in [(215, 1100), (2265, 1100), (300, 1290), (2180, 1290)]:
    estrella(sx, sy, 58)

globo(430, 1600, 120)
globo(700, 1520, 96)
globo(300, 1830, 88)
globo(2050, 1620, 110)
globo(2280, 1800, 92)
globo(1830, 1520, 84)

tarta(760, 1980, 640, 520)
tambor(1830, 2080, 420, 520)
ticket(1330, 1760, 230, 150, -12)
ticket(1450, 1960, 210, 138, 14)

for (cx, cy, r) in [(1330, 2330, 22), (1180, 2500, 16), (1500, 2520, 18), (980, 1600, 14), (1700, 2450, 14)]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NEGRO)

# ---------------------------------------------------------------- el texto
centro(2680, "TARTA · SORTEO · BATUKADA", 92)
centro(2790, "PALMERITAS Y MÚSICA", 92)

d.line([180, 2930, W - 180, 2930], fill=NEGRO, width=14)
centro(2975, "¡NO TE LO PUEDES", 122)
centro(3110, "PERDER!", 122)
d.line([180, 3270, W - 180, 3270], fill=NEGRO, width=14)

centro(3310, "Te esperamos. Ven a celebrarlo con nosotros.", 66, ROUND)

img.save("CARTEL-INVITACION.pdf", "PDF", resolution=300.0)
print(f"  CARTEL-INVITACION.pdf · {round(__import__('os').path.getsize('CARTEL-INVITACION.pdf')/1024,1)} KB")
img.resize((W // 3, H // 3), Image.LANCZOS).save(".tmp-cart/INVITACION-vista.png")
print("  vista previa hecha")
