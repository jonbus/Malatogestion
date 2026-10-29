"""Mete la «o»-árbol en las dos pantallas, sustituyendo el hueco del logo."""
import base64
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

png = open("docs/marca/logo-o-blanco.png", "rb").read()
print(f"  PNG: {len(png)} bytes -> {len(base64.b64encode(png))} en base64")

LEYENDA = """import base64 as _b64
_LOGO = "data:image/png;base64," + _b64.b64encode(
    open("docs/marca/logo-o-blanco.png", "rb").read()).decode()
"""

for ruta in (".tools/generar-tienda.py", ".tools/generar-coordinacion.py"):
    src = open(ruta, encoding="utf-8").read()
    antes = src

    # 1. el hueco del logo -> la imagen
    src = src.replace(
        '<div class="logo">AQUÍ<br>EL LOGO</div>',
        '<div class="logo"><img src="__LOGO__" alt="Malato"></div>')

    # 2. el CSS del logo, para que la imagen encaje
    src = src.replace(
        "border:2px dashed var(--verde-claro); text-shadow:none}",
        "border:none; text-shadow:none; padding:2px}")
    src = src.replace(
        "font-weight:700; font-size:9px; text-align:center; padding:5px;",
        "text-align:center;")

    # 3. inyectar el logo al escribir el fichero
    src = src.replace('html = HTML.replace("__DATOS__"',
                      '_LOGO_URI = "data:image/png;base64," + __import__("base64").b64encode(\n'
                      '    open("docs/marca/logo-o-blanco.png", "rb").read()).decode()\n'
                      'html = HTML.replace("__LOGO__", _LOGO_URI).replace("__DATOS__"')

    # 4. el CSS de la imagen
    src = src.replace(
        "  header h1{margin:0; font-size:20px}",
        "  .logo img{max-width:100%; max-height:100%; object-fit:contain}\n"
        "  header h1{margin:0; font-size:20px}")

    if src == antes:
        print(f"  {ruta}: SIN CAMBIOS (revisar)")
    else:
        open(ruta, "w", encoding="utf-8").write(src)
        print(f"  {ruta}: parcheado")
