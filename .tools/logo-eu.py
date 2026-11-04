"""El logotipo con «supermerkatua», para los carteles en euskera.

La palabra está dentro de la imagen del logotipo, así que se tapa la franja
con blanco (el fondo del logotipo) y se escribe la vasca encima.
"""
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

im = Image.open(".tmp-logo/marca.jpg").convert("RGB")
W, H = im.size
print("  logotipo:", (W, H))

d = ImageDraw.Draw(im)

# la franja de «supermercado», tapada con el blanco del fondo
d.rectangle([0, 0, W, int(H * 0.40)], fill=(255, 255, 255))

# y la palabra en euskera, en su sitio
tam = 62
f = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", tam)
texto = "supermerkatua"
ancho = d.textlength(texto, font=f)
d.text(((W - ancho) / 2, int(H * 0.10)), texto, font=f, fill=(97, 99, 96))

im.save(".tmp-logo/marca-eu.jpg", "JPEG", quality=95)
print("  escrito .tmp-logo/marca-eu.jpg")
im.resize((W // 2, H // 2), Image.LANCZOS).save(".tmp-logo/marca-eu-vista.png")
print("  vista previa hecha")
