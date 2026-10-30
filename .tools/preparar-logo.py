"""Prepara el logotipo en negro puro, para imprimir.

Del .doc sale la hoja entera; aquí se recorta la marca y se deja en blanco y negro.
"""
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

os.makedirs(".tmp-logo", exist_ok=True)

# --- la marca completa (supermercado malato)
hoja = Image.open(".tmp-logo/LogotipoCompleto.png").convert("L")
print(f"  hoja: {hoja.size}")

# se recorta la parte de arriba, donde está la marca
ancho, alto = hoja.size
marca = hoja.crop((0, 0, ancho, int(alto * 0.27)))

# se busca el recuadro con tinta, para no dejar aire
desde = marca.point(lambda p: 0 if p > 245 else 255)
caja = desde.getbbox()
print(f"  marca: {marca.size} · recuadro: {caja}")
if caja:
    x0, y0, x1, y1 = caja
    margen = 12
    marca = marca.crop((max(0, x0 - margen), max(0, y0 - margen),
                        min(ancho, x1 + margen), min(alto, y1 + margen)))
print(f"  recortada: {marca.size}")

# a negro puro sobre blanco
marca = marca.point(lambda p: 0 if p < 150 else 255)
marca.save(".tmp-logo/marca-negro.png")
print("  .tmp-logo/marca-negro.png")

# --- la «o» suelta, que sirve de adorno
o = Image.open("docs/marca/logo-o-tinta.png").convert("L")
fondo = Image.new("L", o.size, 255)
fondo.paste(o, (0, 0), o.point(lambda p: 255 - p) if o.mode == "L" else None)
fondo = fondo.point(lambda p: 0 if p < 150 else 255)
fondo.save(".tmp-logo/o-negro.png")
print("  .tmp-logo/o-negro.png")

# un jpeg de cada una, que es lo que el PDF sabe meter
marca.convert("RGB").save(".tmp-logo/marca.jpg", "JPEG", quality=95)
fondo.convert("RGB").save(".tmp-logo/o.jpg", "JPEG", quality=95)
print(f"  marca.jpg {round(os.path.getsize('.tmp-logo/marca.jpg')/1024,1)} KB")
print(f"  o.jpg {round(os.path.getsize('.tmp-logo/o.jpg')/1024,1)} KB")
