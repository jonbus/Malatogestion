"""En el cartel de euskera, «supermercado» pasa a «supermerkatua».

La palabra está dentro del logotipo, así que se tapa esa franja con el color
del fondo y se escribe la nueva encima, con la misma colocación.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools\cartel-color.py"
t = open(p, encoding="utf-8").read()

viejo = """    logo = logo.resize((al, la), Image.LANCZOS)
    # el blanco del logotipo se vuelve transparente, para que se vea el fondo
    mascara = logo.convert("L").point(lambda p: 255 if p < 245 else 0)
    img.paste(logo, ((W - al) // 2, 32), mascara)"""

nuevo = """    logo = logo.resize((al, la), Image.LANCZOS)
    # el blanco del logotipo se vuelve transparente, para que se vea el fondo
    mascara = logo.convert("L").point(lambda p: 255 if p < 245 else 0)
    img.paste(logo, ((W - al) // 2, 32), mascara)

    # en euskera, «supermercado» pasa a «supermerkatua»
    if idioma == "eu":
        arriba = 32
        franja = int(la * 0.38)
        d.rectangle([(W - al) // 2 - 4, arriba - 6, (W + al) // 2 + 4, arriba + franja],
                    fill=CREMA)
        f_txt = f("C:\\\\Windows\\\\Fonts\\\\arial.ttf", 66)
        ancho_txt = d.textlength("supermerkatua", font=f_txt)
        d.text(((W - ancho_txt) / 2, arriba + 6), "supermerkatua",
               font=f_txt, fill=(97, 99, 96))"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(viejo, nuevo, 1)
t = t.replace("v-2026-10-26-88", "v-2026-10-26-89")
open(p, "w", encoding="utf-8").write(t)
print("  ok  «supermerkatua» en el cartel de euskera")
