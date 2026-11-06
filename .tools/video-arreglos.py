"""El vídeo: fuera la segunda cartela, fotos recortadas a 9:16 y barajadas.

Recortar a 9:16 quita las bandas desenfocadas —y el texto de la tienda que
se colaba en ellas—.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cuadros-video.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# --- 1 · fuera la segunda cartela
rep('''for n in ("1-arbol.png", "2-2006.png"):''',
    '''for n in ("1-arbol.png",):''',
    "fuera la segunda cartela")

# --- 2 · todo recortado a 9:16, sin bandas
rep('''    im = Image.open(ruta).convert("RGB")
    prop = im.size[0] / im.size[1]
    if abs(prop - W / H) < 0.06:
        # casi vertical: se recorta un poco, que queda mejor
        escala = max(W / im.size[0], H / im.size[1])
        n = (int(im.size[0] * escala), int(im.size[1] * escala))
        im = im.resize(n, Image.LANCZOS)
        x = (n[0] - W) // 2
        y = (n[1] - H) // 2
        return im.crop((x, y, x + W, y + H))''',
    '''    im = Image.open(ruta).convert("RGB")
    # SIEMPRE se recorta a 9:16: sin bandas y sin texto de la tienda
    escala = max(W / im.size[0], H / im.size[1])
    n = (int(im.size[0] * escala), int(im.size[1] * escala))
    im = im.resize(n, Image.LANCZOS)
    x = (n[0] - W) // 2
    y = (n[1] - H) // 2
    return im.crop((x, y, x + W, y + H))''',
    "todo recortado a 9:16")

# --- 3 · las fotos, barajadas
rep('''fotos = sorted([f for f in os.listdir(RAIZ)
                if f.lower().endswith((".jpeg", ".jpg")) and "todas" not in f.lower()])''',
    '''import random
fotos = sorted([f for f in os.listdir(RAIZ)
                if f.lower().endswith((".jpeg", ".jpg")) and "todas" not in f.lower()])
random.seed(2026)
random.shuffle(fotos)''',
    "las fotos, barajadas")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
