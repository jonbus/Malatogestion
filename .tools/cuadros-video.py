"""Prepara todos los fotogramas del vídeo, en orden, numerados.

Entrada (dos cartelas) · las fotos · «Todas» · el cierre.
Todos a 1080x1920, y las que no son verticales van sobre el verde, sin recortar.
"""
import os
import shutil
import sys

from PIL import Image, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
VERDE = (30, 154, 69)
VERDE_OSCURO = (16, 92, 42)

RAIZ = r"C:\Users\Usuario\Desktop\APP Malato\Video aniversario"
CARTELAS = os.path.join(RAIZ, "cartelas")
SALIDA = os.path.join(RAIZ, "cuadros")

if os.path.exists(SALIDA):
    shutil.rmtree(SALIDA)
os.makedirs(SALIDA)


def fondo_verde():
    img = Image.new("RGB", (W, H), VERDE)
    d = ImageDraw = None
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(VERDE_OSCURO[0] + (VERDE[0] - VERDE_OSCURO[0]) * (1 - t))
        g = int(VERDE_OSCURO[1] + (VERDE[1] - VERDE_OSCURO[1]) * (1 - t))
        b = int(VERDE_OSCURO[2] + (VERDE[2] - VERDE_OSCURO[2]) * (1 - t))
        d.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def encaja_entera(ruta):
    """La foto ENTERA, sin recortar: se ve más pequeña, en el centro, sobre el verde."""
    im = Image.open(ruta).convert("RGB")
    base = fondo_verde()
    escala = min(W / im.size[0], (H - 240) / im.size[1])
    n = (int(im.size[0] * escala), int(im.size[1] * escala))
    im = im.resize(n, Image.LANCZOS)
    base.paste(im, ((W - n[0]) // 2, (H - n[1]) // 2))
    return base


def encaja(ruta):
    """La foto, llenando 1080x1920. Si no es vertical, sobre el verde y sin recortar."""
    im = Image.open(ruta).convert("RGB")
    # solo se recorta si la foto ya es casi 9:16; si no, se ve ENTERA sobre el verde
    if abs(im.size[0] / im.size[1] - W / H) > 0.10:
        base = fondo_verde()
        escala = min(W / im.size[0], (H - 200) / im.size[1])
        n = (int(im.size[0] * escala), int(im.size[1] * escala))
        im = im.resize(n, Image.LANCZOS)
        base.paste(im, ((W - n[0]) // 2, (H - n[1]) // 2))
        return base
    escala = max(W / im.size[0], H / im.size[1])
    n = (int(im.size[0] * escala), int(im.size[1] * escala))
    im = im.resize(n, Image.LANCZOS)
    x = (n[0] - W) // 2
    y = (n[1] - H) // 2
    return im.crop((x, y, x + W, y + H))
    # si no, entera sobre ella misma desenfocada: sin bandas y sin perder nada
    base = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(45))
    escala = min(W / im.size[0], (H - 200) / im.size[1])
    n = (int(im.size[0] * escala), int(im.size[1] * escala))
    im = im.resize(n, Image.LANCZOS)
    base.paste(im, ((W - n[0]) // 2, (H - n[1]) // 2))
    return base


cuadros = []

# --- la del aniversario, lo PRIMERO de todo, antes de la cartela
_m20 = [f for f in os.listdir(RAIZ)
        if os.path.splitext(f)[0].strip().lower() == "malato20aniversario"
        and f.lower().endswith((".jpeg", ".jpg", ".png"))]
if _m20:
    _cuadro = encaja_entera(os.path.join(RAIZ, _m20[0]))
    cuadros.append(_cuadro)
    cuadros.append(_cuadro)   # dos cuadros: casi 3 segundos
    print("  la del aniversario va la primera, y dura el doble: " + _m20[0])

# --- entrada: dos cartelas, cada una un par de cuadros
for n in ("1-arbol.png",):
    for _ in range(1):
        cuadros.append(Image.open(os.path.join(CARTELAS, n)).convert("RGB"))

# --- las fotos
import random
fotos = sorted([f for f in os.listdir(RAIZ)
                if f.lower().endswith((".jpeg", ".jpg")) and "todas" not in f.lower()
                and "malato20" not in f.lower()])
# primero la «1», después la «2», y luego el resto barajado
primero = []
for nombre in ("1", "2"):
    for f in fotos:
        if os.path.splitext(f)[0].strip() == nombre and f not in primero:
            primero.append(f)
resto = [f for f in fotos if f not in primero]
# el orden se guarda la primera vez y YA NO CAMBIA
_orden_path = os.path.join(RAIZ, "orden.txt")
if os.path.exists(_orden_path):
    _guardado = [l.strip() for l in open(_orden_path, encoding="utf-8") if l.strip()]
    _restantes = [f for f in fotos if f not in _guardado]
    fotos = [f for f in _guardado if f in fotos] + _restantes
    print(f"  orden congelado: {len(_guardado)} guardadas, {len(_restantes)} nuevas")
random.shuffle(resto)
# sin repetidas: se comparan las IMÁGENES, no los ficheros
def _huella(ruta):
    im = Image.open(ruta).convert("L").resize((8, 8), Image.LANCZOS)
    px = list(im.getdata())
    med = sum(px) / len(px)
    return [1 if v > med else 0 for v in px]

def _parecidas(a, b):
    return sum(1 for x, y in zip(a, b) if x != y) <= 10

_huellas, _unicas = [], []
for f in primero + resto:
    _h = _huella(os.path.join(RAIZ, f))
    if any(_parecidas(_h, o) for o in _huellas):
        print("  OJO, parecida a otra (se queda): " + f)
    _huellas.append(_h)
    _unicas.append(f)
fotos = _unicas
# se guarda el orden para que no cambie nunca más
open(os.path.join(RAIZ, "orden.txt"), "w", encoding="utf-8").write(
    "\n".join(fotos))

# fuera la foto que cae en el segundo 29
_total = 2 + 1 + len(fotos) + 1 + 3     # aniversario(2) + arbol(1) + fotos + Todas + cierre
_dur = 124.36 / _total
_no_usar = []
_lista = os.path.join(RAIZ, "no-usar.txt")
if os.path.exists(_lista):
    _no_usar = [l.strip() for l in open(_lista, encoding="utf-8") if l.strip()]
    _antes = len(fotos)
    fotos = [f for f in fotos if f not in _no_usar]
    print(f"  fuera por nombre: {_antes - len(fotos)}")

# la foto «23», clavada en el segundo 23
_f23 = [f for f in fotos if os.path.splitext(f)[0].strip() == "23"]
if _f23:
    fotos.remove(_f23[0])
    # 2 cartelas del principio + 3 del cierre + «Todas» + las fotos
    _total = 2 + 3 + 1 + len(fotos) + 1
    _dur = 124.36 / _total
    _idx = max(0, min(len(fotos), int(round(23 / _dur)) - 2))
    fotos.insert(_idx, _f23[0])   # UNA sola vez
    # la de antes de la «23» es casi igual: se manda lejos, al final
    if _idx > 0:
        _casi = fotos.pop(_idx - 1)
        fotos.append(_casi)
        print(f"  la de antes de la «23» se mueve al final: {_casi}")
    print(f"  la «23» va en el puesto {_idx + 1} de las fotos (sobre el segundo {round((_idx + 2) * _dur, 1)})")
else:
    print("  no hay ninguna foto que se llame 23")
print("  primeras: " + (", ".join(primero) if primero else "(no hay ninguna que se llame 1 ni 2)"))
print(f"  fotos: {len(fotos)}")
for f in fotos:
    # la «2» se ve entera, como la de grupo: no se recorta
    if os.path.splitext(f)[0].strip() == "2":
        cuadros.append(encaja_entera(os.path.join(RAIZ, f)))
    else:
        cuadros.append(encaja(os.path.join(RAIZ, f)))

# --- «Todas», al final de las fotos
todas = r"C:\Users\Usuario\Desktop\APP Malato Documentación\FotosAniversario\Todas.jpeg"
if os.path.exists(todas):
    _todas_cuadro = encaja_entera(todas)
    cuadros.append(_todas_cuadro)
    cuadros.append(_todas_cuadro)    # dos cuadros: dura el doble
    print("  «Todas» incluida, como última foto, y dura el doble")

# --- el cierre
for _ in range(3):
    cuadros.append(Image.open(os.path.join(CARTELAS, "3-cierre.png")).convert("RGB"))

# --- se guardan numerados
for i, im in enumerate(cuadros, start=1):
    im.save(os.path.join(SALIDA, f"f{i:03d}.png"), "PNG", optimize=False)

print(f"  cuadros: {len(cuadros)}  ·  cada uno {round(124.36/len(cuadros),3)} s")
print(f"  en: {SALIDA}")
