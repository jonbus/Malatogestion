"""Extrae la «o» (el árbol) del logotipo y saca una hoja de contacto de los glifos."""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
os.makedirs("docs/marca", exist_ok=True)

im = Image.open(".tools/logo.jpeg").convert("L")
a = np.array(im)
tinta = a < 128

# los 6 bloques detectados
GLIFOS = [
    ("1", 55, 241), ("2", 274, 382), ("3", 424, 446),
    ("4", 478, 586), ("5", 613, 694), ("6", 699, 848),
]

# ---------------------------------------------------- hoja de contacto
ESCALA = 1.0
hoja = Image.new("RGB", (899, 260 + 60), "white")
hoja.paste(Image.open(".tools/logo.jpeg").convert("RGB"), (0, 60))
d = ImageDraw.Draw(hoja)
d.text((6, 8), "LOGOTIPO ORIGINAL · los 6 bloques de tinta detectados", fill=(20, 20, 20))
for etiqueta, x0, x1 in GLIFOS:
    color = (200, 30, 30) if etiqueta == "6" else (30, 90, 200)
    d.rectangle([x0, 60, x1, 259], outline=color, width=2)
    d.text((x0 + 3, 44), etiqueta, fill=color)
hoja.save("docs/marca/00-logotipo-y-glifos.png")

# ---------------------------------------------------- la «o», la 6
x0, x1 = 699, 848
ys, xs = np.where(tinta[:, x0:x1 + 1])
y0, y1 = ys.min(), ys.max()
print(f"  la «o» (bloque 6): x {x0}..{x1}  y {y0}..{y1}  "
      f"({x1-x0+1} x {y1-y0+1})")

margen = 2
caja = (max(0, x0 - margen), max(0, y0 - margen),
        min(im.width, x1 + 1 + margen), min(im.height, y1 + 1 + margen))
recorte = Image.open(".tools/logo.jpeg").convert("L").crop(caja)
w, h = recorte.size

# alfa a partir de la luminancia: oscuro = opaco, blanco = transparente
lum = np.array(recorte).astype(np.float32)
alfa = np.clip((255.0 - lum) / 255.0 * 255.0 * 1.15, 0, 255).astype(np.uint8)

# el árbol de verdad: quitar el ruido de JPEG del fondo
alfa[alfa < 28] = 0


def pintar(color, ruta):
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = color
    rgba[..., 3] = alfa
    Image.fromarray(rgba, "RGBA").save(ruta)
    print(f"    {ruta}  ({w}x{h})")


# blanco, para la cabecera verde
pintar((255, 255, 255), "docs/marca/logo-o-blanco.png")
# verde oscuro de la marca, para fondos claros
pintar((30, 154, 69), "docs/marca/logo-o-verde.png")
# tinta oscura
pintar((19, 37, 26), "docs/marca/logo-o-tinta.png")

# también a 2x y a 4x, para que se vea nítido en pantallas densas
for factor in (2, 4):
    grande = Image.fromarray(
        np.dstack([np.full((h, w), c, dtype=np.uint8) for c in (255, 255, 255)]
                  + [alfa]), "RGBA").resize((w * factor, h * factor), Image.LANCZOS)
    grande.save(f"docs/marca/logo-o-blanco@{factor}x.png")
    print(f"    docs/marca/logo-o-blanco@{factor}x.png  ({w*factor}x{h*factor})")

print("\n  ficheros en docs/marca/:")
for n in sorted(os.listdir("docs/marca")):
    print(f"    {n}  ({os.path.getsize(os.path.join('docs/marca', n))} bytes)")
