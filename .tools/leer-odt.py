"""Extrae el texto de un .odt conservando la estructura de la lista.

Recorre TODOS los parrafos y titulos en orden de documento e indenta segun
cuantos 'list-item' tiene por encima. Es la forma robusta: no depende de
adivinar donde esta el contenido.
"""
import sys
import zipfile
from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
RUTA = sys.argv[1]

with zipfile.ZipFile(RUTA) as z:
    xml = z.read("content.xml")

raiz = etree.fromstring(xml)
cuerpo = raiz.find(".//{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body/"
                   "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text")

print("=" * 78)
print("TEXTO DEL DOCUMENTO (indentado segun su nivel de lista)")
print("=" * 78)

pendiente_fin_tabla = False
for el in cuerpo.iter():
    tag = etree.QName(el).localname

    if tag == "table":
        filas = el.findall("{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row")
        print(f"\n  [TABLA de {len(filas)} filas]")
        for f in filas:
            celdas = []
            for c in f.findall("{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell"):
                rep = int(c.get("{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
                                "number-columns-repeated", "1"))
                t = " ".join("".join(p.itertext()).strip()
                             for p in c.findall("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"))
                celdas.extend([t.strip()] * min(rep, 6))
            while celdas and celdas[-1] == "":
                celdas.pop()
            if any(celdas):
                print("    | " + " | ".join(celdas))
        pendiente_fin_tabla = True
        continue

    if tag in ("p", "h"):
        # Saltar los parrafos que ya se han impreso como parte de una tabla
        ancestros = [etree.QName(a).localname for a in el.iterancestors()]
        if "table-cell" in ancestros:
            continue
        texto = "".join(el.itertext()).strip()
        if not texto:
            continue
        nivel = sum(1 for a in ancestros if a == "list-item")
        prefijo = "  " * nivel
        marca = "# " if tag == "h" else ""
        print(f"{prefijo}{marca}{texto}")
        pendiente_fin_tabla = False
