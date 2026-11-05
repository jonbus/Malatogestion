"""El planning del 8 de noviembre, en una hoja A4 para colgar."""
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

W, H = 2480, 3508
N = (0, 0, 0)
B = (255, 255, 255)
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"

img = Image.new("RGB", (W, H), B)
d = ImageDraw.Draw(img)
M = 180


def f(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def texto(x, y, t, tam, ruta=ROUND):
    d.text((x, y), t, font=f(ruta, tam), fill=N)
    return y + int(tam * 1.22)


def centro(y, t, tam, ruta=ROUND):
    ft = f(ruta, tam)
    c = d.textbbox((0, 0), t, font=ft)
    d.text(((W - (c[2] - c[0])) / 2 - c[0], y), t, font=ft, fill=N)
    return y + int(tam * 1.22)


def raya(y, grosor=8):
    d.line([M, y, W - M, y], fill=N, width=grosor)
    return y


def apartado(y, titulo):
    y += 18
    y = texto(M, y, titulo, 62)
    y = raya(y + 6, 6) + 26
    return y


def paso(y, hora, que, alto=56):
    d.text((M, y), hora, font=f(ROUND, alto), fill=N)
    # el texto largo, partido
    ft = f(ROUND, alto)
    ancho = W - M - (M + 470)
    palabras, lineas, actual = que.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    for i, ln in enumerate(lineas):
        d.text((M + 470, y + i * int(alto * 1.15)), ln, font=ft, fill=N)
    return y + int(alto * 1.15) * max(1, len(lineas)) + 12


# --- cabecera
y = centro(150, "MALATO · 20 ANIVERSARIO", 104, COMIC)
y = centro(y + 4, "2006. urtetik ZUREKIN", 58)
y = centro(y + 16, "DOMINGO 8 DE NOVIEMBRE  -  10:00 – 14:30", 66)
raya(y + 20, 12)

# --- los días antes
y = apartado(y + 30, "LOS DÍAS ANTES")
y = paso(y, "Jue 5", "Montar los globos de estructura (arcos y columnas). Dejarlos en el almacén.")
y = paso(y, "Vie 6", "Los globos que se ven de cerca. La carpa, si se ha decidido.")
y = paso(y, "Sáb 7", "Dejarlo TODO listo. Nada nuevo. Bolsas y premios juntos.")

# --- el domingo
y = apartado(y, "EL DOMINGO")
y = paso(y, "7:00", "Llegamos nosotras. A las 7:30 llegan LAS PALMERAS.")
y = paso(y, "8:00", "Preparar el LUNCH de la batukada en los platos que se dejaron listos el sábado: jamón, cabecero, pastas, aceitunas, patatas, pan y queso. Todo antes de abrir.")
y = paso(y, "9:00", "Subir y colocar los globos. Hacer o reservar sitio en el parking para la batukada.")
y = paso(y, "9:00", "LA MESA: caballetes y tablón / mantel / tarta / lazos / letras «20 urteurrena» / palmeritas alrededor / gominolas / PIRULETAS")
y = paso(y, "9:30", "La urna/ los carteles / las bolsas / los premios / la papelera y la cajita")
y = paso(y, "10:00", "ABRIR. Los dos niños en la puerta. Y llega EL FOTÓGRAFO (Distira, Javi 647 91 06 17): se queda hasta las 14:30.")
y = paso(y, "10:00", "Empieza EL CANJE: el ticket por una papeleta. Quien no gane, cambia la papeleta por una PIRULETA en la caja.")
y = paso(y, "11:00", "La BATUKADA. El lunch ya tiene que estar puesto.")
y = paso(y, "11:00", "Visitar a ROSA y llevarle unas pastas.")
y = paso(y, "11:30", "LA FOTO DE TODO EL EQUIPO, delante de la tarta.")
y = paso(y, "13:00", "Regalos a la batukada, al acabar: bolsa + calcetines + cantimplora. Los preparan los niños.")
y = paso(y, "14:30", "CERRAR. Recoger. Contar la cajita: tienen que ser 113.")

# --- lo que no puede fallar
y = apartado(y, "LO QUE NO PUEDE FALLAR")
for linea in [
    "Las 500 papeletas llegan el lunes 2. Se cuentan y se guardan con la urna.",
    "La mesa firme: tablón sobre caballetes, y encima van 500 palmeritas, la urna y 113 premios.",
    "Las palmeritas TAPADAS hasta la hora. Están en la calle.",
    "Las napolitanas de Cadagua, aparte: son el recambio si se acaban las palmeras.",
    "La batukada y la música no suenan a la vez.",
    "Al cerrar: 113 papeletas en la cajita. Si no, falta un premio.",
]:
    d.text((M + 20, y), "•", font=f(ROUND, 54), fill=N)
    ft = f(ROUND, 52)
    palabras, lineas, actual = linea.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= W - M - 120:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    for i, ln in enumerate(lineas):
        d.text((M + 70, y + i * 62), ln, font=ft, fill=N)
    y += 62 * len(lineas) + 14

# --- los numeros, de un vistazo
# --- pie
raya(H - 165, 8)
centro(H - 145, "Los turnos de la tienda ya están arreglados. El fotógrafo, hasta las 14:30.", 40)
centro(H - 92, "El detalle, en el manual: ANIVERSARIO-PROCEDIMIENTO.md", 34)

img.save("PLANNING-8-NOVIEMBRE.pdf", "PDF", resolution=300.0)
print(f"  PLANNING-8-NOVIEMBRE.pdf · {round(__import__('os').path.getsize('PLANNING-8-NOVIEMBRE.pdf')/1024,1)} KB")
img.resize((W // 3, H // 3), Image.LANCZOS).save(".tmp-cart/PLANNING-vista.png")
print("  vista previa hecha")
