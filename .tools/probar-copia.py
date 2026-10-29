"""Hace la copia de seguridad del proyecto: un .zip con todo lo que hace falta
   para rehacerlo, y una comprobación de que dentro está lo que debe estar.

   Uso:  python .tools\copia-seguridad.py
"""
import datetime
import hashlib
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FECHA = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
SALIDA = os.path.join(BASE, f"COPIA-APP-MALATO-{FECHA}.zip")

# ---------------------------------------------------------------- qué entra
INCLUIR_DIRS = [
    "docs", "tools", "tests", "apps", "packages", "db",
]
INCLUIR_DIRS_TAMBIEN = [
    os.path.join(".tools", "docs"),      # el convenio
]
INCLUIR_FICHEROS_BASE = [
    "package.json", "package-lock.json", "pnpm-workspace.yaml",
    "tsconfig.json", "README.md",
]
# los generadores: solo los scripts, no las herramientas
EXT_TOOLS = {".py", ".ps1", ".mjs", ".js", ".json", ".md"}

# ---------------------------------------------------------------- qué NO entra
EXCLUIR = {
    ".tools/cli", ".tools/webprobe", ".tools/pdfprobe", ".tools/nestprobe",
    ".tools/pglite", ".tools/pgprobe", ".tools/node_modules", ".tools/pipcache",
    ".npm-cache", ".npmcache", "node_modules", ".git", ".netlify",
    "docs/nube/node_modules",
}


def relativo(ruta):
    return os.path.relpath(ruta, BASE).replace("\\", "/")


def excluido(rel):
    for e in EXCLUIR:
        if rel == e or rel.startswith(e + "/"):
            return True
    return False


def recoger():
    """Devuelve la lista de ficheros que van en la copia."""
    ficheros = []

    for d in INCLUIR_DIRS + INCLUIR_DIRS_TAMBIEN:
        raiz = os.path.join(BASE, d)
        if not os.path.isdir(raiz):
            print(f"  AVISO: no existe {d}")
            continue
        for base, dirs, nombres in os.walk(raiz):
            dirs[:] = [x for x in dirs if not excluido(relativo(os.path.join(base, x)))]
            for n in nombres:
                ruta = os.path.join(base, n)
                if not excluido(relativo(ruta)):
                    ficheros.append(ruta)

    for f in INCLUIR_FICHEROS_BASE:
        ruta = os.path.join(BASE, f)
        if os.path.isfile(ruta):
            ficheros.append(ruta)

    # los generadores sueltos de .tools
    for n in os.listdir(os.path.join(BASE, ".tools")):
        ruta = os.path.join(BASE, ".tools", n)
        if os.path.isfile(ruta) and os.path.splitext(n)[1].lower() in EXT_TOOLS:
            ficheros.append(ruta)

    return sorted(set(ficheros))


ficheros = recoger()
print(f"  ficheros a guardar: {len(ficheros)}")

# ---------------------------------------------------------------- zip
huellas = {}
with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for ruta in ficheros:
        arc = relativo(ruta)
        z.write(ruta, arc)
        with open(ruta, "rb") as f:
            huellas[arc] = hashlib.sha256(f.read()).hexdigest()[:16]
    # una lista de lo que va dentro, con su huella
    listado = "\r\n".join(f"{h}  {n}" for n, h in sorted(huellas.items()))
    z.writestr("LISTA-DE-FICHEROS.txt",
               f"Copia de seguridad · APP Malato\r\n"
               f"Fecha: {datetime.datetime.now():%Y-%m-%d %H:%M}\r\n"
               f"Ficheros: {len(huellas)}\r\n\r\n"
               f"huella (sha256, 16 primeros)   fichero\r\n"
               f"{'-'*60}\r\n{listado}\r\n")

tam = os.path.getsize(SALIDA)
print(f"  escrito: {os.path.basename(SALIDA)}  ({tam/1024/1024:.2f} MB)")

# ---------------------------------------------------------------- comprobar
print("\n  === comprobando la copia ===")
fallos = 0


def hay(cond, texto):
    global fallos
    print(f"   {'OK  ' if cond else 'FALLO'}  {texto}")
    if not cond:
        fallos += 1


with zipfile.ZipFile(SALIDA) as z:
    nombres = set(z.namelist())
    malo = z.testzip()
    hay(malo is None, "el zip está íntegro")

    imprescindibles = [
        "docs/MANUAL.md",
        "docs/DECISIONES.md",
        "docs/RESTAURAR.md",
        "docs/NUBE.md",
        "docs/RRHH-TURNOS.md",
        "docs/TAREAS.md",
        "docs/PEDIDOS.md",
        "docs/datos/fruta-verdura.json",
        "docs/marca/logo-o-blanco.png",
        "docs/momentos/tienda.html",
        "docs/momentos/coordinacion.html",
        "docs/momentos/7-gerencia.md",
        "docs/momentos/ofertas.md",
        "docs/momentos/6-cierre-tienda.md",
        "docs/nube/public/index.html",
        "docs/nube/netlify/functions/nucleo.js",
        "docs/nube/netlify/functions/api.mjs",
        "docs/nube/prueba-nucleo.mjs",
        "docs/nube/prueba-en-vivo.mjs",
        ".tools/generar-tienda.py",
        ".tools/generar-coordinacion.py",
        ".tools/generar-nube.py",
        ".tools/desplegar-tienda.py",
        ".tools/extraer-logo.py",
        "tools/check-boundaries.mjs",
        "tsconfig.json",
        "package.json",
        "LISTA-DE-FICHEROS.txt",
    ]
    faltan = [x for x in imprescindibles if x not in nombres]
    hay(not faltan, f"están los {len(imprescindibles)} ficheros imprescindibles"
        + (f"  FALTAN: {faltan}" if faltan else ""))

    hay(not any("node_modules/" in n for n in nombres), "no se cuela ningún node_modules")
    hay(not any(n.startswith(".npm") for n in nombres), "no se cuela la caché de npm")
    hay(not any(n.startswith(".tools/cli/") for n in nombres), "no se cuela el CLI de 214 MB")

    hay(any(n.startswith("docs/archivo/") for n in nombres), "va el archivo histórico")
    hay(any(n.startswith(".tools/docs/") for n in nombres), "van los PDF del convenio")

    descomprimido = sum(i.file_size for i in z.infolist())
    hay(descomprimido > 1_000_000, f"descomprimido ocupa {descomprimido/1024/1024:.1f} MB")

print(f"\n  {'COPIA CORRECTA' if fallos == 0 else 'HAY ' + str(fallos) + ' FALLOS'}")
print(f"  {SALIDA}")
sys.exit(0 if fallos == 0 else 1)
