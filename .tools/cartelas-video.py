"""Las cartelas, en verde MUY pastel y con el árbol en su verde.

Antes el árbol blanco se borraba: el código lo trataba como si fuera negro.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
VERDE = (30, 154, 69)          # el del logotipo
PASTEL = (232, 246, 236)        # muy clarito, para que el verde del logo destaque
PASTEL_2 = (214, 238, 221)
TINTA = (22, 74, 44)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"

RAIZ = r"C:\Users\Usuario\Desktop\APP Malato\Video aniversario\cartelas"
os.makedirs(RAIZ, exist_ok=True)


def fondo():
    """Verde pastel, con un degradado muy suave y un halo."""
    img = Image.new("RGB", (W, H), PASTEL)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(PASTEL[0] + (PASTEL_2[0] - PASTEL[0]) * t)
        g = int(PASTEL[1] + (PASTEL_2[1] - PASTEL[1]) * t)
        b = int(PASTEL[2] + (PASTEL_2[2] - PASTEL[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse([W / 2 - 480, H * 0.32 - 480, W / 2 + 480, H * 0.32 + 480], fill=70)
    halo = halo.filter(ImageFilter.GaussianBlur(170))
    img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), halo)
    return img


def pega(img, ruta, ancho, y):
    """Pega el logo TAL CUAL: mantiene sus colores y su transparencia."""
    logo = Image.open(ruta).convert("RGBA")
    alto = int(ancho * logo.size[1] / logo.size[0])
    logo = logo.resize((ancho, alto), Image.LANCZOS)
    img.paste(logo, ((W - ancho) // 2, y), logo)
    return alto


def frase(img, texto, y, tam, color=TINTA, ruta=ROUND, ancho_max=880):
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(ruta, tam)
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    alto_linea = int(tam * 1.4)
    y0 = y - (len(lineas) - 1) * alto_linea // 2
    for i, ln in enumerate(lineas):
        w = d.textlength(ln, font=ft)
        d.text(((W - w) / 2, y0 + i * alto_linea), ln, font=ft, fill=color)
    return y0 + len(lineas) * alto_linea


MARCA = r"C:\Users\Usuario\Desktop\APP Malato\docs\marca"
ARBOL = os.path.join(MARCA, "logo-o-verde.png")
COMPLETO = r".tmp-logo\marca-color.png"

# ---------------------------------------------------------------- 1 · el árbol y el lema, partido
img = fondo()
alto = pega(img, ARBOL, 560, int(H * 0.15))
y = int(H * 0.15) + alto + 150
frase(img, "2006. urtetik", y, 84, VERDE)
frase(img, "ZUREKIN", y + 150, 118, VERDE, ROUND)
img.save(os.path.join(RAIZ, "1-arbol.png"))

# ---------------------------------------------------------------- 2 · el árbol y el lema
img = fondo()
alto = pega(img, ARBOL, 320, int(H * 0.24))
frase(img, "2006. urtetik zurekin", int(H * 0.24) + alto + 240, 78, VERDE)
img.save(os.path.join(RAIZ, "2-2006.png"))

# ---------------------------------------------------------------- 3 · el cierre
img = fondo()
alto = pega(img, COMPLETO, 740, int(H * 0.20))
frase(img, "Eskerrik asko 20 urte hauetan gurekin egoteagatik",
      int(H * 0.20) + alto + 240, 60, VERDE, COMIC, 820)
img.save(os.path.join(RAIZ, "3-cierre.png"))

print("  hechas las tres cartelas")
for n in ("1-arbol.png", "2-2006.png", "3-cierre.png"):
    r = os.path.join(RAIZ, n)
    print(f"   {n} · {round(os.path.getsize(r)/1024,0)} KB")
