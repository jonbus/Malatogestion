"""Cambia el puesto «operaria» por «Tienda» en todo el proyecto.

No es un reemplazo ciego: «la operaria» y «de la operaria» no se pueden sustituir
por «la tienda» y «de la tienda», porque entonces se confunde la persona con el
local. Se usan las mismas formas que ya usamos con Gerencia y Coordinación.

Uso:  python .tools\renombrar-puesto.py [--aplicar]
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APLICAR = "--aplicar" in sys.argv
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Qué NO se toca: lo histórico se queda como estaba.
SALTAR = {"archivo", "node_modules", ".git", ".npm-cache", ".npmcache",
          "cli", "webprobe", "pdfprobe", "nestprobe", "pglite", "pgprobe",
          "pipcache", "_prueba-restauracion", "appdata"}
# este mismo fichero no se toca (contiene las reglas)
YO = os.path.basename(os.path.abspath(__file__))

EXT = (".md", ".html", ".py", ".mjs", ".js", ".json", ".ts", ".txt")

# ---------------------------------------------------------------- reglas
# El orden importa: de lo más específico a lo más general.
REGLAS = [
    # --- nombres de fichero, de hoja y de módulo
    ("Operaria mañana", "Tienda mañana"),
    ("Operaria tarde", "Tienda tarde"),
    ("generar-operaria.py", "generar-tienda.py"),
    ("comprobar-operaria.py", "comprobar-tienda.py"),
    ("3-operaria-manana.md", "3-tienda-manana.md"),
    ("6-cierre-operaria.md", "6-cierre-tienda.md"),
    ("manana-operaria.html", "manana-tienda.html"),
    ("operaria.html", "tienda.html"),
    ("generar-operaria", "generar-tienda"),

    # --- plural
    ("**Operarias**", "**Tienda**"),
    ("las Operarias", "las personas de tienda"),
    ("Las Operarias", "Las personas de tienda"),
    ("Operarias", "Tienda"),
    ("Operarios", "Tienda"),
    ("+ 1 operaria", "+ 1 persona de tienda"),
    ("1 operaria", "1 persona de tienda"),
    ("las dos operarias", "las dos personas de tienda"),
    ("Las dos operarias", "Las dos personas de tienda"),
    ("una de las operarias", "una de las personas de tienda"),
    ("de las operarias", "de las personas de tienda"),
    ("a las operarias", "a las personas de tienda"),
    ("las operarias", "las personas de tienda"),
    ("Las operarias", "Las personas de tienda"),
    ("los operarios", "las personas de tienda"),
    ("entre operarias", "entre las personas de tienda"),
    ("3 operarias", "3 personas en tienda"),
    ("2 operarias", "2 personas en tienda"),
    ("operarias", "personas de tienda"),

    # --- «de la operaria» y compañía: la persona pasa a ser «de tienda»
    ("de la operaria", "de tienda"),
    ("De la operaria", "De tienda"),
    ("para la operaria", "para tienda"),
    ("a la operaria", "a tienda"),
    ("por la operaria", "por tienda"),
    ("la operaria de", "la persona de tienda de"),
    ("operaria de mañana", "persona de tienda de la mañana"),
    ("operaria de la mañana", "persona de tienda de la mañana"),

    # --- singular con artículo, cuando es una persona
    ("la operaria", "la persona de tienda"),
    ("La operaria", "La persona de tienda"),
    ("una operaria", "una persona de tienda"),
    ("Una operaria", "Una persona de tienda"),

    # --- lo que queda suelto
    ("operaria", "tienda"),
    ("Operaria", "Tienda"),
    ("OPERARIA", "TIENDA"),
]


def tocar(ruta):
    try:
        t = open(ruta, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return None, 0
    antes = t
    n = 0
    for viejo, nuevo in REGLAS:
        c = t.count(viejo)
        if c:
            t = t.replace(viejo, nuevo)
            n += c
    if t != antes:
        return t, n
    return None, 0


cambiados = []
for raiz, dirs, fics in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in SALTAR]
    for f in fics:
        if not f.lower().endswith(EXT):
            continue
        if f == YO:
            continue
        ruta = os.path.join(raiz, f)
        nuevo, n = tocar(ruta)
        if nuevo is not None:
            cambiados.append((n, os.path.relpath(ruta, BASE), nuevo))

print(f"  ficheros a cambiar: {len(cambiados)}")
print(f"  sustituciones:      {sum(n for n, _, _ in cambiados)}")
print()
for n, r, _ in sorted(cambiados, reverse=True)[:15]:
    print(f"    {n:>4}  {r}")

if not APLICAR:
    print("\n  (simulación: no se ha escrito nada. Añade --aplicar)")
    sys.exit(0)

for n, r, nuevo in cambiados:
    open(os.path.join(BASE, r), "w", encoding="utf-8").write(nuevo)
print("\n  ESCRITO")
