"""Analiza el logotipo para localizar los glifos por columnas."""
import sys

import numpy as np
from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

im = Image.open(".tools/logo.jpeg").convert("L")
a = np.array(im)
print(f"  tamaño: {a.shape[1]} x {a.shape[0]}")
print(f"  min={a.min()}  max={a.max()}  media={a.mean():.1f}")

# tinta = oscuro sobre fondo claro (o al revés si el fondo es oscuro)
fondo_oscuro = a.mean() < 128
print(f"  ¿fondo oscuro? {fondo_oscuro}")

tinta = (a > 128) if fondo_oscuro else (a < 128)
print(f"  píxeles de tinta: {tinta.sum()}  ({100*tinta.sum()/tinta.size:.1f} %)")

# caja del contenido
ys, xs = np.where(tinta)
if len(xs) == 0:
    print("  no hay tinta")
    sys.exit(0)
print(f"  caja del contenido: x {xs.min()}..{xs.max()}   y {ys.min()}..{ys.max()}")

# perfil por columnas
col = tinta.sum(axis=0)
print("\n  perfil por columnas (bloques de tinta separados por huecos):")
bloques = []
dentro = False
ini = 0
HUECO = 3
for x in range(len(col)):
    if col[x] > 0 and not dentro:
        dentro = True; ini = x
    elif col[x] == 0 and dentro:
        dentro = False
        bloques.append((ini, x - 1))
if dentro:
    bloques.append((ini, len(col) - 1))

# unir bloques separados por menos de HUECO
unidos = []
for b in bloques:
    if unidos and b[0] - unidos[-1][1] <= HUECO:
        unidos[-1] = (unidos[-1][0], b[1])
    else:
        unidos.append(list(b))
for i, (x0, x1) in enumerate(unidos):
    alto = np.where(tinta[:, x0:x1 + 1].any(axis=1))[0]
    y0, y1 = (alto.min(), alto.max()) if len(alto) else (0, 0)
    ancho = x1 - x0 + 1
    print(f"    glifo {i}: x {x0:>3}..{x1:>3}  (ancho {ancho:>3})   "
          f"y {y0:>3}..{y1:>3}  (alto {y1-y0+1:>3})")

# perfil por filas, para ver si hay dos líneas
fil = tinta.sum(axis=1)
print("\n  filas con tinta (bloques):")
dentro = False; ini = 0; filas = []
for y in range(len(fil)):
    if fil[y] > 0 and not dentro:
        dentro = True; ini = y
    elif fil[y] == 0 and dentro:
        dentro = False; filas.append((ini, y - 1))
if dentro:
    filas.append((ini, len(fil) - 1))
for i, (y0, y1) in enumerate(filas):
    print(f"    banda {i}: y {y0}..{y1}  (alto {y1-y0+1})")
