"""El manual del día, en Word, para que se pueda abrir e imprimir sin líos."""
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Cm

sys.stdout.reconfigure(encoding="utf-8")

doc = Document()

# márgenes y letra base
for s in doc.sections:
    s.top_margin = Cm(1.8)
    s.bottom_margin = Cm(1.8)
    s.left_margin = Cm(1.8)
    s.right_margin = Cm(1.8)

estilo = doc.styles["Normal"]
estilo.font.name = "Arial"
estilo.font.size = Pt(10.5)


def titulo(texto, tam=26):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(texto)
    r.bold = True
    r.font.size = Pt(tam)
    return p


def sub(texto, tam=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(texto)
    r.font.size = Pt(tam)
    return p


def h1(texto):
    doc.add_page_break()
    p = doc.add_paragraph()
    r = p.add_run(texto)
    r.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0x1E, 0x7A, 0x3C)
    return p


def h2(texto):
    p = doc.add_paragraph()
    r = p.add_run(texto)
    r.bold = True
    r.font.size = Pt(12)
    return p


def bullet(texto):
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(texto)
    return p


def tabla(filas, cabecera=None, anchos=None):
    n = len(filas[0])
    t = doc.add_table(rows=0, cols=n)
    t.style = "Light Grid Accent 1"
    if cabecera:
        c = t.add_row().cells
        for i, v in enumerate(cabecera):
            c[i].text = ""
            r = c[i].paragraphs[0].add_run(v)
            r.bold = True
    for fila in filas:
        c = t.add_row().cells
        for i, v in enumerate(fila):
            c[i].text = str(v)
    return t


# ------------------------------------------------------------------ portada
titulo("20 ANIVERSARIO")
sub("supermercado malato · 2006. urtetik ZUREKIN", 13)
sub("")
sub("DOMINGO 8 DE NOVIEMBRE DE 2026  ·  de 10:00 a 14:30", 13)
sub("")
sub("Se lee la víspera, se tacha lo que se hace,", 11)
sub("y el que llega nuevo lo puede seguir solo.", 11)

# ------------------------------------------------------------------ 1
h1("1 · Lo que hay que hacer ANTES")
tabla([
    ["Jueves 5", "Montar los globos de estructura (arcos, columnas). Dejarlos en el almacén."],
    ["Viernes 6", "Los globos que se ven de cerca. La carpa, si se ha decidido."],
    ["Sábado 7", "Dejarlo TODO listo. Nada nuevo. Las bolsas y los premios juntos. Los platos del lunch, preparados. Y confirmar el ALTAVOZ con la batukada."],
], cabecera=["Cuándo", "Qué"])
doc.add_paragraph()
p = doc.add_paragraph()
r = p.add_run("Ya está hecho: las 500 papeletas, cortadas y dobladas. No hay que recortar nada ese día.")
r.bold = True

# ------------------------------------------------------------------ 2
h1("2 · El domingo, hora a hora")
tabla([
    ["7:00", "Llegamos nosotras."],
    ["7:30", "Llegan LAS PALMERAS."],
    ["8:00", "El LUNCH de la batukada, en los platos que se dejaron el sábado. Todo antes de abrir."],
    ["9:00", "Subir y colocar los globos. Y hacer o reservar sitio en el parking para la batukada."],
    ["9:00", "LA MESA DE LA TARTA, en el orden de la página siguiente."],
    ["9:30", "La urna, los carteles, las bolsas, los premios, la papelera y la cajita."],
    ["10:00", "ABRIR. Los dos niños en la puerta. Y llega EL FOTÓGRAFO."],
    ["10:00", "Empieza EL CANJE."],
    ["11:00", "La BATUKADA, con el lunch ya puesto."],
    ["11:00", "Visitar a ROSA y llevarle unas pastas."],
    ["11:30", "LA FOTO DE TODO EL EQUIPO, delante de la tarta."],
    ["13:00", "Los regalos a la batukada, al acabar de tocar."],
    ["14:30", "CERRAR. Recoger. Contar la cajita: tienen que ser 113."],
], cabecera=["Hora", "Qué"])

# ------------------------------------------------------------------ 3
h1("3 · La mesa de la tarta — EN ESTE ORDEN")
p = doc.add_paragraph()
r = p.add_run("El orden importa: si se pone el mantel después, hay que levantar la tarta.")
r.bold = True
for t in [
    "El sitio — que se vea desde la calle y que no estorbe.",
    "Los caballetes — que los cuatro pies apoyen. Si baila, se calza el caballete, no el tablón.",
    "El mantel — sin arrugas, y que caiga igual por los cuatro lados.",
    "La tarta — es de porexpan: no se corta, no se reparte y no se come.",
    "Los lazos y las letras «20 urteurrena» — que se lean desde la calle.",
    "Las palmeritas alrededor, y las que no quepan aparte y tapadas.",
    "Las gominolas — un plato hondo, y que no le dé el sol.",
    "Las PIRULETAS.",
    "La urna, los carteles, las bolsas y los premios.",
]:
    bullet(t)

# ------------------------------------------------------------------ 4
h1("4 · El lunch de la batukada")
p = doc.add_paragraph()
r = p.add_run("Es SOLO para la batukada. Aparte, no en la mesa de la tarta.")
r.bold = True
for t in ["jamón", "cabecero", "pastas", "aceitunas", "patatas", "pan", "queso"]:
    bullet(t)
doc.add_paragraph("En los platos que se dejaron listos el sábado. Y las botellas negras de agua de Pepsi, que son el regalo.")
p = doc.add_paragraph()
r = p.add_run("Para la batukada se sacan las PASTAS CONGELADAS del almacén.")
r.bold = True
doc.add_paragraph("Y a cada integrante se le regala una bolsa del 20 aniversario con unos calcetines y una cantimplora. Lo preparan los niños en un rato sin clientes, y tiene que estar listo antes de que terminen.")

# ------------------------------------------------------------------ 5
h1("5 · Los dos niños, en la puerta")
doc.add_paragraph("Chico, 16 años · chica, 13. Mandil verde y gorro de cocinero.")
p = doc.add_paragraph()
r = p.add_run("Uno da la palmera y el otro la bolsa — a todo el que entra.")
r.bold = True
doc.add_paragraph("Y se encargan de la mesa de las palmeras y de la urna. Es su sitio.")
for t in [
    "Que estén desde la apertura.",
    "Que la mesa esté a su altura: sin tener que salir de su sitio.",
    "Un adulto cerca, pero no encima: para que puedan ir al baño, comer o descansar.",
    "Que haya palmeras y bolsas de sobra para reponer.",
]:
    bullet(t)

# ------------------------------------------------------------------ 6
h1("6 · El canje y la piruleta")
doc.add_paragraph("El cliente paga, y al salir cambia el ticket por una papeleta.")
for t in [
    "Una papeleta por ticket.",
    "Premiada → a la CAJITA (esas se guardan: son el control).",
    "No premiada → a la PAPELERA.",
    "Y quien no gane, cambia la papeleta por una PIRULETA, en la caja.",
]:
    bullet(t)
p = doc.add_paragraph()
r = p.add_run("Hay 500 piruletas para 387 papeletas que no ganan. Sobran 113.")
r.bold = True

# ------------------------------------------------------------------ 7
h1("7 · El fotógrafo")
p = doc.add_paragraph()
r = p.add_run("Distira (Javi) — 647 91 06 17")
r.bold = True
r.font.size = Pt(13)
doc.add_paragraph("Viene a las 10:00 y se queda hasta las 14:30.")
for t in [
    "Que sepa dónde ponerse: la tarta y la mesa son el fondo.",
    "La foto de todo el equipo, a las 11:30 — avisar a todos el sábado.",
    "Que salgan la tarta, el cartel y los niños.",
]:
    bullet(t)

# ------------------------------------------------------------------ 8
h1("8 · La visita a Rosa")
doc.add_paragraph("Sobre las 11, con unas pastas.")
for t in [
    "Que alguien vaya: que no se pase la hora entre la batukada y la foto.",
    "Las pastas, aparte. No las del lunch.",
]:
    bullet(t)

# ------------------------------------------------------------------ 9
h1("9 · Lo que NO puede pasar")
tabla([
    ["Que la mesa se vuelque", "tablón sobre caballetes, con 500 palmeritas, la urna y 113 premios"],
    ["Que las palmeritas estén al aire", "son comida, y están en la calle"],
    ["Que se cambie dos veces el mismo ticket", "se acaban las papeletas antes de la hora"],
    ["Que los niños se queden sin nada que dar", "hay que reponer a media mañana"],
    ["Que la batukada llegue y no haya lunch", "se prepara antes de abrir"],
    ["Que la batukada y la música suenen a la vez", "no se oye ninguna de las dos"],
    ["Que al cerrar la cajita no tenga 113", "falta un premio por entregar"],
], cabecera=["Qué", "Por qué"])

# ------------------------------------------------------------------ 10
h1("10 · Quién hace qué")
tabla([
    ["Jefa", "Libra. Va y viene y está pendiente de todo. No tiene puesto fijo: su trabajo es que aquello funcione."],
    ["Tienda", "La jornada normal. Los turnos ya están arreglados."],
    ["Coordinación", "El pan de la tahona y de Zuaza, y el canje."],
    ["Cocina", "—"],
], cabecera=["Puesto", "Qué hace ese día"])

# ------------------------------------------------------------------ 11
h1("11 · Los números")
p = doc.add_paragraph()
r = p.add_run("500 papeletas  ·  113 con premio  ·  387 de «hoy no ha sido»")
r.font.size = Pt(12)
p = doc.add_paragraph()
r = p.add_run("500 palmeritas  ·  500 bolsas de tela  ·  500 piruletas")
r.font.size = Pt(12)
p = doc.add_paragraph()
r = p.add_run("113 premios  ·  2 niños  ·  de 10:00 a 14:30")
r.font.size = Pt(12)

salida = "MANUAL-DEL-DIA-20-ANIVERSARIO.docx"
doc.save(salida)
import os
print(f"  {salida} · {round(os.path.getsize(salida)/1024,1)} KB")
