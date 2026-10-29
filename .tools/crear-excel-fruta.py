"""Excel de fruta y verdura por familias, con desplegable.

Solo se clasifica lo que está claro. Lo dudoso se deja SIN familia, para que lo
complete la propiedad. El CI va marcado como interno.
"""
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

sys.stdout.reconfigure(encoding="utf-8")

VERDE = "2EC258"
VERDE_OSC = "1E9A45"
SUAVE = "EFFAF2"
AMARILLO = "FFF8E6"
CABECERA = PatternFill("solid", fgColor=VERDE_OSC)
TITULO = PatternFill("solid", fgColor=VERDE)
SITIO_FILL = PatternFill("solid", fgColor=AMARILLO)
BORDE = Border(*[Side(style="thin", color="D6EDDD")] * 4)

FAMILIAS = ["Fruta", "Verdura", "Embolsado", "Ensaladas Preparadas", "Legumbres", "Varios"]

COLORES_FAMILIA = {
    "Fruta": ("E8F5D0", "4A6B15"),
    "Verdura": ("D6EDDD", "1E6B3A"),
    "Embolsado": ("FDE7C8", "8A4B00"),
    "Ensaladas Preparadas": ("D8EAF7", "12496E"),
    "Legumbres": ("EADCF5", "5B2D8E"),
    "Varios": ("EAEAEA", "4A4A4A"),
}

# (ci, producto, familia)  · familia None = no lo tengo claro, lo deja la propiedad
DATOS = [
    # ---- FRUTA
    ("960036", "PLATANO CANARIAS", "Fruta"),
    ("960030", "MELON BOLLO", "Fruta"),
    ("961297", "SANDIA BOLLO", "Fruta"),
    ("961339", "POMELO", "Fruta"),
    ("960031", "NARANJA BOLLO", "Fruta"),
    ("960972", "NARANJA ZUMO MALLA", "Fruta"),
    ("960156", "NARANJA ZUMO BARATA", "Fruta"),
    ("960020", "CLEMENTINA BOLLO", "Fruta"),
    ("961268", "CLEMENTINA RAMA BOLLO", "Fruta"),
    ("961131", "MANDARINA BARATA", "Fruta"),
    ("960024", "LIMON", "Fruta"),
    ("961070", "MANZANA VERDE G SMITH", "Fruta"),
    ("960028", "MANZANA ROYAL GALA", "Fruta"),
    ("960025", "MANZANA FUJI", "Fruta"),
    ("960027", "MANZANA KANZI", "Fruta"),
    ("960017", "MANZANA GOLDEN", "Fruta"),
    ("961541", "MANZANA JOYA ROJA", "Fruta"),
    ("", "MANZANA CHANTECLER", "Fruta"),
    ("961459", "MANZANA PINK LADY", "Fruta"),
    ("960026", "REINETA PARDA", "Fruta"),
    ("960034", "PERA CONFERENCIA", "Fruta"),
    ("960151", "PERA DUQUESA", "Fruta"),
    ("960290", "PERA BLANQUILLA", "Fruta"),
    ("", "PERA CHAMPION", "Fruta"),
    ("961179", "PERA COMPOTA", "Fruta"),
    ("961477", "PERA QTEE", "Fruta"),
    ("960022", "KAKI", "Fruta"),
    ("960019", "CHIRIMOYA", "Fruta"),
    ("960018", "AGUACATES", "Fruta"),
    ("960035", "PIÑA DEL MONTE", "Fruta"),
    ("960038", "UVA MORADA", "Fruta"),
    ("960037", "UVA BLANCA", "Fruta"),
    ("961309", "CEREZAS", "Fruta"),
    ("960033", "PARAGUAYOS", "Fruta"),
    ("960021", "GRANADA", "Fruta"),
    ("961141", "FRESAS", "Fruta"),
    ("960722", "FRESAS BLANCAS", "Fruta"),
    ("961285", "MELOCOTON ROJO", "Fruta"),
    ("960029", "MELOCOTON AMARILLO", "Fruta"),
    ("960032", "NECTARINA AMARILLA", "Fruta"),
    ("961284", "NECTARINA BLANCA", "Fruta"),
    ("961308", "NECTARINA BARATA", "Fruta"),
    ("960968", "CIRUELA ROJA", "Fruta"),
    ("", "CIRUELA AMARILLA", "Fruta"),
    ("960080", "CIRUELA CLAUDIA", "Fruta"),
    ("961286", "ALBARICOQUES", "Fruta"),
    ("", "KIWI", "Fruta"),
    ("960050", "HIGOS CUELLO DAMA", "Fruta"),
    ("", "ARANDANOS / FRAMBUESAS", "Fruta"),
    # ---- VERDURA
    ("960928", "BROCOLI", "Verdura"),
    ("", "ROMANESCU", "Verdura"),
    ("960926", "AJO A PESO", "Verdura"),
    ("960933", "COLIFLOR", "Verdura"),
    ("960941", "BERZA", "Verdura"),
    ("960936", "PUERRO", "Verdura"),
    ("960958", "ZANAHORIA", "Verdura"),
    ("960935", "CEBOLLETAS", "Verdura"),
    ("960940", "PIMIENTO VERDE", "Verdura"),
    ("960939", "PIMIENTO ROJO", "Verdura"),
    ("960945", "VAINAS", "Verdura"),
    ("960893", "TOMATE RAF", "Verdura"),
    ("960943", "TOMATE RAMA", "Verdura"),
    ("960946", "AJOS TIERNOS", "Verdura"),
    ("960952", "ESPARRAGOS TIERNOS", "Verdura"),
    ("960947", "APIO", "Verdura"),
    ("960951", "ENDIVIAS", "Verdura"),
    ("", "ESCAROLA", "Verdura"),
    ("804343", "CORAZONES LECHUGA", "Verdura"),
    ("960931", "ICEBERG", "Verdura"),
    # ---- EMBOLSADO
    ("960948", "AJO EN BOLSA", "Embolsado"),
    ("960953", "PIMIENTO DEL PAIS BOLSA", "Embolsado"),
    # ---- ENSALADAS PREPARADAS
    ("394555", "GOURMET", "Ensaladas Preparadas"),
    ("960973", "4 ESTACIONES", "Ensaladas Preparadas"),
    ("394587", "CESAR", "Ensaladas Preparadas"),
    ("960975", "FLORETTE INTEGRAL", "Ensaladas Preparadas"),
    ("394648", "FLORETTE COMPLETA GOURMET", "Ensaladas Preparadas"),
    # ---- LEGUMBRES
    ("960039", "ALUBIA BLANCA", "Legumbres"),
    ("960040", "ALUBIA (¿SABROSANA?)", "Legumbres"),
    ("960041", "GARBANZO PEDROSILLANO", "Legumbres"),
    ("960042", "LENTEJA PARDINA", "Legumbres"),
    # ---- VARIOS
    ("961208", "NUECES", "Varios"),
    ("960969", "CASTAÑAS", "Varios"),
    # ---- DUDOSOS: sin familia, para que los complete la propiedad
    ("960949", "CHAMPIS BANDEJA", None),
    ("960956", "SETAS BANDEJA", None),
    ("960957", "TOMATE CHERRY", None),
    ("960974", "CANONIGOS", None),
    ("", "HIERBABUENA", None),
    ("", "CEBOLLINO", None),
    ("961051", "CARNE PIMIENTO CHORICERO", None),
    ("960932", "HOJA (¿HOJA DE ROBLE?)", None),
    ("", "¿PIMIENTO…? (no se lee)", None),
]

# Cuántos quedan sin clasificar
sin_clasificar = sum(1 for _, _, f in DATOS if f is None)
sin_ci = sum(1 for c, _, _ in DATOS if not c)

wb = Workbook()
ws = wb.active
ws.title = "Clasificar"

ws["A1"] = "FRUTA Y VERDURA · POR FAMILIAS"
ws["A1"].font = Font(bold=True, size=16, color="FFFFFF")
ws["A1"].fill = TITULO
ws.merge_cells("A1:D1")
ws.row_dimensions[1].height = 30

ws["A2"] = ("La columna FAMILIA tiene desplegable. Lo que ya está puesto es lo que tengo claro; "
            "lo que está en blanco es lo que no me atrevo a decidir. El CI es interno: "
            "sólo gerencia y coordinadoras.")
ws["A2"].font = Font(size=10, italic=True, color="5E6E63")
ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
ws.merge_cells("A2:D2")
ws.row_dimensions[2].height = 32

for i, h in enumerate(["CI\n(interno)", "PRODUCTO", "FAMILIA", "NOTAS"], 1):
    cel = ws.cell(row=4, column=i, value=h)
    cel.font = Font(bold=True, color="FFFFFF", size=11)
    cel.fill = PatternFill("solid", fgColor="D97706" if i == 3 else VERDE_OSC)
    cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cel.border = BORDE
ws.row_dimensions[4].height = 32

r = 5
for ci, prod, fam in DATOS:
    c = ws.cell(row=r, column=1, value=ci or "¿?")
    c.alignment = Alignment(horizontal="center")
    c.font = Font(size=10, color="5E6E63" if ci else "B3261E")
    c.border = BORDE
    c2 = ws.cell(row=r, column=2, value=prod)
    c2.border = BORDE
    c3 = ws.cell(row=r, column=3, value=fam or "")
    c3.fill = SITIO_FILL
    c3.border = BORDE
    c3.alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=4).fill = SITIO_FILL
    ws.cell(row=r, column=4).border = BORDE
    r += 1
ULTIMA = r - 1

# --- desplegable de familia
dv = DataValidation(type="list", formula1='"' + ",".join(FAMILIAS) + '"',
                    allow_blank=True, showDropDown=False)
dv.error = "Elige una de las seis familias"
dv.errorTitle = "Familia no válida"
ws.add_data_validation(dv)
dv.add(f"C5:C{ULTIMA}")

# --- color por familia
for fam, (fondo, texto) in COLORES_FAMILIA.items():
    ws.conditional_formatting.add(
        f"C5:C{ULTIMA}",
        CellIsRule(operator="equal", formula=[f'"{fam}"'],
                   fill=PatternFill("solid", fgColor=fondo),
                   font=Font(bold=True, color=texto)))

ws.column_dimensions["A"].width = 13
ws.column_dimensions["B"].width = 34
ws.column_dimensions["C"].width = 22
ws.column_dimensions["D"].width = 48
ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:D{ULTIMA}"

# --- resumen
wr = wb.create_sheet("Resumen")
wr["A1"] = "CUÁNTOS HAY DE CADA FAMILIA"
wr["A1"].font = Font(bold=True, size=15, color="FFFFFF")
wr["A1"].fill = TITULO
wr.merge_cells("A1:B1")
wr.row_dimensions[1].height = 28

wr["A3"] = "Familia"
wr["B3"] = "Productos"
for c in ("A3", "B3"):
    wr[c].font = Font(bold=True, color="FFFFFF")
    wr[c].fill = CABECERA
    wr[c].border = BORDE

for i, fam in enumerate(FAMILIAS, 4):
    wr.cell(row=i, column=1, value=fam).font = Font(bold=True)
    wr.cell(row=i, column=2, value=f'=COUNTIF(Clasificar!$C$5:$C${ULTIMA},$A{i})')
    wr.cell(row=i, column=1).border = BORDE
    wr.cell(row=i, column=2).border = BORDE

fila = 4 + len(FAMILIAS)
wr.cell(row=fila, column=1, value="Sin clasificar").font = Font(bold=True, color="B3261E")
wr.cell(row=fila, column=2, value=f'=COUNTIF(Clasificar!$C$5:$C${ULTIMA},"")')
wr.cell(row=fila, column=1).border = BORDE
wr.cell(row=fila, column=2).border = BORDE
wr.cell(row=fila + 1, column=1, value="TOTAL").font = Font(bold=True)
wr.cell(row=fila + 1, column=2, value=f"=COUNTA(Clasificar!$B$5:$B${ULTIMA})")
wr.cell(row=fila + 1, column=1).border = BORDE
wr.cell(row=fila + 1, column=2).border = BORDE
wr.column_dimensions["A"].width = 26
wr.column_dimensions["B"].width = 13

# --- cómo usarlo
wi = wb.create_sheet("Cómo usarlo", 0)
wi["A1"] = "CÓMO USARLO"
wi["A1"].font = Font(bold=True, size=16, color="FFFFFF")
wi["A1"].fill = TITULO
wi.merge_cells("A1:B1")
wi.row_dimensions[1].height = 30

PASOS = [
    ("De dónde sale", "De las dos fotos que has mandado. Las he ampliado y les he pasado "
                      "el OCR de Windows, que no siempre acierta."),
    ("El CI", "Es interno: sólo gerencia y coordinadoras. Servirá para los pedidos. "
              "Los que van con «¿?» no los he podido leer."),
    ("Lo que ya está clasificado", "Lo que tengo claro. Son 84 productos."),
    ("Lo que está en blanco", f"Lo que no me atrevo a decidir: {sin_clasificar} productos. "
                              "Dime en qué familia van con el desplegable."),
    ("Los dudosos, y por qué", ""),
    ("· CHAMPIS y SETAS BANDEJA", "¿Embolsado (van en bandeja) o Verdura?"),
    ("· TOMATE CHERRY", "¿Verdura o Embolsado?"),
    ("· CANONIGOS", "Lo he leído «CAN NICOS». Es una hoja, pero estaba en la lista de "
                    "ensaladas preparadas: ¿Verdura o Ensaladas Preparadas?"),
    ("· HIERBABUENA y CEBOLLINO", "¿Verdura (hierbas frescas) o Varios?"),
    ("· CARNE PIMIENTO CHORICERO", "No sé qué es. ¿Varios?"),
    ("· HOJA", "Lo he leído «HOJA» a secas. ¿Hoja de roble?"),
    ("", ""),
    ("OJO", "El OCR es una máquina leyendo una foto. Puede haber fallos de escritura "
            "en los nombres: «PIÑA» lo leí «PINA», y alguna tilde se ha perdido. "
            "Si ves un nombre mal escrito, corrígelo sin miedo."),
]
r = 3
for a, b in PASOS:
    ca = wi.cell(row=r, column=1, value=a)
    cb = wi.cell(row=r, column=2, value=b)
    cb.alignment = Alignment(wrap_text=True, vertical="top")
    ca.font = Font(bold=True, size=10,
                   color="B3261E" if a in ("OJO", "Los dudosos, y por qué") else "1E9A45")
    r += 1
wi.column_dimensions["A"].width = 30
wi.column_dimensions["B"].width = 92

wb.move_sheet("Cómo usarlo", offset=-(len(wb.sheetnames) - 1))
wb.save("docs/fruta-verdura-familias.xlsx")
print("  escrito docs/fruta-verdura-familias.xlsx")
print(f"  productos: {len(DATOS)}  ·  clasificados: {len(DATOS)-sin_clasificar}  ·  "
      f"sin clasificar: {sin_clasificar}  ·  sin CI: {sin_ci}")
