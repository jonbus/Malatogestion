"""Los carteles del 20 aniversario, con el logotipo y dibujos hechos a mano.

Blanco y negro. Los dibujos son vectoriales: estrellas, confeti y una papeleta.
"""
import math
import os
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8")

ANCHO, ALTO = 595.28, 841.89
K = 0.5523  # para las curvas de los círculos


def esc(t):
    t = t.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
    return t.encode("cp1252", "replace").decode("cp1252")


def texto(x, y, t, tam, fuente="F1", color=0):
    return (f"BT /{fuente} {tam} Tf {color:.3f} {color:.3f} {color:.3f} rg "
            f"1 0 0 1 {x:.2f} {y:.2f} Tm ({esc(t)}) Tj ET\n")


def centrado(y, t, tam, fuente="F2", color=0, ancho_pag=ANCHO):
    w = len(t) * tam * (0.56 if fuente == "F2" else 0.52)
    return texto((ancho_pag - w) / 2, y, t, tam, fuente, color)

def centrado_en(x0, ancho_caja, y, t, tam, fuente="F2", color=0):
    w = len(t) * tam * (0.56 if fuente == "F2" else 0.52)
    return texto(x0 + (ancho_caja - w) / 2, y, t, tam, fuente, color)


def linea(x0, y0, x1, y1, grosor=1.0, color=0):
    return (f"{color:.3f} {color:.3f} {color:.3f} RG {grosor} w "
            f"{x0:.2f} {y0:.2f} m {x1:.2f} {y1:.2f} l S\n")


def rect(x, y, w, h, grosor=1.0, color=0, relleno=False):
    op = "f" if relleno else "S"
    return (f"{color:.3f} {color:.3f} {color:.3f} RG {color:.3f} {color:.3f} {color:.3f} rg "
            f"{grosor} w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re {op}\n")


def circulo(cx, cy, r, relleno=True, color=0, grosor=1.0):
    k = r * K
    camino = (f"{cx+r:.2f} {cy:.2f} m "
              f"{cx+r:.2f} {cy+k:.2f} {cx+k:.2f} {cy+r:.2f} {cx:.2f} {cy+r:.2f} c "
              f"{cx-k:.2f} {cy+r:.2f} {cx-r:.2f} {cy+k:.2f} {cx-r:.2f} {cy:.2f} c "
              f"{cx-r:.2f} {cy-k:.2f} {cx-k:.2f} {cy-r:.2f} {cx:.2f} {cy-r:.2f} c "
              f"{cx+k:.2f} {cy-r:.2f} {cx+r:.2f} {cy-k:.2f} {cx+r:.2f} {cy:.2f} c ")
    op = "f" if relleno else "S"
    return (f"{color:.3f} {color:.3f} {color:.3f} rg {grosor} w " + camino + op + "\n")


def estrella(cx, cy, r, relleno=True, color=0, grosor=1.2):
    puntos = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.44
        puntos.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    camino = f"{puntos[0][0]:.2f} {puntos[0][1]:.2f} m "
    for px, py in puntos[1:]:
        camino += f"{px:.2f} {py:.2f} l "
    camino += "h "
    op = "f" if relleno else "S"
    return (f"{color:.3f} {color:.3f} {color:.3f} rg {grosor} w " + camino + op + "\n")


def triangulo(x, y, tam, color=0, giro=0.0):
    pts = []
    for i in range(3):
        a = giro + i * 2 * math.pi / 3
        pts.append((x + tam * math.cos(a), y + tam * math.sin(a)))
    camino = f"{pts[0][0]:.2f} {pts[0][1]:.2f} m "
    for px, py in pts[1:]:
        camino += f"{px:.2f} {py:.2f} l "
    camino += "h f\n"
    return f"{color:.3f} {color:.3f} {color:.3f} rg " + camino


def imagen(nombre, x, y, w, h):
    return f"q {w:.2f} 0 0 {h:.2f} {x:.2f} {y:.2f} cm /{nombre} Do Q\n"


def escribir_pdf(nombre, paginas):
    objetos = ["<< /Type /Catalog /Pages 2 0 R >>", "",
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"]

    for contenido, imagenes in paginas:
        ids_img = {}
        for nombre_img, ruta in imagenes:
            datos = open(ruta, "rb").read()
            from PIL import Image
            im = Image.open(ruta)
            w, h = im.size
            objetos.append(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} "
                           f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
                           f"/Length {len(datos)} >>\nstream\n".encode() + datos + b"\nendstream")
            ids_img[nombre_img] = len(objetos)
        z = zlib.compress(contenido.encode("cp1252", "replace"))
        objetos.append(f"<< /Length {len(z)} /Filter /FlateDecode >>\nstream\n".encode()
                       + z + b"\nendstream")
        id_c = len(objetos)
        xobj = " ".join(f"/{k} {v} 0 R" for k, v in ids_img.items())
        objetos.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {ANCHO:.2f} {ALTO:.2f}] "
                       f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> "
                       f"/XObject << {xobj} >> >> /Contents {id_c} 0 R >>")
    # las paginas son los ultimos objetos de cada bloque: se recogen
    total = len(objetos)
    ids = [i for i in range(total - len(paginas) + 1, total + 1)]
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
    f.write(f"xref\n0 {len(objetos)+1}\n".encode())
    f.write(b"0000000000 65535 f \n")
    for p in pos[1:]:
        f.write(f"{p:010d} 00000 n \n".encode())
    f.write(f"trailer\n<< /Size {len(objetos)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    f.close()
    print(f"  {nombre} · {round(os.path.getsize(nombre)/1024,1)} KB")


LOGO = ".tmp-logo/marca.jpg"
O_GLIFO = ".tmp-logo/o.jpg"
LOGO_W, LOGO_H = 657, 250

# ============================================================ CARTEL 1 · LA URNA
c = []

# confeti arriba y a los lados
import random
random.seed(11)
for _ in range(46):
    x = random.uniform(18, ANCHO - 18)
    y = random.uniform(690, 830)
    t = random.choice(["c", "e", "t", "r"])
    tam = random.uniform(1.6, 4.2)
    if t == "c":
        c.append(circulo(x, y, tam))
    elif t == "e":
        c.append(estrella(x, y, tam * 1.5))
    elif t == "t":
        c.append(triangulo(x, y, tam * 1.4, giro=random.uniform(0, 6)))
    else:
        c.append(rect(x, y, tam * 2.4, tam * 1.1, relleno=True))

# el logotipo
ancho_logo = 200
alto_logo = ancho_logo * LOGO_H / LOGO_W
c.append(imagen("Logo", (ANCHO - ancho_logo) / 2, 690, ancho_logo, alto_logo))

c.append(centrado(648, "2006. urtetik ZUREKIN", 16))
c.append(linea(120, 628, ANCHO - 120, 628, 1.2))

c.append(centrado(560, "CAMBIA TU TICKET", 32))
c.append(centrado(514, "POR UNA PAPELETA", 32))

# --- la papeleta dibujada
PX, PY, PW, PH = 118, 330, ANCHO - 236, 148
c.append(f"0 0 0 RG 2.4 w {PX:.2f} {PY:.2f} {PW:.2f} {PH:.2f} re S\n")
# la línea de puntos (el troquel)
c.append(f"0 0 0 RG 1.4 w [4 3] 0 d {PX+PW*0.62:.2f} {PY:.2f} m {PX+PW*0.62:.2f} {PY+PH:.2f} l S [] 0 d\n")
# muescas
for yy in (PY, PY + PH):
    c.append(circulo(PX + PW * 0.62, yy, 7, relleno=False, grosor=2.0))
# estrellas dentro
IZQ = PW * 0.60
c.append(estrella(PX + IZQ / 2, PY + PH * 0.58, 30))
c.append(estrella(PX + IZQ / 2, PY + PH * 0.58, 18, relleno=False, grosor=1.4))
c.append(centrado_en(PX, IZQ, PY + 22, "TE PUEDE TOCAR", 12.5))
c.append(centrado_en(PX + IZQ, PW - IZQ, PY + PH * 0.58, "PREMIO", 23))
c.append(centrado_en(PX + IZQ, PW - IZQ, PY + PH * 0.30, "¡MUCHA SUERTE!", 13, "F1"))

c.append(centrado(268, "Mete la mano en la urna.", 19, "F1"))
c.append(centrado(238, "Si sale premio, te lo llevas.", 19, "F1"))
c.append(centrado(186, "Una compra, una papeleta.", 15, "F1", 0.25))

c.append(imagen("O", ANCHO / 2 - 13, 132, 26, 29))

c.append(linea(120, 112, ANCHO - 120, 112, 1.0))
c.append(centrado(80, "Gracias por estos 20 años a tu lado.", 14))

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
ancho_logo2 = 210
alto_logo2 = ancho_logo2 * LOGO_H / LOGO_W
d.append(imagen("Logo", (ANCHO - ancho_logo2) / 2, 752, ancho_logo2, alto_logo2))
d.append(centrado(722, "2006. urtetik ZUREKIN", 15))
d.append(linea(95, 706, ANCHO - 95, 706, 1.2))
d.append(centrado(668, "ESTOS SON LOS PREMIOS", 22))
d.append(linea(95, 650, ANCHO - 95, 650, 0.8))

y = 612
for nombre_premio, cuantas in PREMIOS:
    d.append(texto(115, y, f"{cuantas}", 15, "F2"))
    d.append(texto(155, y, "×", 13, "F1", 0.35))
    d.append(texto(175, y, nombre_premio, 13.5, "F1"))
    d.append(linea(95, y - 7, ANCHO - 95, y - 7, 0.25, 0.82))
    y -= 31

d.append(linea(95, y + 8, ANCHO - 95, y + 8, 0.8))
d.append(centrado(y - 24, "113 PREMIOS EN TOTAL", 19))
d.append(centrado(y - 58, "Cambia tu ticket por una papeleta.", 13.5, "F1", 0.25))
d.append(imagen("O", ANCHO / 2 - 11, 42, 22, 24))

# el cartel de la urna lo hace cartel-urna2.py (el dibujado).
# aqui SOLO los premios, para no pisarlo.
escribir_pdf("CARTEL-PREMIOS.pdf", [(("".join(d)), [("Logo", LOGO), ("O", O_GLIFO)])])
