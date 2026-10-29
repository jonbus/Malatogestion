"""Muestra cómo quedarían las frases, sin escribir nada."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

REGlas_txt = open(".tools/renombrar-puesto.py", encoding="utf-8").read()
trozo = REGlas_txt.split("REGLAS = [")[1].split("]\n\n\ndef tocar")[0]
REGLAS = eval("[" + trozo + "]")

RUTAS = [
    "docs/DECISIONES.md", "docs/TAREAS.md", "docs/RRHH-TURNOS.md",
    "docs/momentos/6-cierre-tienda.md", "docs/momentos/7-gerencia.md",
    "docs/NUBE.md", "docs/MANUAL.md", "docs/momentos/ofertas.md",
]

muestras = []
for ruta in RUTAS:
    if not os.path.exists(ruta):
        continue
    for linea in open(ruta, encoding="utf-8"):
        if "tienda" not in linea.lower() or len(linea.strip()) <= 40:
            continue
        nueva = linea
        for v, n in REGLAS:
            nueva = nueva.replace(v, n)
        if nueva != linea:
            muestras.append((linea.strip(), nueva.strip()))

print(f"  frases que cambian: {len(muestras)}\n")
vistos = set()
mostradas = 0
for a, b in muestras:
    clave = a[:55]
    if clave in vistos:
        continue
    vistos.add(clave)
    print(f"  ANTES:   {a[:150]}")
    print(f"  DESPUÉS: {b[:150]}\n")
    mostradas += 1
    if mostradas >= 10:
        break

# buscar resultados sospechosos en TODOS los ficheros
print("  === resultados que hay que mirar con lupa ===")
SOSPECHOSOS = [
    "la tienda revisa", "tienda de la tienda", "de tienda de la tienda",
    "las tiendas", "personas de tienda de tienda", "tienda de tienda",
    "a tienda de", "para tienda de",
]
import re
for raiz, dirs, fics in os.walk("."):
    dirs[:] = [d for d in dirs if d not in
               ("archivo", "node_modules", ".git", ".npm-cache", "cli",
                "webprobe", "pdfprobe", "nestprobe", "pglite", "pgprobe")]
    for f in fics:
        if not f.lower().endswith((".md", ".html", ".py", ".mjs", ".js", ".json")):
            continue
        ruta = os.path.join(raiz, f)
        if "renombrar-puesto" in ruta:
            continue
        try:
            t = open(ruta, encoding="utf-8").read()
        except Exception:
            continue
        for v, n in REGLAS:
            t = t.replace(v, n)
        for s in SOSPECHOSOS:
            for m in re.finditer(re.escape(s), t):
                ctx = t[max(0, m.start() - 50):m.end() + 50].replace("\n", " ")
                print(f"    {os.path.relpath(ruta)}: …{ctx}…")
