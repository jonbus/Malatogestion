"""El cartel de los premios, en euskera.

Los nombres de marca se quedan como están; lo que se traduce es el producto.
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

origen = open(r".tools\carteles2.py", encoding="utf-8").read()

# los premios, en euskera
VIEJO = '''PREMIOS = [
    ("Botella Plástico Negra Pepsi", 30),
    ("Flor Ambientador", 16),
    ("Peluche Bimbito", 10),
    ("Mini Nevera Alvalle", 10),
    ("Calendario 2027 Tudis", 9),
    ("Bolígrafo Tudis", 7),
    ("Cantimplora Cristal Argal", 6),
    ("Mini Tabla Madera para Aperitivo", 6),
    ("Vaso Cristal Infusión con Pajita", 5),
    ("Delantal azul Hellmann's", 4),
    ("Mini Nevera Flexible Roja Frigo", 4),
    ("Toalla Frigo", 3),
    ("Bolsa XL Negra Viaje Bocatta Club", 2),
    ("Mini Nevera Portátil Rígida", 1),
]'''

NUEVO = '''PREMIOS = [
    ("Pepsi botila beltz plastikoa", 30),
    ("Lore usain-tanta", 16),
    ("Bimbito peluxea", 10),
    ("Mini hozkailua Alvalle", 10),
    ("2027ko egutegia Tudis", 9),
    ("Tudis boligrafoa", 7),
    ("Argal kristalezko kantinplora", 6),
    ("Aperitiborako zurezko oholtxoa", 6),
    ("Kristalezko infusio basoa kanutoarekin", 5),
    ("Hellmann's blusa urdina", 4),
    ("Mini hozkailu tolesgarri gorria Frigo", 4),
    ("Frigo eskuoihala", 3),
    ("Bocatta Club bidaia-poltsa beltz XL", 2),
    ("Mini hozkailu eramangarri zurruna", 1),
]'''

if VIEJO not in origen:
    print("  NO ENCONTRADO la lista de premios")
    sys.exit(1)

t = origen.replace(VIEJO, NUEVO, 1)

# los textos de alrededor
t = t.replace('"ESTOS SON LOS PREMIOS"', '"HAUEK DIRA SARIAK"')
t = t.replace('"113 PREMIOS EN TOTAL"', '"GUZTIRA 113 SARIA"')
t = t.replace('"Cambia tu ticket por una papeleta."', '"Aldakatu zure tiketa papeletagatik."')
t = t.replace('"2006. urtetik ZUREKIN"', '"2006. urtetik ZUREKIN"')   # el lema ya está en euskera
t = t.replace('"supermercado"', '"supermerkatua"')

# el nombre del fichero
t = t.replace('CARTEL-PREMIOS.pdf', 'Kartel Sariak.pdf')

open(r".tools\carteles-premios-eu.py", "w", encoding="utf-8").write(t)
print("  escrito .tools/carteles-premios-eu.py")

# se quita el cartel de la urna de este script: aquí solo los premios
lineas = t.split("\n")
salida = [l for l in lineas if "CARTEL-URNA" not in l]
open(r".tools\carteles-premios-eu.py", "w", encoding="utf-8").write("\n".join(salida))
print("  y sin tocar el de la urna")
