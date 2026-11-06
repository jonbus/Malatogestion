"""Dos cosas: mezclar más, y que «Todas» entre entera aunque sea más pequeña."""
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


# --- 1 · otra semilla: otra mezcla
rep("random.seed(2026)", "random.seed(7)", "otra mezcla")

# --- 2 · «Todas» entera, sobre el verde pastel
rep('''def encaja(ruta):''',
    '''def encaja_entera(ruta):
    """La foto ENTERA, sin recortar: se ve más pequeña, en el centro, sobre el verde."""
    im = Image.open(ruta).convert("RGB")
    base = fondo_verde()
    escala = min(W / im.size[0], (H - 240) / im.size[1])
    n = (int(im.size[0] * escala), int(im.size[1] * escala))
    im = im.resize(n, Image.LANCZOS)
    base.paste(im, ((W - n[0]) // 2, (H - n[1]) // 2))
    return base


def encaja(ruta):''',
    "la función de la foto entera")

rep('''    cuadros.append(encaja(todas))''',
    '''    cuadros.append(encaja_entera(todas))''',
    "«Todas», entera")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
