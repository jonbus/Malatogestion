"""El cartel de la urna, en euskera.

Se cambian los textos del dibujo y se pone «supermerkatua» tapando la franja
del logotipo, como en los demás carteles.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

origen = open(r".tools\cartel-urna2.py", encoding="utf-8").read()

CAMPOS = [
    ('"CAMBIA TU TICKET"', '"ALDAKATU ZURE TIKETA"'),
    ('"POR UNA PAPELETA"', '"PAPELETAGATIK"'),
    ('"TE PUEDE TOCAR"', '"ZUREA IZAN DAITEKE"'),
    ('"PREMIO"', '"SARIA"'),
    ('"¡MUCHA SUERTE!"', '"ZORTE ON!"'),
    ('"Mete la mano en la urna."', '"Sartu eskua urnan."'),
    ('"Si sale premio, te lo llevas."', '"Saria ateratzen bazaizu, zurea da."'),
    ('"Una compra, una papeleta."', '"Erosketa bat, papeleta bat."'),
    ('"Gracias por estos 20 años a tu lado."', '"Eskerrik asko 20 urte hauetan gurekin egoteagatik."'),
    ('"20 ANIVERSARIO"', '"20 URTEURRENA"'),
    ('CARTEL-URNA.pdf', 'Kartel Urna.pdf'),
]

t = origen
for viejo, nuevo in CAMPOS:
    if viejo not in t:
        print(f"    OJO, no encontrado: {viejo}")
    t = t.replace(viejo, nuevo)

# «supermerkatua» encima del logotipo, tapando el castellano
ANCLA = 'img.paste(logo, ((W - ancho_logo) // 2, 32))'
if ANCLA in t:
    t = t.replace(ANCLA, '''img.paste(logo, ((W - ancho_logo) // 2, 32))
# el logotipo dice «supermercado»: en euskera, «supermerkatua»
d.rectangle([(W - ancho_logo) // 2 - 4, 26,
             (W + ancho_logo) // 2 + 4, 32 + int(alto_logo * 0.38)], fill=BLANCO)
_f = ImageFont.truetype("C:\\\\Windows\\\\Fonts\\\\arial.ttf", 66)
_an = d.textlength("supermerkatua", font=_f)
d.text(((W - _an) / 2, 34), "supermerkatua", font=_f, fill=(97, 99, 96))''', 1)
    print("    ok  supermerkatua")
else:
    print("    OJO, no encontrado el sitio del logotipo")

open(r".tools\cartel-urna-eu.py", "w", encoding="utf-8").write(t)
print("  escrito .tools/cartel-urna-eu.py")
