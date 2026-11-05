"""El planning en A4 APAISADO, a dos columnas: el horario a la izquierda
y lo que hay que hacer a la derecha."""
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

W, H = 3508, 2480          # A4 apaisado a 300 ppp
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (30, 122, 60)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
M = 130

img = Image.new("RGB", (W, H), BLANCO)
d = ImageDraw.Draw(img)


def f(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def centro(y, texto, tam, ruta=COMIC):
    ft = f(ruta, tam)
    c = d.textbbox((0, 0), texto, font=ft)
    d.text(((W - (c[2] - c[0])) / 2 - c[0], y), texto, font=ft, fill=NEGRO)


def cabecera(x, y, texto, tam=64):
    p = d.text((x, y), texto, font=f(ROUND, tam), fill=VERDE)
    d.line([x, y + tam + 10, x + 1500, y + tam + 10], fill=VERDE, width=5)
    return y + tam + 26


def hora(x, y, h, texto, ancho_texto, tam=54):
    d.text((x, y), h, font=f(ROUND, tam), fill=NEGRO)
    ft = f(ROUND, tam)
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= ancho_texto:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    for i, ln in enumerate(lineas):
        d.text((x + 210, y + i * int(tam * 1.62)), ln, font=ft, fill=NEGRO)
    return y + int(tam * 1.62) * max(1, len(lineas)) + 14


# ---------------------------------------------------------------- cabecera
centro(50, "MALATO · 20 ANIVERSARIO", 132)
centro(212, "2006. urtetik ZUREKIN  ·  DOMINGO 8 DE NOVIEMBRE  ·  10:00 – 14:30", 58)
d.line([M, 320, W - M, 320], fill=NEGRO, width=10)

# ---------------------------------------------------------------- columna izquierda: el horario
IX = M
iy = 380
iy = cabecera(IX, iy, "EL DÍA, HORA A HORA", 70)
for h, txt in [
    ("7:00", "Llegamos nosotras."),
    ("7:30", "Llegan LAS PALMERAS."),
    ("8:00", "El LUNCH de la batukada, en los platos del sábado. Todo antes de abrir."),
    ("9:00", "Los globos, y sitio en el parking."),
    ("9:00", "LA MESA DE LA TARTA (ver a la derecha)."),
    ("9:30", "La urna, carteles, bolsas, premios, papelera y cajita."),
    ("10:00", "ABRIR. Los niños en la puerta. Llega EL FOTÓGRAFO."),
    ("10:00", "Empieza EL CANJE."),
    ("11:00", "La BATUKADA, con el lunch puesto."),
    ("11:00", "Visitar a ROSA con unas pastas."),
    ("11:30", "LA FOTO DE TODO EL EQUIPO."),
    ("13:00", "Regalos a la batukada."),
    ("14:30", "CERRAR. Contar la cajita: 113."),
]:
    iy = hora(IX, iy, h, txt, 1230)

# ---------------------------------------------------------------- columna derecha
DX = 1780
dy = 380

dy = cabecera(DX, dy, "LA MESA, EN ESTE ORDEN", 70)
for n, t in [
    ("1", "El sitio: que se vea y que no estorbe."),
    ("2", "Los caballetes: que apoyen los cuatro pies."),
    ("3", "El mantel, sin arrugas."),
    ("4", "La tarta. No se corta ni se come."),
    ("5", "Lazos y letras «20 urteurrena»."),
    ("6", "Palmeritas alrededor."),
    ("7", "Gominolas, y las PIRULETAS."),
    ("8", "La urna, los carteles, las bolsas y los premios."),
]:
    d.text((DX, dy), n + ".", font=f(ROUND, 52), fill=NEGRO)
    ft = f(ROUND, 40)
    palabras, lineas, actual = t.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= 1430:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    for i, ln in enumerate(lineas):
        d.text((DX + 50, dy + i * 88), ln, font=ft, fill=NEGRO)
    dy += 88 * max(1, len(lineas)) + 10

dy += 14
dy = cabecera(DX, dy, "NO PUEDE FALLAR", 70)
for t in [
    "El lunch es SOLO para la batukada, aparte.",
    "El altavoz lo trae la batukada.",
    "Fotógrafo: Distira, Javi · 647 91 06 17 · de 10:00 a 14:30.",
    "Una papeleta por ticket. Premiada a la cajita.",
    "Quien no gane, PIRULETA en la caja.",
    "Al cerrar: 113 papeletas en la cajita.",
]:
    d.text((DX, dy), "•", font=f(ROUND, 52), fill=NEGRO)
    ft = f(ROUND, 40)
    palabras, lineas, actual = t.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= 1430:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    for i, ln in enumerate(lineas):
        d.text((DX + 40, dy + i * 88), ln, font=ft, fill=NEGRO)
    dy += 88 * max(1, len(lineas)) + 10

# ---------------------------------------------------------------- pie
d.line([M, H - 150, W - M, H - 150], fill=NEGRO, width=6)
centro(H - 130, "500 papeletas · 113 premios · 500 piruletas · 500 palmeritas · 2 niños", 56)

# ---------------------------------------------------------------- margen y centrado
caja = img.convert("L").point(lambda p: 0 if p > 250 else 255).getbbox()
contenido = img.crop(caja)
MARGEN = 120
cabe = H - 2 * MARGEN
esc = cabe / contenido.size[1]
nw = int(contenido.size[0] * esc)
if nw > W - 2 * MARGEN:
    nw = W - 2 * MARGEN
    cabe = int(contenido.size[1] * nw / contenido.size[0])
contenido = contenido.resize((nw, cabe), Image.LANCZOS)
lienzo = Image.new("RGB", (W, H), BLANCO)
lienzo.paste(contenido, ((W - nw) // 2, (H - cabe) // 2))

lienzo.save("PLANNING-8-NOVIEMBRE.pdf", "PDF", resolution=300.0)
print(f"  PLANNING-8-NOVIEMBRE.pdf · {round(__import__('os').path.getsize('PLANNING-8-NOVIEMBRE.pdf')/1024,1)} KB")
lienzo.resize((W // 4, H // 4), Image.LANCZOS).save(".tmp-cart/PLANNING-vista.png")
print("  vista previa hecha")
