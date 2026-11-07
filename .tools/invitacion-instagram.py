"""La invitación para INSTAGRAM: 1080 × 1350 (4:5), que es el formato que
más pantalla ocupa en el feed. En euskera y en castellano.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1350          # 4:5, el del feed de Instagram
PAPEL = (252, 250, 243)
PAPEL_2 = (244, 240, 228)
TINTA = (48, 44, 38)
VERDE = (30, 154, 69)
GRIS = (150, 145, 130)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.ttf"
MARCA = r"C:\Users\Usuario\Desktop\APP Malato\docs\marca"

PAGINAS = {
    "EUSKERA": {
        "cabecera": "Gonbidapena",
        "titulo": "20 urte.",
        "lineas": [
            ("Ez dugu sinesten.", 44, 0),
            ("Igande honetan, azaroak 8,", 44, 0),
            ("10:00etatik 14:30era,", 44, 0),
            ("Malaton zain gaituzu.", 44, 26),
            ("Tarta, palmeritak, batukada", 44, 0),
            ("eta papeleta bat erosketa bakoitzeko.", 40, 26),
            ("Baina benetan nahi duguna", 46, "comic"),
            ("zu han ikustea da.", 46, 26),
            ("Eskerrik asko 20 urte hauengatik.", 38, 0),
            ("Malatoko taldea", 42, 0),
        ],
        "archivo": "INSTAGRAM-INVITACION-EUSKERA.jpg",
    },
    "CASTELLANO": {
        "cabecera": "Invitación",
        "titulo": "20 años.",
        "lineas": [
            ("No nos lo creemos ni nosotros.", 44, 0),
            ("Este domingo 8 de noviembre,", 44, 0),
            ("de 10:00 a 14:30,", 44, 0),
            ("te esperamos en Malato.", 44, 26),
            ("Habrá tarta, palmeritas, batukada", 44, 0),
            ("y una papeleta por cada compra.", 44, 26),
            ("Pero lo que de verdad queremos", 46, "comic"),
            ("es verte ahí.", 46, 26),
            ("Gracias por estos 20 años.", 42, 0),
            ("El equipo de Malato", 42, 0),
        ],
        "archivo": "INSTAGRAM-INVITACION-CASTELLANO.jpg",
    },
}


def una(nombre, datos):
    img = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(
            int(PAPEL[0] + (PAPEL_2[0] - PAPEL[0]) * t),
            int(PAPEL[1] + (PAPEL_2[1] - PAPEL[1]) * t),
            int(PAPEL[2] + (PAPEL_2[2] - PAPEL[2]) * t),
        ))
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse([W / 2 - 480, H * 0.38 - 480, W / 2 + 480, H * 0.38 + 480], fill=60)
    img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(170)))

    arbol = Image.open(os.path.join(MARCA, "logo-o-verde.png")).convert("RGBA")
    al = 96
    arbol = arbol.resize((al, int(al * arbol.size[1] / arbol.size[0])), Image.LANCZOS)
    img.paste(arbol, ((W - al) // 2, 60), arbol)

    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(ROUND, 40)
    w = d.textlength(datos["cabecera"], font=ft)
    d.text(((W - w) / 2, 188), datos["cabecera"], font=ft, fill=GRIS)
    d.line([(W / 2 - 80, 244), (W / 2 + 80, 244)], fill=GRIS, width=2)

    ft = ImageFont.truetype(ROUND, 76)
    w = d.textlength(datos["titulo"], font=ft)
    d.text(((W - w) / 2, 280), datos["titulo"], font=ft, fill=VERDE)

    y = 280 + int(76 * 1.42) + 16
    for texto, tam, extra in datos["lineas"]:
        ruta = COMIC if extra == "comic" else ROUND
        f2 = ImageFont.truetype(ruta, tam)
        w = d.textlength(texto, font=f2)
        d.text(((W - w) / 2, y), texto, font=f2, fill=TINTA)
        y += int(tam * 1.42) + (extra if isinstance(extra, int) else 0)

    d.line([(W / 2 - 80, y + 22), (W / 2 + 80, y + 22)], fill=VERDE, width=4)
    d.text((26, H - 34), "Malato · 2006. urtetik zurekin",
           font=ImageFont.truetype(ROUND, 24), fill=(180, 175, 160))
    d.text((W - 60, H - 34), "8.11.2026", font=ImageFont.truetype(ROUND, 24), fill=(180, 175, 160))

    img.save(datos["archivo"], "JPEG", quality=95, optimize=True)
    print(f"  {datos['archivo']} · {round(os.path.getsize(datos['archivo'])/1024,0)} KB")
    img.resize((W // 3, H // 3), Image.LANCZOS).save(
        f".tmp-cart/IG-{'eu' if nombre == 'EUSKERA' else 'es'}.png")


for nombre, datos in PAGINAS.items():
    una(nombre, datos)
print("  hechas las dos para instagram (1080 x 1350)")
