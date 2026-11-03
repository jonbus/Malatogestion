"""El cartel del aniversario EN COLOR, en castellano y en euskera.

Para el whatsapp del pueblo. Mismo dibujo que el de la tienda, pero pintado.
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

W, H = 2480, 3508

CREMA = (255, 246, 228)
CORAL = (231, 90, 74)
AMARILLO = (255, 200, 40)
AZUL = (52, 138, 208)
VERDE = (46, 158, 92)
MAGENTA = (222, 76, 138)
ROJO = (222, 72, 62)
NARANJA = (246, 146, 46)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROSA = (250, 190, 205)
VERDE_MALATO = (30, 154, 69)      # el de la «o» del logotipo

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"

TEXTOS = {
    "es": {
        "domingo": "DOMINGO",
        "ocho": "8",
        "noviembre": "DE NOVIEMBRE",
        "aniversario": "20 ANIVERSARIO",
        "manana": "por la mañana",
        "linea1": "TARTA · PREMIOS",
        "linea2": "ACTUACIÓN MUSICAL",
        "linea3": "DULCES ARTESANOS",
        "gancho1": "¡NO TE LO PUEDES",
        "gancho2": "PERDER!",
        "pie": "Te esperamos. Ven a celebrarlo con nosotros.",
        "salida": "CARTEL-ANIVERSARIO-CASTELLANO.pdf",
    },
    "eu": {
        "domingo": "IGANDEA",
        "ocho": "8",
        "noviembre": "AZAROAK",
        "aniversario": "20 URTEURRENA",
        "manana": "goizean",
        "linea1": "TARTA · SARIAK",
        "linea2": "MUSIKA EMANALDIA",
        "linea3": "GOZO ARTISAUAK",
        "gancho1": "EZ GALDU!",
        "gancho2": "",
        "pie": "Zure zain gaude. Etorri gurekin ospatzera.",
        "salida": "CARTEL-ANIVERSARIO-EUSKERA.pdf",
    },
}


def f(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def haz(idioma):
    T = TEXTOS[idioma]
    # se dibuja en un lienzo mas alto: luego se recorta y se ajusta
    ALTO_DIBUJO = 3960
    img = Image.new("RGB", (W, ALTO_DIBUJO), CREMA)
    d = ImageDraw.Draw(img)

    def centro(y, texto, tam, ruta=COMIC, color=NEGRO):
        ft = f(ruta, tam)
        c = d.textbbox((0, 0), texto, font=ft)
        d.text(((W - (c[2] - c[0])) / 2 - c[0], y), texto, font=ft, fill=color)
        return c[3] - c[1]

    def nube(x0, y0, x1, y1, color):
        """Una nube: varios bollos unidos por la base, todo del mismo color."""
        alto = y1 - y0
        ancho = x1 - x0
        # la base
        d.rounded_rectangle([x0 + ancho * 0.03, y0 + alto * 0.10,
                             x1 - ancho * 0.03, y1 - alto * 0.04],
                            radius=alto * 0.30, fill=color)
        # los bollos, asomando solo por el borde de arriba
        for fx, fr in [(0.12, 0.17), (0.26, 0.20), (0.41, 0.18), (0.55, 0.21),
                       (0.69, 0.19), (0.83, 0.20), (0.94, 0.16)]:
            cx = x0 + ancho * fx
            r = alto * fr
            cy = y0 + r * 0.92
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        # y dos bollos pequenos a los lados, para que no parezca un rectangulo
        for fx, fy, fr in [(0.02, 0.62, 0.13), (0.98, 0.64, 0.12)]:
            cx = x0 + ancho * fx
            cy = y0 + alto * fy
            r = alto * fr
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    def estrella(cx, cy, r, color=AMARILLO):
        pts = []
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.44
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=color, outline=NEGRO)
        d.line(pts + [pts[0]], fill=NEGRO, width=10)

    def globo(cx, cy, r, color, largo=1.0):
        d.ellipse([cx - r, cy - r * 1.18, cx + r, cy + r * 1.18], fill=color, outline=NEGRO, width=12)
        d.polygon([(cx - r * 0.16, cy + r * 1.12), (cx + r * 0.16, cy + r * 1.12), (cx, cy + r * 1.32)],
                  fill=NEGRO)
        pts = [(cx, cy + r * 1.32)]
        pasos = max(2, int(6 * largo))
        for k in range(1, pasos + 1):
            pts.append((cx + (18 if k % 2 else -18), cy + r * 1.32 + k * r * 0.32 * largo))
        d.line(pts, fill=NEGRO, width=6, joint="curve")
        # el brillo
        d.ellipse([cx - r * 0.55, cy - r * 0.75, cx - r * 0.15, cy - r * 0.35], fill=BLANCO)

    def tarta(cx, cy, w, h):
        d.rounded_rectangle([cx - w / 2, cy, cx + w / 2, cy + h * 0.55], radius=40,
                            fill=ROSA, outline=NEGRO, width=12)
        d.rounded_rectangle([cx - w * 0.34, cy - h * 0.42, cx + w * 0.34, cy + h * 0.06], radius=36,
                            fill=(255, 232, 240), outline=NEGRO, width=12)
        for k, col in zip((-1, 0, 1), (AZUL, CORAL, AMARILLO)):
            x = cx + k * w * 0.18
            d.line([x, cy - h * 0.42, x, cy - h * 0.60], fill=NEGRO, width=10)
            d.ellipse([x - 16, cy - h * 0.70, x + 16, cy - h * 0.54], fill=col, outline=NEGRO)

    def tambor(cx, cy, w, h):
        d.ellipse([cx - w / 2, cy, cx + w / 2, cy + h * 0.22], fill=(255, 214, 170),
                  outline=NEGRO, width=12)
        d.rectangle([cx - w / 2, cy + h * 0.11, cx + w / 2, cy + h * 0.72], fill=ROJO,
                    outline=NEGRO, width=12)
        d.ellipse([cx - w / 2, cy + h * 0.61, cx + w / 2, cy + h * 0.83], fill=(255, 214, 170),
                  outline=NEGRO, width=12)
        for k in range(1, 4):
            y = cy + h * (0.11 + k * 0.15)
            d.line([cx - w / 2, y, cx + w / 2, y - h * 0.04], fill=(245, 210, 120), width=8)
        d.line([cx + w * 0.42, cy + h * 0.10, cx + w * 0.86, cy - h * 0.16], fill=NEGRO, width=9)
        d.line([cx + w * 0.30, cy + h * 0.14, cx + w * 0.66, cy - h * 0.26], fill=NEGRO, width=9)

    def ticket(cx, cy, w, h, ang):
        t = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
        dt = ImageDraw.Draw(t)
        dt.rectangle([30, 30, 30 + w, 30 + h], fill=AMARILLO, outline=NEGRO, width=12)
        dt.line([30 + w * 0.12, 30 + h * 0.35, 30 + w * 0.88, 30 + h * 0.35], fill=NEGRO, width=7)
        dt.line([30 + w * 0.12, 30 + h * 0.62, 30 + w * 0.7, 30 + h * 0.62], fill=NEGRO, width=7)
        t = t.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.paste(t, (cx - t.size[0] // 2, cy - t.size[1] // 2), t)

    # --- el logotipo, con su verde
    logo = Image.open(".tmp-logo/marca-color.png").convert("RGB")
    al = 1020
    la = int(al * logo.size[1] / logo.size[0])
    logo = logo.resize((al, la), Image.LANCZOS)
    # el blanco del logotipo se vuelve transparente, para que se vea el fondo
    mascara = logo.convert("L").point(lambda p: 255 if p < 245 else 0)
    img.paste(logo, ((W - al) // 2, 32), mascara)

    # globos de arriba, con color
    globo(280, 340, 236, CORAL, 0.12)
    globo(520, 250, 176, AMARILLO, 0.12)
    globo(2200, 340, 240, AZUL, 0.12)
    globo(1960, 250, 178, VERDE, 0.12)

    # --- la nube verde con la fecha en blanco
    nube(110, 430, W - 110, 1590, VERDE_MALATO)
    centro(650, T["domingo"], 140, ROUND, BLANCO)
    centro(790, T["ocho"], 360, ROUND, BLANCO)
    centro(1180, T["noviembre"], 124, ROUND, BLANCO)
    centro(1310, T["aniversario"], 94, ROUND, BLANCO)
    centro(1420, T["manana"], 90, COMIC, BLANCO)

    # --- los dibujos
    for (sx, sy) in [(215, 1600), (2265, 1600), (300, 1790), (2180, 1790)]:
        estrella(sx, sy, 58)

    globo(400, 2120, 158, MAGENTA)
    globo(690, 2020, 128, AMARILLO)
    globo(268, 2380, 118, VERDE)
    globo(2080, 2140, 146, NARANJA)
    globo(2310, 2360, 122, MAGENTA)
    globo(1840, 2000, 114, AZUL)

    tarta(760, 2480, 640, 520)
    tambor(1830, 2580, 420, 520)
    ticket(1330, 2260, 230, 150, -12)
    ticket(1450, 2460, 210, 138, 14)

    for (cx, cy, r, col) in [(1330, 2830, 22, AZUL), (1180, 3000, 16, CORAL),
                             (1500, 3020, 18, VERDE), (980, 2100, 14, NARANJA),
                             (1700, 2950, 14, MAGENTA)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=NEGRO, width=5)

    # --- el texto de abajo
    centro(3130, T["linea1"], 104)
    centro(3245, T["linea2"], 96)
    centro(3350, T["linea3"], 94)

    # --- el gancho, en una caja amarilla
    caja_y = 3480
    ft = f(COMIC, 104)
    ancho1 = d.textlength(T["gancho1"], font=ft)
    ancho2 = d.textlength(T["gancho2"], font=ft) if T["gancho2"] else 0
    ancho = max(ancho1, ancho2) + 180
    alto_caja = 300 if T["gancho2"] else 180
    d.rounded_rectangle([(W - ancho) / 2, caja_y, (W + ancho) / 2, caja_y + alto_caja],
                        radius=48, fill=VERDE_MALATO)
    centro(caja_y + 40, T["gancho1"], 104, COMIC, BLANCO)
    if T["gancho2"]:
        centro(caja_y + 165, T["gancho2"], 104, COMIC, BLANCO)

    # --- el pie
    centro(caja_y + alto_caja + 70, T["pie"], 60, ROUND)

    # --- margen de 1,5 cm y centrado
    caja = img.convert("L").point(lambda p: 0 if p > 250 else 255).getbbox()
    contenido = img.crop(caja)
    MARGEN = 177
    cabe = H - 2 * MARGEN
    esc = cabe / contenido.size[1]
    nw = int(contenido.size[0] * esc)
    contenido = contenido.resize((nw, cabe), Image.LANCZOS)
    lienzo = Image.new("RGB", (W, H), CREMA)
    lienzo.paste(contenido, ((W - nw) // 2, MARGEN))

    import os
    lienzo.save(T["salida"], "PDF", resolution=300.0)
    print(f"  {T['salida']} · {round(os.path.getsize(T['salida'])/1024,1)} KB")

    # --- foto para mandar por WhatsApp: grande, y otra ya preparada
    nombre = T["salida"].replace(".pdf", "")
    lienzo.save(nombre + ".jpg", "JPEG", quality=93, optimize=True)
    print(f"  {nombre}.jpg · {round(os.path.getsize(nombre + '.jpg')/1024,1)} KB")

    peq = lienzo.resize((1600, int(1600 * H / W)), Image.LANCZOS)
    peq.save(nombre + "-whatsapp.jpg", "JPEG", quality=90, optimize=True)
    print(f"  {nombre}-whatsapp.jpg · {round(os.path.getsize(nombre + '-whatsapp.jpg')/1024,1)} KB")

    lienzo.resize((W // 3, H // 3), Image.LANCZOS).save(f".tmp-cart/{idioma}-vista.png")


haz("es")
haz("eu")
print("  hechos los dos")
