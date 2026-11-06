"""La carta en los dos idiomas: castellano y euskera."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
PAPEL = (252, 250, 243)
PAPEL_2 = (244, 240, 228)
TINTA = (48, 44, 38)
VERDE = (30, 154, 69)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
MARCA = r"C:\Users\Usuario\Desktop\APP Malato\docs\marca"

# líneas de cada idioma
TEXTOS = {
    "CASTELLANO": {
        "titulo": "20 años.",
        "lineas": [
            ("No nos lo creemos ni nosotros.", 52, "normal"),
            ("Este domingo 8 de noviembre,", 52, "normal"),
            ("de 10:00 a 14:30,", 52, "normal"),
            ("te esperamos en Malato.", 52, "normal"),
            ("Habrá tarta, palmeritas, batukada", 52, "normal"),
            ("y una papeleta por cada compra.", 52, "normal"),
            ("Pero lo que de verdad queremos", 56, "comic"),
            ("es verte ahí.", 56, "comic"),
            ("Gracias por estos 20 años.", 50, "normal"),
            ("El equipo de Malato", 50, "normal"),
        ],
    },
    "EUSKERA": {
        "titulo": "20 urte.",
        "lineas": [
            ("Ez dugu sinesten.", 52, "normal"),
            ("Igande honetan, azaroak 8,", 52, "normal"),
            ("10:00etatik 14:30era,", 52, "normal"),
            ("Malaton zain gaituzu.", 52, "normal"),
            ("Tarta, palmeritak, batukada", 52, "normal"),
            ("eta papeleta bat erosketa bakoitzeko.", 50, "normal"),
            ("Baina benetan nahi duguna", 56, "comic"),
            ("zu han ikustea da.", 56, "comic"),
            ("Eskerrik asko 20 urte hauengatik.", 48, "normal"),
            ("Malatoko taldea", 50, "normal"),
        ],
    },
}


def una(idioma):
    datos = TEXTOS[idioma]

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
    ImageDraw.Draw(halo).ellipse([W / 2 - 520, H * 0.35 - 520, W / 2 + 520, H * 0.35 + 520], fill=60)
    img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(190)))

    arbol = Image.open(os.path.join(MARCA, "logo-o-verde.png")).convert("RGBA")
    al = 150
    arbol = arbol.resize((al, int(al * arbol.size[1] / arbol.size[0])), Image.LANCZOS)
    img.paste(arbol, ((W - al) // 2, 110), arbol)

    d = ImageDraw.Draw(img)

    def linea(y, texto, tam, ruta):
        ft = ImageFont.truetype(ruta, tam)
        w = d.textlength(texto, font=ft)
        d.text(((W - w) / 2, y), texto, font=ft, fill=TINTA)
        return y + int(tam * 1.42)

    ft_tit = ImageFont.truetype(ROUND, 86)
    w = d.textlength(datos["titulo"], font=ft_tit)
    d.text(((W - w) / 2, 330), datos["titulo"], font=ft_tit, fill=VERDE)

    y = 330 + int(86 * 1.42) + 40
    for texto, tam, estilo in datos["lineas"]:
        ruta = COMIC if estilo == "comic" else ROUND
        y = linea(y, texto, tam, ruta)
        # aire entre los bloques
        if texto in ("No nos lo creemos ni nosotros.", "Ez dugu sinesten.",
                     "te esperamos en Malato.", "Malaton zain gaituzu.",
                     "y una papeleta por cada compra.", "eta papeleta bat erosketa bakoitzeko.",
                     "es verte ahí.", "zu han ikustea da.", "Gracias por estos 20 años.",
                     "Eskerrik asko 20 urte hauengatik."):
            y += 40

    d.line([(W / 2 - 90, y + 30), (W / 2 + 90, y + 30)], fill=VERDE, width=4)
    d.text((26, H - 40), "Malato · 2006. urtetik zurekin",
           font=ImageFont.truetype(ROUND, 26), fill=(180, 175, 160))

    NOMBRES = {"CASTELLANO": "CARTA-INVITACION-CASTELLANO.jpg",
               "EUSKERA": "GUTUNA-GONBITA-EUSKERA.jpg"}
    salida = NOMBRES[idioma]
    img.save(salida, "JPEG", quality=94, optimize=True)
    print(f"  {salida} · {round(os.path.getsize(salida)/1024,0)} KB")
    img.resize((W // 3, H // 3), Image.LANCZOS).save(f".tmp-cart/CARTA-{idioma}-vista.png")


for idioma in ("CASTELLANO", "EUSKERA"):
    una(idioma)
print("  hechas las dos")
