"""Genera la paleta de color de la app (verde botella no demasiado oscuro).

El generador SE VERIFICA A SI MISMO: comprueba que ninguna muestra se sale del
lienzo y, tras guardar, vuelve a abrir el PNG y muestrea el centro de cada
muestra para confirmar que el color pintado es el esperado. Un generador de
imagenes que no se comprueba produce lienzos a los que les faltan colores.
"""
from PIL import Image, ImageDraw, ImageFont

W = 1180
MARGEN = 40
ANCHO = 245
PASO = 258
POR_FILA = 4          # (W - 2*MARGEN) // PASO

BG = (247, 250, 248)
TINTA = (28, 43, 38)
VERDE_OSCURO = (10, 87, 65)

img = Image.new("RGB", (1240, 1020), BG)
d = ImageDraw.Draw(img)


def font(size, bold=False):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TIT, F_SEC, F_NAME = font(30, True), font(17, True), font(15, True)
F_HEX, F_NOTE = font(14), font(13)

muestras = []   # (centro_x, centro_y, rgb) para la autoverificacion


def luminancia(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hx(rgb):
    return "#%02X%02X%02X" % rgb


d.text((MARGEN, 30), "Paleta · App Malato", font=F_TIT, fill=TINTA)
d.text((MARGEN, 70), "Verde botella no demasiado oscuro · contraste calculado, no estimado",
       font=F_NOTE, fill=(90, 107, 100))

SECCIONES = [
    ("MARCA", [
        ("verde-botella-600", (14, 122, 86), "principal: botones y cabecera"),
        ("verde-botella-400", (22, 163, 116), "hover y estados activos"),
        ("verde-botella-800", (10, 87, 65), "sidebar y texto de marca"),
        ("verde-botella-050", (233, 244, 239), "fondos suaves y seleccion"),
    ]),
    ("NEUTROS", [
        ("texto-principal", (28, 43, 38), "titulares y cuerpo"),
        ("texto-secundario", (90, 107, 100), "etiquetas y ayudas"),
        ("borde", (216, 224, 220), "separadores y tarjetas"),
        ("fondo", (247, 250, 248), "fondo de pantalla"),
    ]),
    ("ESTADOS DE TAREA", [
        ("pendiente", (138, 148, 166), "gris azulado"),
        ("asignada", (46, 111, 217), "azul"),
        ("en-curso", (201, 122, 14), "ambar"),
        ("bloqueada", (192, 57, 43), "rojo"),
        ("hecha", (78, 154, 106), "verde apagado + check"),
        ("cancelada", (154, 160, 166), "gris"),
    ]),
]

y = 115
alto_total_min = 0
for titulo, items in SECCIONES:
    d.text((MARGEN, y), titulo, font=F_SEC, fill=VERDE_OSCURO)
    y += 27
    for i, (nombre, rgb, nota) in enumerate(items):
        fila, col = divmod(i, POR_FILA)
        x = MARGEN + col * PASO
        yy = y + fila * 78
        d.rounded_rectangle([x, yy, x + ANCHO, yy + 64], radius=9, fill=rgb,
                            outline=(200, 210, 205) if luminancia(rgb) > 0.5 else None)
        txt = TINTA if luminancia(rgb) > 0.5 else (255, 255, 255)
        d.text((x + 14, yy + 10), nombre, font=F_NAME, fill=txt)
        d.text((x + 14, yy + 30), hx(rgb), font=F_HEX, fill=txt)
        d.text((x + 14, yy + 46), nota[:30], font=F_NOTE, fill=txt)
        muestras.append((x + ANCHO // 2, yy + 32, rgb))
        alto_total_min = max(alto_total_min, yy + 64)
    filas = -(-len(items) // POR_FILA)
    y += filas * 78 + 14

y = alto_total_min + 34
d.text((MARGEN, y), "PRIORIDAD", font=F_SEC, fill=VERDE_OSCURO)
y += 27
for i, (nombre, rgb) in enumerate([
    ("baja", (138, 148, 166)), ("media", (46, 111, 217)),
    ("alta", (201, 122, 14)), ("urgente", (192, 57, 43)),
]):
    x = MARGEN + i * PASO
    d.rounded_rectangle([x, y, x + ANCHO, y + 50], radius=9, fill=rgb)
    d.text((x + 14, y + 16), nombre, font=F_NAME, fill=(255, 255, 255))
    muestras.append((x + ANCHO // 2, y + 25, rgb))

y += 82
d.text((MARGEN, y), "CONTRASTE (WCAG · AA exige 4.5 en texto normal)",
       font=F_SEC, fill=VERDE_OSCURO)
y += 28
for etiqueta, fg, bg in [
    ("texto blanco sobre verde-botella-600", (255, 255, 255), (14, 122, 86)),
    ("texto blanco sobre verde-botella-800", (255, 255, 255), (10, 87, 65)),
    ("texto principal sobre fondo", (28, 43, 38), (247, 250, 248)),
    ("texto secundario sobre fondo", (90, 107, 100), (247, 250, 248)),
]:
    ratio = contraste(fg, bg)
    veredicto = "AA y AAA" if ratio >= 7 else ("AA" if ratio >= 4.5 else "NO CUMPLE")
    d.text((MARGEN + 8, y), etiqueta, font=F_NOTE, fill=TINTA)
    d.text((660, y), f"{ratio:.2f}:1   {veredicto}", font=F_NAME,
           fill=VERDE_OSCURO if ratio >= 4.5 else (192, 57, 43))
    y += 22

y += 16
d.rounded_rectangle([MARGEN, y, 1200, y + 74], radius=9, fill=(255, 246, 224),
                    outline=(201, 122, 14))
for i, linea in enumerate([
    "AVISO: el verde de marca y el verde de 'hecha' compiten entre si.",
    "La marca se reserva para identidad y acciones; 'hecha' va siempre con icono",
    "de check y en la ultima columna. El color NUNCA es el unico aviso.",
]):
    d.text((MARGEN + 18, y + 12 + i * 19), linea,
           font=F_NAME if i == 0 else F_NOTE,
           fill=(120, 70, 10))

# ---------------------------------------------------------------- verificacion
alto_necesario = y + 74 + MARGEN
if alto_necesario > img.height:
    raise SystemExit(f"FALLO: el contenido necesita {alto_necesario}px y el lienzo tiene {img.height}")

for cx, cy, _ in muestras:
    if not (0 <= cx < img.width and 0 <= cy < img.height):
        raise SystemExit(f"FALLO: muestra fuera del lienzo en ({cx},{cy})")

img.save("docs/paleta.png")

# Reabrir el PNG y comprobar pixel a pixel que cada muestra tiene SU color.
comprobada = Image.open("docs/paleta.png").convert("RGB")
print(f"lienzo {comprobada.size[0]}x{comprobada.size[1]} · {len(muestras)} muestras")
mal = 0
for i, (cx, cy, rgb) in enumerate(muestras):
    real = comprobada.getpixel((cx, cy))
    if real != rgb:
        mal += 1
        print(f"  MAL  muestra {i} en ({cx},{cy}): esperado {rgb} real {real}")
print(f"{len(muestras) - mal}/{len(muestras)} muestras correctas")
raise SystemExit(1 if mal else 0)
