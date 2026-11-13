"""Recoge en una carpeta todo lo del aniversario que está suelto en el escritorio,
y aparta los duplicados exactos.

No borra nada: lo que sobra va a una subcarpeta «duplicados».
"""
import hashlib
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

ESCRITORIO = r"C:\Users\Usuario\Desktop"
DESTINO = os.path.join(ESCRITORIO, "Aniversario 20")
DUPLICADOS = os.path.join(DESTINO, "duplicados")

# lo que es del aniversario: por el nombre
PISTAS = [
    "kartel urteurrena", "kartel sariak", "kartel urna", "kartel piruleta",
    "invitacion", "invitación", "carta-invitacion", "gutuna-gonbita",
    "instagram-invitacion", "20-aniversario", "planning-8-noviembre",
    "papeletas-aniversario", "carta-aiaraldea", "manual-del-dia-20",
    "aniversario-procedimiento",
]
CARPETAS = ["invitación", "invitacion", "video aniversario"]

os.makedirs(DESTINO, exist_ok=True)

movidos, saltados = [], []

for nombre in sorted(os.listdir(ESCRITORIO)):
    ruta = os.path.join(ESCRITORIO, nombre)
    bajo = nombre.lower().strip()

    # la propia carpeta de destino y las de sistema, ni tocarlas
    if ruta == DESTINO:
        continue

    es_carpeta = os.path.isdir(ruta)
    if es_carpeta:
        if bajo in CARPETAS:
            # se mete su contenido dentro, sin sobrescribir
            for f in os.listdir(ruta):
                o = os.path.join(ruta, f)
                d = os.path.join(DESTINO, f)
                if os.path.isfile(o) and not os.path.exists(d):
                    shutil.move(o, d)
                    movidos.append(f)
            # la carpeta, ya vacía, se quita
            try:
                if not os.listdir(ruta):
                    os.rmdir(ruta)
            except Exception:
                pass
        continue

    if not any(p in bajo for p in PISTAS):
        continue
    destino = os.path.join(DESTINO, nombre)
    if os.path.exists(destino):
        saltados.append(nombre)
        continue
    shutil.move(ruta, destino)
    movidos.append(nombre)

print(f"  movidos a «Aniversario 20»: {len(movidos)}")
for m in movidos:
    print("   " + m)
if saltados:
    print(f"\n  ya había uno igual, no se toca: {len(saltados)}")
    for s in saltados:
        print("   " + s)

# --- duplicados exactos dentro de la carpeta
os.makedirs(DUPLICADOS, exist_ok=True)
vistos, reps = {}, []
for f in sorted(os.listdir(DESTINO)):
    ruta = os.path.join(DESTINO, f)
    if not os.path.isfile(ruta):
        continue
    h = hashlib.md5(open(ruta, "rb").read()).hexdigest()
    if h in vistos:
        reps.append((f, vistos[h]))
        shutil.move(ruta, os.path.join(DUPLICADOS, f))
    else:
        vistos[h] = f

print(f"\n  duplicados apartados: {len(reps)}")
for f, orig in reps:
    print(f"   {f}   (igual que {orig})")

total = [f for f in os.listdir(DESTINO) if os.path.isfile(os.path.join(DESTINO, f))]
print(f"\n  en la carpeta: {len(total)} ficheros")
