"""Monta una muestra de cómo queda la «o»-árbol en la cabecera verde."""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

VERDE = (46, 194, 88)
VERDE_OSC = (30, 154, 69)
ANCHO, ALTO = 900, 260

# degradado igual que la cabecera
base = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
for x in range(ANCHO):
    t = x / (ANCHO - 1)
    for i in range(3):
        base[:, x, i] = int(VERDE[i] + (VERDE_OSC[i] - VERDE[i]) * t)
muestra = Image.fromarray(base, "RGB")

# la caja blanca del logo, como en la pantalla
CAJA = 96
caja = Image.new("RGBA", (CAJA, CAJA), (255, 255, 255, 255))
logo = Image.open("docs/marca/logo-o-verde.png").convert("RGBA")
escala = (CAJA - 14) / max(logo.size)
peq = logo.resize((int(logo.width * escala), int(logo.height * escala)), Image.LANCZOS)
caja.alpha_composite(peq, ((CAJA - peq.width) // 2, (CAJA - peq.height) // 2))
muestra.paste(caja, (26, (ALTO - CAJA) // 2), caja)

d = ImageDraw.Draw(muestra)


def fuente(tam):
    for ruta in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        try:
            return ImageFont.truetype(ruta, tam)
        except OSError:
            continue
    return ImageFont.load_default()


d.text((140, 78), "Coordinación", font=fuente(38), fill=(255, 255, 255))
d.text((142, 128), "Apertura · El día · Cierre", font=fuente(19), fill=(235, 255, 240))
d.text((26, 14), "ASÍ QUEDA EL LOGO EN LA CABECERA", font=fuente(15), fill=(210, 245, 220))

muestra.save("docs/marca/como-queda-en-la-cabecera.png")
print(f"  docs/marca/como-queda-en-la-cabecera.png "
      f"({muestra.size[0]}x{muestra.size[1]})")

# --- comprobar que el base64 incrustado en las pantallas es el mismo PNG
import base64
import re

original = open("docs/marca/logo-o-blanco.png", "rb").read()
for f in ("docs/momentos/tienda.html", "docs/momentos/coordinacion.html"):
    h = open(f, encoding="utf-8").read()
    m = re.search(r'src="data:image/png;base64,([^"]+)"', h)
    if not m:
        print(f"  {f}: NO encuentro el logo")
        continue
    datos = base64.b64decode(m.group(1))
    print(f"  {f}: {len(datos)} bytes, "
          f"{'IDENTICO al PNG' if datos == original else 'DISTINTO (revisar)'}")
