"""La invitación como imagen: 1080x1920, lista para el estado o para mandar."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
VERDE = (30, 154, 69)
PASTEL = (238, 249, 241)
PASTEL_2 = (219, 240, 226)
TINTA = (22, 74, 44)
GRIS = (90, 120, 100)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
MARCA = r"C:\Users\Usuario\Desktop\APP Malato\docs\marca"

img = Image.new("RGB", (W, H), PASTEL)
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(
        int(PASTEL[0] + (PASTEL_2[0] - PASTEL[0]) * t),
        int(PASTEL[1] + (PASTEL_2[1] - PASTEL[1]) * t),
        int(PASTEL[2] + (PASTEL_2[2] - PASTEL[2]) * t),
    ))

halo = Image.new("L", (W, H), 0)
ImageDraw.Draw(halo).ellipse([W / 2 - 500, H * 0.30 - 500, W / 2 + 500, H * 0.30 + 500], fill=70)
img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(170)))

d = ImageDraw.Draw(img)


def centro(y, texto, tam, color=TINTA, ruta=ROUND):
    ft = ImageFont.truetype(ruta, tam)
    w = d.textlength(texto, font=ft)
    d.text(((W - w) / 2, y), texto, font=ft, fill=color)
    return y + int(tam * 1.25)


# --- el árbol arriba
arbol = Image.open(os.path.join(MARCA, "logo-o-verde.png")).convert("RGBA")
al = 190
arbol = arbol.resize((al, int(al * arbol.size[1] / arbol.size[0])), Image.LANCZOS)
img.paste(arbol, ((W - al) // 2, 130), arbol)

y = 400
y = centro(y, "20 URTE", 120, VERDE) + 10
y = centro(y, "20 AÑOS", 96, VERDE) + 70

d.line([(W / 2 - 110, y), (W / 2 + 110, y)], fill=VERDE, width=5)
y += 80

y = centro(y, "Este domingo", 100, TINTA, COMIC) + 10
y = centro(y, "te esperamos", 100, TINTA, COMIC) + 90

y = centro(y, "8 de noviembre — 10:00 a 14:30", 62, GRIS) + 60

y = centro(y, "tarta, palmeritas y batukada", 58, TINTA) + 16
y = centro(y, "una papeleta por cada compra", 58, TINTA) + 110

y = centro(y, "Malato  —  2006. urtetik zurekin", 46, VERDE) + 10

img.save("INVITACION-20-ANIVERSARIO.jpg", "JPEG", quality=94, optimize=True)
img.save("INVITACION-20-ANIVERSARIO.png", "PNG")
for f in ("INVITACION-20-ANIVERSARIO.jpg", "INVITACION-20-ANIVERSARIO.png"):
    print(f"  {f} · {round(os.path.getsize(f)/1024,0)} KB")
img.resize((W // 3, H // 3), Image.LANCZOS).save(".tmp-cart/INVITACION-vista.png")
print("  vista previa")
