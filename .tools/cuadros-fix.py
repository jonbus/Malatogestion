"""La foto «Todas» (y las que no son verticales) sobre ellas mismas desenfocadas.

Así no salen bandas y no se ve el «formato» del vídeo.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cuadros-video.py"
t = open(p, encoding="utf-8").read()

VIEJO = """    # si no, entera sobre el verde
    base = fondo_verde()"""

NUEVO = """    # si no, entera sobre ella misma desenfocada: sin bandas y sin perder nada
    base = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(45))"""

if VIEJO not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(VIEJO, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  la foto entera, sobre ella misma desenfocada")
