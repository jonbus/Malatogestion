"""Busca restos de «operaria» fuera del archivo histórico."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

SALTAR = {"node_modules", ".git", ".npm-cache", ".npmcache", "cli", "webprobe",
          "pdfprobe", "nestprobe", "pglite", "pgprobe", "appdata",
          "_prueba-restauracion"}
YO = ("renombrar-puesto", "ver-renombrado", "buscar-restos")

EXT = (".md", ".html", ".py", ".mjs", ".js", ".json", ".ts", ".txt")

total = 0
for raiz, dirs, fics in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SALTAR]
    for f in fics:
        if not f.lower().endswith(EXT):
            continue
        if any(x in f for x in YO):
            continue
        ruta = os.path.join(raiz, f)
        try:
            t = open(ruta, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        bajo = t.lower()
        n = bajo.count("operari")
        if n:
            total += n
            print(f"  {n:>3}  {os.path.relpath(ruta)}")
            for i, linea in enumerate(t.splitlines(), 1):
                if "operari" in linea.lower():
                    print(f"        L{i}: {linea.strip()[:100]}")
                    break

print(f"\n  TOTAL de restos fuera del archivo: {total}")
print("  (el archivo histórico SÍ conserva el nombre antiguo, a propósito)")
