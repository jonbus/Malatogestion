"""Limpieza de duplicadas: compara el CONTENIDO de cada imagen, no el nombre.

No borra nada: mueve las repetidas a una carpeta «duplicadas», por si acaso.
"""
import hashlib
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = r"C:\Users\Usuario\Desktop\APP Malato\Video aniversario"
SALIDA = os.path.join(RAIZ, "duplicadas")

# estas no se tocan nunca, aunque parezcan repetidas
INTOCABLES = {"1", "2", "malato20aniversario", "todas"}

fotos = sorted([f for f in os.listdir(RAIZ)
                if f.lower().endswith((".jpeg", ".jpg")) and os.path.isfile(os.path.join(RAIZ, f))])
print(f"  fotos en la carpeta: {len(fotos)}")

por_hash = {}
for f in fotos:
    h = hashlib.md5(open(os.path.join(RAIZ, f), "rb").read()).hexdigest()
    por_hash.setdefault(h, []).append(f)

grupos = {h: fs for h, fs in por_hash.items() if len(fs) > 1}
print(f"  grupos de imágenes idénticas: {len(grupos)}")

if not grupos:
    print("\n  No hay ninguna repetida. La carpeta está limpia.")
    sys.exit(0)

os.makedirs(SALIDA, exist_ok=True)
movidas = 0
for h, fs in grupos.items():
    # se queda la de nombre intocable, si la hay; si no, la primera por orden
    fs_orden = sorted(fs, key=lambda x: (os.path.splitext(x)[0].strip().lower() not in INTOCABLES, x))
    se_queda = fs_orden[0]
    print(f"\n  GRUPO ({len(fs)}):")
    print(f"    se queda: {se_queda}")
    for f in fs_orden[1:]:
        nombre = os.path.splitext(f)[0].strip().lower()
        if nombre in INTOCABLES:
            print(f"    NO se toca (es la «{nombre}»): {f}")
            continue
        shutil.move(os.path.join(RAIZ, f), os.path.join(SALIDA, f))
        movidas += 1
        print(f"    movida a duplicadas: {f}")

print(f"\n  movidas: {movidas}")
print(f"  quedan en la carpeta: {len([f for f in os.listdir(RAIZ) if f.lower().endswith(('.jpeg', '.jpg'))])}")
