"""Los premios, de PDF a foto grande, como los demás carteles."""
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

im = Image.open(r".tmp-img\CARTEL-PREMIOS.png")
print("  tamaño del PNG:", im.size)

alto = 3508
ancho = round(im.size[0] * alto / im.size[1])
im = im.convert("RGB").resize((ancho, alto), Image.LANCZOS)
im.save("CARTEL-PREMIOS.jpg", "JPEG", quality=93, optimize=True)

print("  CARTEL-PREMIOS.jpg:", im.size)
print(f"  pesa {round(os.path.getsize('CARTEL-PREMIOS.jpg') / 1024, 1)} KB")
