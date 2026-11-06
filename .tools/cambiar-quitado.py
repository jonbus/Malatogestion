"""Cambios pedidos:
  · fuera mis capturas (mira-*, vista-*)
  · las fotos se quitan por NOMBRE (no-usar.txt), no por segundo
  · las casi iguales se AVISAN, no se borran solas
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = r"C:\Users\Usuario\Desktop\APP Malato\Video aniversario"

# --- 1 · fuera mis capturas
quitadas = 0
for f in os.listdir(RAIZ):
    if f.lower().endswith((".jpg", ".jpeg")) and f.startswith(("mira-", "vista-")):
        os.remove(os.path.join(RAIZ, f))
        quitadas += 1
print(f"  capturas mías borradas: {quitadas}")

# --- 2 · el programa: quitar por nombre, avisar de las parecidas
p = r".tools\cuadros-video.py"
t = open(p, encoding="utf-8").read()

INICIO = "# fuera la foto que cae en el segundo 29"
FIN = "else:\n    print(\"  no se pudo calcular la del segundo 29\")"

i = t.find(INICIO)
j = t.find(FIN)
if i < 0 or j < 0:
    print("  NO ENCONTRADO el bloque de los segundos")
    sys.exit(1)

NUEVO = '''# fuera las que estén apuntadas en no-usar.txt, POR NOMBRE
_no_usar = []
_lista = os.path.join(RAIZ, "no-usar.txt")
if os.path.exists(_lista):
    _no_usar = [l.strip() for l in open(_lista, encoding="utf-8") if l.strip()]
    antes = len(fotos)
    fotos = [f for f in fotos if f not in _no_usar]
    print(f"  fuera por nombre: {antes - len(fotos)}")

'''

t = t[:i] + NUEVO + t[j + len(FIN):]

# las casi iguales: se avisan, no se quitan
t = t.replace(
    '''    if any(_parecidas(_h, o) for o in _huellas):
        print("  parecida a otra, fuera: " + f)''',
    '''    if any(_parecidas(_h, o) for o in _huellas):
        print("  OJO, parecida a otra (pero se queda): " + f)''',
    1,
)
t = t.replace(
    '''    else:
        _huellas.append(_h)
        _unicas.append(f)''',
    '''    _huellas.append(_h)
    _unicas.append(f)''',
    1,
)

open(p, "w", encoding="utf-8").write(t)
print("  ok  se quita por nombre, y las parecidas se avisan")

# --- 3 · la lista de nombres, vacía al principio
ruta_lista = os.path.join(RAIZ, "no-usar.txt")
if not os.path.exists(ruta_lista):
    with open(ruta_lista, "w", encoding="utf-8") as fh:
        fh.write("# Una foto por línea (nombre exacto del fichero).\n")
        fh.write("# Las que estén aquí no salen en el vídeo.\n")
    print("  creada no-usar.txt (vacía, para que apuntes las que no quieras)")
