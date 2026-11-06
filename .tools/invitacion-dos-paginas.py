"""La invitación en UN documento de dos páginas: euskera y castellano.

Título arriba en las dos: «Invitación / Gonbidapena».
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

W, H = 1080, 1920
PAPEL = (252, 250, 243)
PAPEL_2 = (244, 240, 228)
TINTA = (48, 44, 38)
VERDE = (30, 154, 69)
GRIS = (150, 145, 130)

COMIC = "C:\\Windows\\Fonts\\comicbd.ttf"
ROUND = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
MARCA = r"C:\Users\Usuario\Desktop\APP Malato\docs\marca"

PAGINAS = {
    "EUSKERA": {
        "titulo": "20 urte.",
        "lineas": [
            ("Ez dugu sinesten.", 52, 0),
            ("Igande honetan, azaroak 8,", 52, 0),
            ("10:00etatik 14:30era,", 52, 0),
            ("Malaton zain gaituzu.", 52, 40),
            ("Tarta, palmeritak, batukada", 52, 0),
            ("eta papeleta bat erosketa bakoitzeko.", 50, 40),
            ("Baina benetan nahi duguna", 56, "comic"),
            ("zu han ikustea da.", 56, 40),
            ("Eskerrik asko 20 urte hauengatik.", 48, 0),
            ("Malatoko taldea", 50, 0),
        ],
    },
    "CASTELLANO": {
        "titulo": "20 años.",
        "lineas": [
            ("No nos lo creemos ni nosotros.", 52, 0),
            ("Este domingo 8 de noviembre,", 52, 0),
            ("de 10:00 a 14:30,", 52, 0),
            ("te esperamos en Malato.", 52, 40),
            ("Habrá tarta, palmeritas, batukada", 52, 0),
            ("y una papeleta por cada compra.", 52, 40),
            ("Pero lo que de verdad queremos", 56, "comic"),
            ("es verte ahí.", 56, 40),
            ("Gracias por estos 20 años.", 50, 0),
            ("El equipo de Malato", 50, 0),
        ],
    },
}


def pagina(idioma, numero):
    datos = PAGINAS[idioma]
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
    ImageDraw.Draw(halo).ellipse([W / 2 - 520, H * 0.36 - 520, W / 2 + 520, H * 0.36 + 520], fill=60)
    img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(190)))

    # el árbol
    arbol = Image.open(os.path.join(MARCA, "logo-o-verde.png")).convert("RGBA")
    al = 120
    arbol = arbol.resize((al, int(al * arbol.size[1] / arbol.size[0])), Image.LANCZOS)
    img.paste(arbol, ((W - al) // 2, 80), arbol)

    d = ImageDraw.Draw(img)

    # el título del documento, igual en las dos páginas
    ft_titulo = ImageFont.truetype(ROUND, 40)
    w = d.textlength("Invitación / Gonbidapena", font=ft_titulo)
    d.text(((W - w) / 2, 232), "Invitación / Gonbidapena", font=ft_titulo, fill=GRIS)
    d.line([(W / 2 - 90, 292), (W / 2 + 90, 292)], fill=GRIS, width=2)

    # el título del idioma
    ft_idioma = ImageFont.truetype(ROUND, 84)
    w = d.textlength(datos["titulo"], font=ft_idioma)
    d.text(((W - w) / 2, 340), datos["titulo"], font=ft_idioma, fill=VERDE)

    y = 340 + int(84 * 1.42) + 30
    for texto, tam, extra in datos["lineas"]:
        ruta = COMIC if extra == "comic" else ROUND
        ft = ImageFont.truetype(ruta, tam)
        w = d.textlength(texto, font=ft)
        d.text(((W - w) / 2, y), texto, font=ft, fill=TINTA)
        y += int(tam * 1.42) + (extra if isinstance(extra, int) else 0)

    d.line([(W / 2 - 90, y + 26), (W / 2 + 90, y + 26)], fill=VERDE, width=4)
    d.text((26, H - 40), "Malato · 2006. urtetik zurekin",
           font=ImageFont.truetype(ROUND, 26), fill=(180, 175, 160))
    # el número de página
    d.text((W - 90, H - 40), str(numero), font=ImageFont.truetype(ROUND, 26), fill=(180, 175, 160))
    return img


hojas = [pagina("EUSKERA", 1), pagina("CASTELLANO", 2)]

# un solo documento de dos páginas
hojas[0].save("INVITACION-GONBIDAPENA.pdf", "PDF", resolution=300.0, save_all=True, append_images=hojas[1:])
print(f"  INVITACION-GONBIDAPENA.pdf · {round(os.path.getsize('INVITACION-GONBIDAPENA.pdf')/1024,0)} KB · 2 páginas")

# y las dos imágenes sueltas, por si las quieres mandar
for i, (hoja, nombre) in enumerate(zip(hojas, ("GUTUNA-GONBITA-EUSKERA.jpg", "CARTA-INVITACION-CASTELLANO.jpg")), 1):
    hoja.save(nombre, "JPEG", quality=94, optimize=True)
    print(f"  {nombre} · {round(os.path.getsize(nombre)/1024,0)} KB")
    hoja.resize((W // 3, H // 3), Image.LANCZOS).save(f".tmp-cart/PAGINA-{i}.png")
