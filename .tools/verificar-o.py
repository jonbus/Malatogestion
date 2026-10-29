"""Comprueba cuántos glifos hay de verdad y si el último es un anillo con tronco."""
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
im = Image.open(".tools/logo.jpeg").convert("L")
a = np.array(im)
tinta = a < 128
col = tinta.sum(axis=0)

# --- todos los tramos de tinta, sin unir nada
tramos = []
dentro = False
ini = 0
for x in range(len(col)):
    if col[x] > 0 and not dentro:
        dentro = True; ini = x
    elif col[x] == 0 and dentro:
        dentro = False; tramos.append((ini, x - 1))
if dentro:
    tramos.append((ini, len(col) - 1))
print(f"  tramos de tinta sin unir: {len(tramos)}")
print("  " + ", ".join(f"{a_}-{b_}" for a_, b_ in tramos))

# --- el bloque de la «o»: ¿anillo arriba y tronco abajo?
x0, x1 = 699, 848
sub = tinta[:, x0:x1 + 1]
print(f"\n  bloque x {x0}..{x1}: perfil por filas")
for y in range(sub.shape[0]):
    fila = sub[y]
    if not fila.any():
        continue
    # tramos de esta fila
    tr = []
    d2 = False; i2 = 0
    for i in range(len(fila)):
        if fila[i] and not d2:
            d2 = True; i2 = i
        elif not fila[i] and d2:
            d2 = False; tr.append((i2, i - 1))
    if d2:
        tr.append((i2, len(fila) - 1))
    # solo imprimir cada 8 filas para no llenar
    if y % 8 == 0 or y > sub.shape[0] - 12:
        huecos = len(tr) - 1
        print(f"    y={y:>3}  tramos={len(tr):>2}  huecos={huecos}  "
              f"ancho={sum(b_-a_+1 for a_,b_ in tr):>3}")

print("\n  --- resumen ---")
filas_con_hueco = 0
filas_solidas = 0
for y in range(sub.shape[0]):
    fila = sub[y]
    if not fila.any():
        continue
    tr = 0; d2 = False
    for i in range(len(fila)):
        if fila[i] and not d2:
            d2 = True; tr += 1
        elif not fila[i] and d2:
            d2 = False
    if tr >= 2:
        filas_con_hueco += 1
    else:
        filas_solidas += 1
print(f"    filas con hueco (anillo): {filas_con_hueco}")
print(f"    filas macizas:            {filas_solidas}")
