"""Empareja CI y nombre a partir del OCR con coordenadas."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


def leer(ruta):
    filas = []
    for linea in open(ruta, encoding="utf-8"):
        m = re.match(r"^(\d+)\|(\d+)\|(\d+)\|(.+)$", linea.strip())
        if not m:
            continue
        filas.append({"y": int(m.group(1)), "x": int(m.group(2)),
                      "h": int(m.group(3)), "t": m.group(4).strip()})
    return filas


def agrupar(filas):
    """Agrupa por Y (misma fila) y ordena por X."""
    filas = sorted(filas, key=lambda f: (f["y"], f["x"]))
    filas.sort(key=lambda f: f["y"] + f["h"] / 2)
    grupos = []
    for f in filas:
        centro = f["y"] + f["h"] / 2
        if grupos and abs(centro - grupos[-1]["c"]) < max(12, f["h"] * 0.6):
            grupos[-1]["it"].append(f)
        else:
            grupos.append({"c": centro, "it": [f]})
    return [sorted(g["it"], key=lambda f: f["x"]) for g in grupos]


for n in (1, 2):
    filas = leer(f".tools/ocr{n}c.txt")
    print(f"=== FOTO {n} · {len(filas)} lineas ===")
    for g in agrupar(filas):
        trozos = " | ".join(f"{f['t']}" for f in g)
        print(f"   {trozos}")
    print()
