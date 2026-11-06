"""La primera cartela: el árbol más grande, y el lema partido en dos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cartelas-video.py"
t = open(p, encoding="utf-8").read()

VIEJO = '''# ---------------------------------------------------------------- 1 · solo el árbol
img = fondo()
pega(img, ARBOL, 380, int(H * 0.36))
img.save(os.path.join(RAIZ, "1-arbol.png"))'''

NUEVO = '''# ---------------------------------------------------------------- 1 · el árbol y el lema, partido
img = fondo()
alto = pega(img, ARBOL, 560, int(H * 0.15))
y = int(H * 0.15) + alto + 150
frase(img, "2006. urtetik", y, 84, VERDE)
frase(img, "ZUREKIN", y + 150, 118, VERDE, ROUND)
img.save(os.path.join(RAIZ, "1-arbol.png"))'''

if VIEJO not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(VIEJO, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  la primera cartela, cambiada")
