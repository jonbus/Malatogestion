"""Las 500 papeletas del aniversario, en A4, para imprimir y cortar.

3 columnas x 5 filas = 15 por hoja -> 34 hojas.
Se barajan para que dos papeletas seguidas no sean iguales.
"""
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")

PREMIOS = [
    ("Mini Nevera Portátil Rígida", 1),
    ("Calendario 2027 Tudis", 9),
    ("Delantal azul Hellmann's", 4),
    ("Toalla Frigo", 3),
    ("Mini Nevera Flexible Roja Frigo", 4),
    ("Bolígrafo Tudis", 7),
    ("Peluche Bimbito", 10),
    ("Botella Plástico Negra Pepsi", 30),
    ("Flor Ambientador", 16),
    ("Vaso Cristal Infusión con Pajita", 5),
    ("Mini Nevera Alvalle", 10),
    ("Cantimplora Cristal Argal", 6),
    ("Mini Tabla Madera para Aperitivo", 6),
    ("Bolsa XL Negra Viaje Bocatta Club", 2),
]

TOTAL = 500
GRACIAS = "Hoy no ha sido."

papeletas = []
for nombre, cuantas in PREMIOS:
    papeletas += [nombre] * cuantas
premios = len(papeletas)
papeletas += [None] * (TOTAL - premios)

random.seed(2026)          # así siempre salen igual: se puede volver a imprimir igual
random.shuffle(papeletas)

print(f"  premios: {premios}")
print(f"  «{GRACIAS}»: {TOTAL - premios}")
print(f"  total: {len(papeletas)}")

POR_HOJA = 15              # 3 columnas x 5 filas
hojas = (len(papeletas) + POR_HOJA - 1) // POR_HOJA
print(f"  hojas: {hojas}")


def celda(numero, premio):
    if premio:
        centro = (f'<div class="et">¡ENHORABUENA!</div>'
                  f'<div class="premio">{premio}</div>')
    else:
        centro = (f'<div class="et no">HOY NO HA SIDO.</div>'
                  f'<div class="gracias">Gracias por acompañarnos<br>en nuestro aniversario.</div>')
    clase = "papeleta gana" if premio else "papeleta"
    return (f'<div class="{clase}">'
            f'<div class="cab">MALATO · ANIVERSARIO</div>'
            f'<div class="cuerpo">{centro}</div>'
            f'<div class="num">nº {numero}</div>'
            f'</div>')


partes = []
for h in range(hojas):
    trozo = papeletas[h * POR_HOJA:(h + 1) * POR_HOJA]
    celdas = "".join(celda(h * POR_HOJA + i + 1, p) for i, p in enumerate(trozo))
    # se rellena la última hoja si queda corta
    for _ in range(POR_HOJA - len(trozo)):
        celdas += '<div class="papeleta vacia"></div>'
    partes.append(f'<div class="hoja"><div class="rejilla">{celdas}</div></div>')

HTML = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Papeletas · Aniversario Malato</title>
<style>
  @page { size: A4; margin: 7mm; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: "DejaVu Sans", Arial, sans-serif; }
  .hoja { width: 196mm; height: 283mm; page-break-after: always; }
  .hoja:last-child { page-break-after: auto; }
  .rejilla { display: grid; grid-template-columns: repeat(3, 1fr);
             grid-template-rows: repeat(5, 1fr); width: 196mm; height: 283mm; }
  .papeleta { border: 0.3mm dashed #9aa3a0; padding: 3mm 3mm 5mm 3mm;
              display: flex; flex-direction: column; position: relative;
              overflow: hidden; }
  .papeleta.gana { background: #FFF8E6; border-color: #C9A227; }
  .cab { font-size: 6.4pt; letter-spacing: .12em; color: #6b7a75;
         text-transform: uppercase; }
  .cuerpo { flex: 1 1 auto; display: flex; flex-direction: column;
            align-items: center; justify-content: center; text-align: center; }
  .et { font-size: 8pt; font-weight: 700; letter-spacing: .06em;
        color: #B07B12; margin-bottom: 1.5mm; }
  .et.no { color: #6b7a75; }
  .premio { font-size: 12pt; font-weight: 700; line-height: 1.15; color: #1d2b26; }
  .gracias { font-size: 9pt; line-height: 1.3; color: #1d2b26; }
  .num { position: absolute; bottom: 1.2mm; right: 3mm; font-size: 6pt; color: #9aa3a0; }
  .vacia { border: none; }
</style></head><body>
""" + "".join(partes) + "</body></html>"

salida = "PAPELETAS-ANIVERSARIO.html"
with open(salida, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"  escrito {salida}")
