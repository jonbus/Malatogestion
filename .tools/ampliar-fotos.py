"""Amplía y realza las fotos para mejorar el OCR."""
import sys

from PIL import Image, ImageEnhance, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

for n in (1, 2):
    src = f".tools/fv{n}.jpeg"
    im = Image.open(src)
    print(f"  fv{n}: {im.size[0]} x {im.size[1]}  modo={im.mode}")
    # escala de grises, más contraste, y 3x
    g = ImageOps.grayscale(im)
    g = ImageEnhance.Contrast(g).enhance(1.8)
    g = ImageEnhance.Sharpness(g).enhance(2.0)
    grande = g.resize((g.width * 3, g.height * 3), Image.LANCZOS)
    out = f".tools/fv{n}_big.png"
    grande.save(out)
    print(f"     -> {out}  ({grande.size[0]} x {grande.size[1]})")
