"""La «1» y después la «2», y el resto barajado."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\cuadros-video.py"
t = open(p, encoding="utf-8").read()

VIEJO = """# la que se llama «1» va la primera, justo después del comienzo
primera = [f for f in fotos if os.path.splitext(f)[0].strip() == "1"]
resto = [f for f in fotos if f not in primera]
random.seed(11)
random.shuffle(resto)
fotos = (primera[:1] if primera else []) + resto
print("  primera foto: " + (primera[0] if primera else "(no hay ninguna que se llame 1)"))"""

NUEVO = """# primero la «1», después la «2», y luego el resto barajado
primero = []
for nombre in ("1", "2"):
    for f in fotos:
        if os.path.splitext(f)[0].strip() == nombre and f not in primero:
            primero.append(f)
resto = [f for f in fotos if f not in primero]
random.seed(11)
random.shuffle(resto)
fotos = primero + resto
print("  primeras: " + (", ".join(primero) if primero else "(no hay ninguna que se llame 1 ni 2)"))"""

if VIEJO not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(VIEJO, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  la «1» y después la «2»")
