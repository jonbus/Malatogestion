"""Los carteles del 20 aniversario: el de la urna y el de los premios.

Mismo estilo que las papeletas: negro sobre blanco, negritas, sin florituras.
A4. Para A3, se imprime al 141 %.
"""
import os
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8")

ANCHO, ALTO = 595.28, 841.89


def esc(t):
    t = t.replace("\\", r"\\").replace("(", r"\(").replace(r")", r"\)")
    return t.encode("cp1252", "replace").decode("cp1252")


def texto(x, y, t, tam, fuente="F1", color=0):
    return (f"BT /{fuente} {tam} Tf {color:.3f} {color:.3f} {color:.3f} rg "
            f"1 0 0 1 {x:.2f} {y:.2f} Tm ({esc(t)}) Tj ET\n")


def centrado(y, t, tam, fuente="F2", color=0, ancho_pag=ANCHO):
    w = len(t) * tam * (0.56 if fuente == "F2" else 0.52)
    return texto((ancho_pag - w) / 2, y, t, tam, fuente, color)


def linea(x0, y0, x1, y1, grosor=1.0, color=0):
    return (f"{color:.3f} {color:.3f} {color:.3f} RG {grosor} w "
            f"{x0:.2f} {y0:.2f} m {x1:.2f} {y1:.2f} l S\n")


def escribir_pdf(nombre, contenidos):
    objetos = ["<< /Type /Catalog /Pages 2 0 R >>", "",
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"]
    ids = []
    for c in contenidos:
        z = zlib.compress(c.encode("cp1252", "replace"))
        objetos.append(f"<< /Length {len(z)} /Filter /FlateDecode >>\nstream\n".encode()
                       + z + b"\nendstream")
        id_c = len(objetos)
        objetos.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {ANCHO:.2f} {ALTO:.2f}] "
                       f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {id_c} 0 R >>")
        ids.append(len(objetos))
    objetos[1] = ("<< /Type /Pages /Count " + str(len(ids)) + " /Kids ["
                  + " ".join(f"{i} 0 R" for i in ids) + "] >>")

    f = open(nombre, "wb")
    f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    pos = [0]
    for i, obj in enumerate(objetos, start=1):
        pos.append(f.tell())
        if isinstance(obj, bytes):
            f.write(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
        else:
            f.write(f"{i} 0 obj\n{obj}\nendobj\n".encode("cp1252"))
    xref = f.tell()
    f.write(f"xref\n0 {len(objetos) + 1}\n".encode())
    f.write(b"0000000000 65535 f \n")
    for p in pos[1:]:
        f.write(f"{p:010d} 00000 n \n".encode())
    f.write(f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    f.close()
    print(f"  {nombre} · {round(os.path.getsize(nombre)/1024, 1)} KB")


# ============================================================ CARTEL 1 · LA URNA
c = []
c.append(centrado(770, "MALATO", 34))
c.append(centrado(742, "20 ANIVERSARIO", 15))
c.append(linea(150, 726, 445, 726, 1.2))
c.append(centrado(600, "CAMBIA TU TICKET", 30))
c.append(centrado(555, "POR UNA PAPELETA", 30))
c.append(linea(150, 520, 445, 520, 1.0))
c.append(centrado(462, "Mete la mano en la urna.", 19, "F1"))
c.append(centrado(432, "Si sale premio, te lo llevas.", 19, "F1"))
c.append(centrado(370, "Una compra, una papeleta.", 15, "F1", 0.25))
c.append(centrado(230, "Gracias por estos 20 años", 17, "F2"))
c.append(centrado(196, "a tu lado.", 17, "F2"))
c.append(linea(150, 165, 445, 165, 1.0))
c.append(centrado(130, "MALATO", 13))
urne = "".join(c)

# ============================================================ CARTEL 2 · LOS PREMIOS
PREMIOS = [
    ("Botella Plástico Negra Pepsi", 30),
    ("Flor Ambientador", 16),
    ("Peluche Bimbito", 10),
    ("Mini Nevera Alvalle", 10),
    ("Calendario 2027 Tudis", 9),
    ("Bolígrafo Tudis", 7),
    ("Cantimplora Cristal Argal", 6),
    ("Mini Tabla Madera para Aperitivo", 6),
    ("Vaso Cristal Infusión con Pajita", 5),
    ("Delantal azul Hellmann's", 4),
    ("Mini Nevera Flexible Roja Frigo", 4),
    ("Toalla Frigo", 3),
    ("Bolsa XL Negra Viaje Bocatta Club", 2),
    ("Mini Nevera Portátil Rígida", 1),
]

d = []
d.append(centrado(770, "MALATO", 34))
d.append(centrado(742, "20 ANIVERSARIO", 15))
d.append(linea(120, 726, 475, 726, 1.2))
d.append(centrado(686, "ESTOS SON LOS PREMIOS", 22))
d.append(linea(120, 668, 475, 668, 0.8))

y = 630
for nombre, cuantas in PREMIOS:
    d.append(texto(138, y, f"{cuantas}", 15, "F2"))
    d.append(texto(178, y, "×", 13, "F1", 0.35))
    d.append(texto(198, y, nombre, 13.5, "F1"))
    d.append(linea(120, y - 7, 475, y - 7, 0.25, 0.82))
    y -= 32

d.append(linea(120, y + 8, 475, y + 8, 0.8))
d.append(centrado(y - 22, "113 PREMIOS EN TOTAL", 19))
d.append(centrado(y - 58, "Cambia tu ticket por una papeleta.", 14, "F1", 0.25))
d.append(centrado(80, "MALATO", 13))
premios = "".join(d)

escribir_pdf("CARTEL-URNA.pdf", [urne])
escribir_pdf("CARTEL-PREMIOS.pdf", [premios])
