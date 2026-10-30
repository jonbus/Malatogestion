"""Las 500 papeletas del aniversario, en un PDF de verdad.

Se escribe el PDF a mano: texto vectorial, A4, 3x5 por hoja, con líneas de corte.
Así sale nítido al imprimir y el fichero pesa poco.
"""
import random
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8")

ANCHO, ALTO = 595.28, 841.89          # A4 en puntos
MARGEN = 18
COLS, FILAS = 3, 5
ANCHO_CELDA = (ANCHO - 2 * MARGEN) / COLS
ALTO_CELDA = (ALTO - 2 * MARGEN) / FILAS
POR_HOJA = COLS * FILAS

PREMIOS = [
    ("Mini Nevera Portátil Rígida", 1),
    ("Calendario 2027 Tudis", 9),
    ("Delantal azul Hellmann's", 4),
    ("Toalla Frigo", 3),
    ("Mini Nevera Flexible Roja Frigo", 4),
    ("Bolígrafo Tudis", 7),
    ("Peluche Bimbito", 10),
    ("Botella Plástico Negra Pepsi", 30),
    ("Flor Ambientador", 16),
    ("Vaso Cristal Infusión con Pajita", 5),
    ("Mini Nevera Alvalle", 10),
    ("Cantimplora Cristal Argal", 6),
    ("Mini Tabla Madera para Aperitivo", 6),
    ("Bolsa XL Negra Viaje Bocatta Club", 2),
]

TOTAL = 500
papeletas = []
for nombre, cuantas in PREMIOS:
    papeletas += [nombre] * cuantas
premios = len(papeletas)
papeletas += [None] * (TOTAL - premios)
random.seed(2026)
random.shuffle(papeletas)
hojas = (TOTAL + POR_HOJA - 1) // POR_HOJA

print(f"  premios: {premios} · gracias: {TOTAL - premios} · hojas: {hojas}")


def esc(t):
    """Prepara el texto para el PDF (WinAnsi y escapes)."""
    t = t.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
    return t.encode("cp1252", "replace").decode("cp1252")


def envuelve(texto, maximo):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if len(prueba) <= maximo:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def texto(x, y, t, tam, fuente="F1", color=(0.11, 0.17, 0.15)):
    return (f"BT /{fuente} {tam} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg "
            f"1 0 0 1 {x:.2f} {y:.2f} Tm ({esc(t)}) Tj ET\n")


def centrado(x0, ancho, y, t, tam, fuente="F1", color=(0.11, 0.17, 0.15)):
    # ancho aproximado: 0.5 * tam por carácter
    w = len(t) * tam * (0.52 if fuente == "F2" else 0.5)
    return texto(x0 + (ancho - w) / 2, y, t, tam, fuente, color)


Gris = (0.08, 0.10, 0.09)
Oro = (0.69, 0.48, 0.07)
Tinta = (0.11, 0.17, 0.15)
Tenue = (0.08, 0.10, 0.09)

contenido_paginas = []

for h in range(hojas):
    c = []
    # el marco de cada papeleta, con línea de puntos
    for fila in range(FILAS):
        for col in range(COLS):
            x = MARGEN + col * ANCHO_CELDA
            y = ALTO - MARGEN - (fila + 1) * ALTO_CELDA
            c.append(f"[0.30 0.30 0.30] 0.6 w [2 2] 0 d {x:.2f} {y:.2f} "
                     f"{ANCHO_CELDA:.2f} {ALTO_CELDA:.2f} re S\n")

    for i in range(POR_HOJA):
        num = h * POR_HOJA + i
        if num >= TOTAL:
            break
        fila, col = divmod(i, COLS)
        x = MARGEN + col * ANCHO_CELDA
        y_top = ALTO - MARGEN - fila * ALTO_CELDA
        premio = papeletas[num]

        # cabecera
        c.append(centrado(x, ANCHO_CELDA, y_top - 16, "MALATO", 10.5, "F2", Gris))
        c.append(centrado(x, ANCHO_CELDA, y_top - 27, "20 ANIVERSARIO", 7.4, "F2", Gris))

        # la misma altura para las dos: arriba, y mas grande
        ALTO_ET = 56
        if premio:
            c.append(centrado(x, ANCHO_CELDA, y_top - ALTO_ET, "¡ENHORABUENA!", 9.6, "F2", Tinta))
            lineas = envuelve(premio, 19)
            y0 = y_top - ALTO_ET - 30 - (len(lineas) - 1) * 8
            for j, ln in enumerate(lineas):
                c.append(centrado(x, ANCHO_CELDA, y0 - j * 15, ln, 12.5, "F2", Tinta))
        else:
            c.append(centrado(x, ANCHO_CELDA, y_top - ALTO_ET, "HOY NO HA SIDO.", 9.6, "F2", Tinta))
            for j, ln in enumerate(["Gracias por acompañarnos",
                                    "en nuestro aniversario."]):
                c.append(centrado(x, ANCHO_CELDA, y_top - ALTO_ET - 30 - j * 15, ln, 10.5, "F1", Tinta))

        # número
        c.append(texto(x + ANCHO_CELDA - 34, y_top - ALTO_CELDA + 8, f"nº {num + 1}", 7.4, "F2", Tenue))

    contenido_paginas.append("".join(c))

# ---------------------------------------------------------------- el PDF
objetos = []
objetos.append("<< /Type /Catalog /Pages 2 0 R >>")
objetos.append("")                                   # 2: pages (se rellena luego)
objetos.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
objetos.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

ids_paginas = []
for contenido in contenido_paginas:
    comprimido = zlib.compress(contenido.encode("cp1252", "replace"))
    # el diccionario y el contenido van en EL MISMO objeto
    objetos.append(f"<< /Length {len(comprimido)} /Filter /FlateDecode >>\nstream\n".encode()
                   + comprimido + b"\nendstream")
    id_contenido = len(objetos)
    objetos.append(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {ANCHO:.2f} {ALTO:.2f}] "
        f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {id_contenido} 0 R >>")
    ids_paginas.append(len(objetos))

objetos[1] = ("<< /Type /Pages /Count " + str(len(ids_paginas)) + " /Kids ["
              + " ".join(f"{i} 0 R" for i in ids_paginas) + "] >>")

# se monta el fichero
salida = open("PAPELETAS-ANIVERSARIO.pdf", "wb")
salida.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
posiciones = [0]
for i, obj in enumerate(objetos, start=1):
    posiciones.append(salida.tell())
    if isinstance(obj, bytes):
        salida.write(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    else:
        salida.write(f"{i} 0 obj\n{obj}\nendobj\n".encode("cp1252"))

inicio_xref = salida.tell()
salida.write(f"xref\n0 {len(objetos) + 1}\n".encode())
salida.write(b"0000000000 65535 f \n")
for p in posiciones[1:]:
    salida.write(f"{p:010d} 00000 n \n".encode())
salida.write(f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF\n".encode())
salida.close()

import os
print(f"  escrito PAPELETAS-ANIVERSARIO.pdf · {round(os.path.getsize('PAPELETAS-ANIVERSARIO.pdf')/1024,1)} KB")
