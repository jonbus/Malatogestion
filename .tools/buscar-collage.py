"""Encuentra la foto que sale en el segundo 56 comparando la imagen, y la quita.

No sirve mirar el tamaño: el collage ya vendrá así de WhatsApp. Lo que sí
sirve es comparar la huella visual del cuadro con la de cada foto.
"""
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = r"C:\Users\Usuario\Desktop\APP Malato\Video aniversario"


def huella(ruta):
    im = Image.open(ruta).convert("L").resize((16, 16), Image.LANCZOS)
    px = list(im.getdata())
    med = sum(px) / len(px)
    return [1 if v > med else 0 for v in px]


def distancia(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


objetivo = os.path.join(RAIZ, "cuadros", "f033.png")
if not os.path.exists(objetivo):
    print("  no existe el cuadro 33")
    sys.exit(1)

h_obj = huella(objetivo)
candidatas = []
for f in os.listdir(RAIZ):
    if f.lower().endswith((".jpeg", ".jpg")):
        d = distancia(h_obj, huella(os.path.join(RAIZ, f)))
        candidatas.append((d, f))

candidatas.sort()
print("  las 5 más parecidas al cuadro del segundo 56:")
for d, f in candidatas[:5]:
    print(f"   {d:3d}  {f}")

d, nombre = candidatas[0]
if d <= 12:
    print(f"\n  ES ESTA: {nombre}  (diferencia {d})")
    # se apunta en la lista negra
    lista = os.path.join(RAIZ, "no-incluir.txt")
    with open(lista, "a", encoding="utf-8") as fh:
        fh.write(nombre + "\n")
    print(f"  apuntada en {os.path.basename(lista)}")
else:
    print(f"\n  no está claro (la mejor diferencia es {d}); no se toca nada")
