"""La invitación como CARTA: el texto entero, en una imagen.

Papel crema, el árbol arriba y la firma abajo. Para adjuntar como si fuera
una carta.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
PAPEL = (252, 250, 243)
PAPEL_2 = (244, 240, 228)
TINTA = (48, 44, 38)
VERDE = (30, 154, 69)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
MARCA = r"C:\Users\Usuario\Desktop\APP Malato\docs\marca"

img = Image.new("RGB", (W, H), PAPEL)
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(
        int(PAPEL[0] + (PAPEL_2[0] - PAPEL[0]) * t),
        int(PAPEL[1] + (PAPEL_2[1] - PAPEL[1]) * t),
        int(PAPEL[2] + (PAPEL_2[2] - PAPEL[2]) * t),
    ))

# un halo suave detrás de todo
halo = Image.new("L", (W, H), 0)
ImageDraw.Draw(halo).ellipse([W / 2 - 520, H * 0.35 - 520, W / 2 + 520, H * 0.35 + 520], fill=60)
img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(190)))

d = ImageDraw.Draw(img)

# --- el árbol
arbol = Image.open(os.path.join(MARCA, "logo-o-verde.png")).convert("RGBA")
al = 150
arbol = arbol.resize((al, int(al * arbol.size[1] / arbol.size[0])), Image.LANCZOS)
img.paste(arbol, ((W - al) // 2, 110), arbol)


def linea(y, texto, tam, color=TINTA, ruta=ROUND):
    ft = ImageFont.truetype(ruta, tam)
    w = d.textlength(texto, font=ft)
    d.text(((W - w) / 2, y), texto, font=ft, fill=color)
    return y + int(tam * 1.42)


y = 330
y = linea(y, "20 años.", 86, VERDE) + 40
y = linea(y, "No nos lo creemos ni nosotros.", 52) + 60
y = linea(y, "Este domingo 8 de noviembre,", 52) + 8
y = linea(y, "de 10:00 a 14:30,", 52) + 8
y = linea(y, "te esperamos en Malato.", 52) + 60
y = linea(y, "Habrá tarta, palmeritas, batukada", 52) + 8
y = linea(y, "y una papeleta por cada compra.", 52) + 60
y = linea(y, "Pero lo que de verdad queremos", 56, TINTA, COMIC) + 8
y = linea(y, "es verte ahí.", 56, TINTA, COMIC) + 70
y = linea(y, "Gracias por estos 20 años.", 50) + 10
y = linea(y, "El equipo de Malato", 50) + 10

# --- una raya corta al final, como una firma
d.line([(W / 2 - 90, y + 40), (W / 2 + 90, y + 40)], fill=VERDE, width=4)
d.text((26, H - 40), "Malato · 2006. urtetik zurekin", font=ImageFont.truetype(ROUND, 26), fill=(180, 175, 160))

img.save("CARTA-INVITACION.jpg", "JPEG", quality=94, optimize=True)
print(f"  CARTA-INVITACION.jpg · {round(os.path.getsize('CARTA-INVITACION.jpg')/1024,0)} KB")
img.resize((W // 3, H // 3), Image.LANCZOS).save(".tmp-cart/CARTA-vista.png")
print("  vista previa")
