"""La foto «1», la primera después del comienzo; el resto, barajado de nuevo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cuadros-video.py"
t = open(p, encoding="utf-8").read()

VIEJO = """import random
fotos = sorted([f for f in os.listdir(RAIZ)
                if f.lower().endswith((".jpeg", ".jpg")) and "todas" not in f.lower()])
random.seed(7)
random.shuffle(fotos)"""

NUEVO = """import random
fotos = sorted([f for f in os.listdir(RAIZ)
                if f.lower().endswith((".jpeg", ".jpg")) and "todas" not in f.lower()])
# la que se llama «1» va la primera, justo después del comienzo
primera = [f for f in fotos if os.path.splitext(f)[0].strip() == "1"]
resto = [f for f in fotos if f not in primera]
random.seed(11)
random.shuffle(resto)
fotos = (primera[:1] if primera else []) + resto
print("  primera foto: " + (primera[0] if primera else "(no hay ninguna que se llame 1)"))"""

if VIEJO not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(VIEJO, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  la «1» primera, y otro barajado")
