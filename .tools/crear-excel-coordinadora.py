"""Excel de revisión. MAÑANA y TARDE de tienda SEPARADAS, y en el orden dictado.

Formato uniforme:
  {"sec": "..."}                        -> fila de apartado
  {"c": "...", "o": "...", "n": "..."}  -> fila de tarea
"""
import json
import sys
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

sys.stdout.reconfigure(encoding="utf-8")

VERDE = "2EC258"
VERDE_OSC = "1E9A45"
SUAVE = "EFFAF2"
AMARILLO = "FFF8E6"
CABECERA = PatternFill("solid", fgColor=VERDE_OSC)
TITULO = PatternFill("solid", fgColor=VERDE)
BLOQUE_FILL = PatternFill("solid", fgColor=SUAVE)
SITIO_FILL = PatternFill("solid", fgColor=AMARILLO)
BORDE = Border(*[Side(style="thin", color="D6EDDD")] * 4)
DIAS = {"LUN": "lun", "MAR": "mar", "MIE": "mié", "JUE": "jue", "VIE": "vie", "SAB": "sáb", "DOM": "dom"}


def S(t):
    return {"sec": t}


def T(texto, nota=None):
    return {"o": texto, "n": nota}


def C(texto, nota=None):
    return {"c": texto, "n": nota}


# --------------------------------------------------------------- coordinadora
APERTURA_LS = [
    S("BLOQUE 0 · Al llegar — 7:00 (sábado 8:00)"),
    C("Quitar la alarma"),
    C("Encender contadora, ordenadores, cajas, balanzas y horno"),
    C("Sacar el carro de la cámara de fruta"),
    C("Sacar la bollería de Malato (la que sobró del día anterior)"),
    C("Preparar la primera hornada: pan y una bandeja de bollería grande"),
    C("Quitar los ventiladores, si hiciera falta"),
    S("BLOQUE 1 · Durante la primera hornada — 7:00 a 7:30"),
    C("Sacar bandejas de bollería de la cámara y colocarlas en el lineal de la caja"),
    C("Decidir si hace falta bollería pequeña y, si sí, apuntarla para la 3.ª hornada"),
    C("Mirar si harán falta empanadillas (si sí, 4.ª y 5.ª, que tardan dos hornadas)"),
    C("Preparar las siguientes bandejas de pan"),
    C("Quitar el pan del día anterior, si hubiera"),
    C("Comprobar la devolución de pan"),
    {"c": "Colocar el carro de la fruta", "o": "Reponer y colocar fruta"},
    C("Echar un vistazo rápido a la fruta, por si faltara algo indispensable antes de abrir"),
    C("Preparar pollo, cerdo, ternera, salchichas, hamburguesas y empanado"),
    C("Guardar el pedido de fruta (lunes y viernes)"),
    C("Hacer la lista del monta"),
    C("Preparar las cajas de cobro para el día"),
    C("Pintar bollería (la recién horneada)"),
    S("BLOQUE 2 · Segunda hornada — 7:30"),
    {"c": "Bajar al almacén a preparar el monta", "o": "Subir monta"},
    S("BLOQUE 3 · Antes de abrir — 8:00 (sábado 9:00)"),
    C("Encender luces"),
    C("Encender música"),
    S("BLOQUE 4 · Una vez abierta la tienda — 8:00 a 9:00"),
    C("Pintar la bollería de Malato"),
    C("Limpiar y ordenar la zona del horno"),
    C("Sacar lo que hace falta reponer, para colocarlo después "
      "(snacks · bolsitas 1 € · envasados de charcutería · congelado · refrigerado)"),
]

APERTURA_DOM = [
    S("BLOQUE 0 · Al llegar — 8:00"),
    C("Quitar la alarma (la misma que de lunes a sábado)"),
    C("Encender contadora, ordenadores, cajas, balanzas y horno"),
    C("Bajar al almacén y subir: 1 caja Mediterránea + 1 caja Baguette"),
    C("Sacar la bollería de Malato — si la hubiera"),
    S("BLOQUE 1 · Primera hornada — 8:00 a 8:30"),
    C("Preparar la bollería para la apertura de las 10:00"),
    C("Quitar el pan del día anterior, si lo hubiera"),
    C("Comprobar la devolución de pan"),
    {"c": "Colocar el carro de la fruta", "o": "Reponer y colocar fruta"},
    {"c": "Sacar la fruta y verdura para que la coloque la persona de tienda", "o": "Reponer y colocar fruta"},
    C("Preparar pollo, cerdo, ternera, salchichas, hamburguesas y empanado"),
    C("Hacer la lista del monta"),
    S("BLOQUE 2 · Segunda hornada — 8:30 a 9:00"),
    {"c": "Bajar al almacén a preparar el monta", "o": "Subir monta"},
    C("Subir el pan restante"),
    C("Subir panes especiales"),
    {"c": "Frentear la cámara de yogures", "o": "Frentear y reponer yogures"},
    C("Sacar lo que hace falta reponer, para colocarlo antes de abrir "
      "(snacks · bolsitas 1 € · envasados de charcutería · congelado · refrigerado)"),
    S("BLOQUE 3 · Tercera hornada — 9:00 a 9:30"),
    C("Pintar toda la bollería hecha hasta el momento y meterla a la nevera"),
    C("Abrir las cajas de cobro"),
    S("BLOQUE 4 · Cuarta hornada — 9:30 a 10:00"),
    C("Pintar la última bandeja de bollería y meterla a la cámara"),
    C("Sacar las bandejas de bollería de la cámara y montar la bollería grande y la "
      "pequeña, y las tartas y el pastel de arroz"),
    C("Sacar la última bandeja de bollería de la cámara y montarla"),
    S("BLOQUE 5 · Antes de abrir — 9:45"),
    C("Actualizar el stock de la cocina y decidir lo que se mete en el asador"),
    C("Pintar la bollería de Malato — si la hubiera"),
    C("Encender luces"),
    C("Encender tablets"),
    C("Encender música"),
]

EL_DIA = [
    S("RUTINA · todos los días"),
    C("Preparar pedidos"),
    C("Pasar pedidos"),
    {"c": "Mirar si hace falta utillaje y subirlo del almacén", "o": "Reponer utillaje"},
    C("Organizar el trabajo del día (buscar tarea o clasificar alguna como urgente)"),
    C("Hacer pan según necesidades"),
    C("Ordenar Lineal (Producto-Precio)"),
    C("Subir panes especiales"),
    C("Hacer sitio para los pedidos que vayan a llegar hoy"),
    C("Poner precios nuevos o actualizados en los productos"),
    C("Ordenar trastienda"),
    C("Fruta, verdura, carne y empanado: sacar y reponer a lo largo de la mañana"),
    C("Arreglar productos que no estén en buen estado"),
    S("DE UN DÍA CONCRETO"),
    C("Bajar Cadagua — lunes, miércoles y viernes"),
    C("Subir Cadagua — martes, jueves, sábados y domingos"),
    C("Sacar pollos congelados — jueves"),
    C("Sacar salsa de pollos congelada — jueves"),
    C("Preparar bollería de Malato en bandejas de 1-2 € y sacarlas en el cierre — viernes y sábados"),
    C("Ordenar cámara de fruta — sobre todo domingos y jueves"),
]

CIERRE_COORD = [
    S("CIERRE DE COORDINACIÓN"),
    C("Cerrar Caja 3"),
    C("Revisar que la carne esté bien repuesta"),
    C("Revisar que la fruta esté bien repuesta"),
    C("Revisar que la verdura esté bien repuesta"),
]

# ----------------------------------------------------- tienda · mañana dictada
MANANA = [
    S("LO DE SIEMPRE · en este orden"),
    T("Fichar", "DESAPARECE: lo hace la aplicación al entrar"),
    T("Tarea diaria urgente", "La pone coordinación o gerencia"),
    T("Frentear y reponer, siempre ORDENADO POR CADUCIDADES: fruta · leche · yogures · congelado"),
    T("Subir monta"),
    T("Apuntar el pan", "Quizá pase a coordinadoras"),
    T("Tickar los pedidos que llegan y comprobar que todo pasa"),
    T("Reponer bebidas frías", "No pegar atrás"),
    T("Tarea diaria complementaria", "La pone coordinación o gerencia"),
    T("Cocina: fregar y recoger todo", "Dejar las fregaderas limpias"),
    S("LO DE HOY · lunes"),
    T("Limpiar y desinfectar la cámara de pollos: suelo puerta derecha · suelo puerta izquierda · "
      "puertas · baldas superiores derecha · baldas inferiores derecha · baldas superiores izquierda",
      "Con qué producto · resumen de quién, qué y con qué"),
    T("Pollos que han sobrado del fin de semana: envasar con salsa los cocinados"),
    T("Pollos que han sobrado del fin de semana: congelar los frescos"),
    T("Pollos que han sobrado del fin de semana: congelar la salsa"),
    T("Contar: pollos · codillos · patatas normales · patatas bravas"),
    T("Limpiar la envasadora", "Con un paño y agua · habrá documento de cómo funciona"),
    T("Limpiar las fregonas",
      "Dejar con lejía · son varias fregonas · el resto de días solo se sacuden"),
    T("Limpiar el baño"),
    S("LO DE HOY · martes"),
    T("Limpiar y desinfectar el horno de pan"),
    T("Limpiar y desinfectar la charcutería: exposición · zona de almacenaje inferior · "
      "todos los cristales · todas las puertas"),
    T("Limpiar y desinfectar la mesa de charcutería", "Entera"),
    S("LO DE HOY · miércoles"),
    T("Limpiar el suelo debajo del horno de pan"),
    T("Limpiar la zona de bandejas de horno"),
    T("Limpiar el congelado: cubetas (dos mínimo, ir alternando) · tarrinas",
      "Desplegable para saber cuáles cubetas"),
    S("LO DE HOY · sábado"),
    T("Limpiar y desinfectar la charcutería: exposición · zona de almacenaje inferior · "
      "todos los cristales · todas las puertas"),
    T("Limpiar y desinfectar la mesa de charcutería", "Entera"),
    T("Revisar toda la fruta y verdura",
      "Desplegable para que no se olvide nada · la lista la dirá la propiedad"),
    S("LO DE HOY · jueves, viernes y domingo"),
    T("FALTA: no me has dictado tarea propia para estos días"),
    S("ANTES DE IRSE · en este orden"),
    T("Revisar la charcutería: que no queden piezas sin tapar · que estén las puertas cerradas"),
    T("Apagar luces"),
    T("Comprobar las puertas: las de los congeladores cerradas · las de las neveras cerradas"),
    T("Tirar basura", "Si está llena"),
    T("Tirar cartones"),
    T("Tirar plásticos"),
]

# ------------------------------------------------- tienda · tarde (del Excel)
# OJO: el archivo histórico conserva la clave antigua («operaria») a propósito;
# aquí se acepta cualquiera de las dos para no romper la generación.
cat = json.load(open("docs/archivo/tareas-catalogo.json", encoding="utf-8"))
op = next(x for x in cat["puestos"] if x["clave"] in ("tienda", "operaria"))
por_id = {t["id"]: t for t in op["tareas"]}
tarde = defaultdict(list)
for dia, items in op["semana"].items():
    for x in items:
        if x["t"] == "T":
            t = por_id.get(x["id"])
            if t:
                tarde[dia].append(t["nombre"])

# ------------------------------------------------- tienda · tarde (DICTADA)
TARDE = [
    S("LO DE SIEMPRE · en este orden"),
    T("Fichar", "DESAPARECE: lo hace la aplicación al entrar · igual que a la mañana"),
    T("Reponer, frentear y colocar, respetando caducidades: fruta · leche · yogures · congelado · "
      "zona gominolas y txutxes · zona snacks (Matutano) · zona snacks (Tosfrit) · "
      "zona snacks (Paquetería surtida)",
      "Lo mismo que a la mañana, más gominolas y txutxes, más los tres snacks"),
    T("Colocar monta", "El que se ha subido por la mañana"),
    T("Lineales: frentear · rellenar · ordenar"),
    T("Reponer bebidas frías", "No pegar atrás"),
    T("Tarea diaria complementaria", "La pone coordinación o gerencia"),
    T("Vaciar agua cámara fruta", "Las dos bandejas"),
    T("Limpiar las fregonas",
      "Solo se sacuden · son varias fregonas · el lunes por la mañana se dejan con lejía"),
    T("Cocina: fregar y recoger todo", "Dejar las fregaderas limpias"),
    T("Limpiar cajas de cobro: delante · detrás · pantalla", "Con brocha"),
    S("LO DE HOY · lunes"),
    T("Limpiar zona txutxes: izquierda de caja · frente de caja"),
    T("Limpiar el mueble pan de Zuaza"),
    T("Limpiar el expositor azul", "Junto a caja"),
    T("Limpiar el mueble expositor de madera", "Frente a caja"),
    T("Hacer bolsitas: txutxes 1 € · torcidas rojas · torcidas negras · torcidas mixtas"),
    S("LO DE HOY · martes"),
    T("Limpiar y ordenar la zona de cajas: caja · baldas / lineales · TPV"),
    T("Limpiar etiqueteros por zonas, con trapo húmedo",
      "Las zonas, en otro desplegable que rellenará la propiedad"),
    T("Hacer bolsitas: txutxes 1 € · torcidas rojas · torcidas negras · torcidas mixtas"),
    S("LO DE HOY · miércoles"),
    T("Centrar agua"),
    T("Reponer utillaje", "Con una casilla con todo lo que hay que reponer"),
    T("Limpiar el mueble de bandejas del horno", "Cesto de mimbre incluido"),
    T("Limpiar los congeladores por fuera: los bordes · los frentes · entre cristales"),
    T("Revisar toda la verdura y fruta",
      "Lo mismo que el sábado por la mañana: la MISMA tarea, no una copia"),
    S("LO DE HOY · jueves"),
    T("Ordenar y colocar la zona de galletas 1 €"),
    T("Limpiar el exterior entero de la cámara de los yogures"),
    T("Limpiar una balda de yogures"),
    T("Fregar la cámara de la fruta"),
    T("Poner cartones en las escaleras", "Felpudo"),
    T("Abrir la puerta del lateral de la tienda"),
    S("LO DE HOY · viernes"),
    T("NO HAY TAREA PROPIA: se termina lo que quedó pendiente a lo largo de la semana"),
    S("LO DE HOY · sábado"),
    T("Hacer bandejas de bollería"),
    T("Reponer utillaje", "Con una casilla con todo lo que hay que reponer"),
    S("LO DE HOY · domingo"),
    T("Hay muchos clientes: solo trabajo de caja y reponer lo que dé tiempo"),
    T("Fregar la cámara de la fruta"),
    T("Poner cartones en las escaleras", "Felpudo"),
    T("Abrir la puerta del lateral de la tienda"),
    S("ANTES DE IRSE · en este orden"),
    T("Revisar la fruta más perecedera",
      "La que esté guardada en el carro, en la cámara de la fruta"),
    T("Revisar la charcutería: que no queden piezas sin tapar · que estén las puertas cerradas"),
    T("Apagar luces"),
    T("Comprobar las puertas: las de los congeladores cerradas · las de los refrigeradores cerradas"),
    T("Tirar basura"),
    T("Tirar cartones"),
    T("Tirar plásticos"),
]

SHEETS = [
    ("Apertura L-S", "Apertura · lunes a sábado",
     "25 pasos · la hace coordinación o gerencia (sábado, una hora más tarde)", APERTURA_LS),
    ("Apertura domingo", "Apertura · domingos y festivos",
     "26 pasos · LOS HACE UNA SOLA PERSONA, la coordinadora que entra a las 8:00", APERTURA_DOM),
    ("El día", "El día · coordinación", "rutina de todos los días + lo de cada día", EL_DIA),
    ("Cierre coordinación", "Cierre de coordinación", "4 pasos · tres son revisiones", CIERRE_COORD),
    ("Tienda mañana", "Tienda · la mañana",
     "Lo dictado, EN TU ORDEN: lo de siempre → lo de hoy → antes de irse.", MANANA),
    ("Tienda tarde", "Tienda · la tarde",
     "Lo dictado, EN TU ORDEN: lo de siempre → lo de hoy → antes de irse. "
     "Distinta de la mañana: aquí crece la reposición y se añaden zonas.", TARDE),
]

wb = Workbook()


def hoja(nombre, titulo, subtitulo, filas):
    ws = wb.create_sheet(nombre)
    ws["A1"] = titulo.upper()
    ws["A1"].font = Font(bold=True, size=15, color="FFFFFF")
    ws["A1"].fill = TITULO
    ws.merge_cells("A1:C1")
    ws.row_dimensions[1].height = 28
    ws["A2"] = subtitulo
    ws["A2"].font = Font(size=10, italic=True, color="5E6E63")
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.merge_cells("A2:C2")
    ws.row_dimensions[2].height = 32
    for i, h in enumerate(["COORDINADORA", "TIENDA", "MODIFICACIONES"], 1):
        cel = ws.cell(row=4, column=i, value=h)
        cel.font = Font(bold=True, color="FFFFFF", size=11)
        cel.fill = PatternFill("solid", fgColor=VERDE_OSC if i < 3 else "D97706")
        cel.alignment = Alignment(horizontal="center", vertical="center")
        cel.border = BORDE
    ws.row_dimensions[4].height = 24

    r = 5
    for f in filas:
        if "sec" in f:
            ws.cell(row=r, column=1, value=f["sec"]).font = Font(bold=True, size=10, color=VERDE_OSC)
            for col in range(1, 4):
                ws.cell(row=r, column=col).fill = BLOQUE_FILL
                ws.cell(row=r, column=col).border = BORDE
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
            ws.row_dimensions[r].height = 20
            r += 1
            continue
        for col, clave in ((1, "c"), (2, "o")):
            if f.get(clave):
                cel = ws.cell(row=r, column=col, value=f[clave])
                cel.alignment = Alignment(wrap_text=True, vertical="top")
        if f.get("n"):
            nc = ws.cell(row=r, column=2)
            if not f.get("o"):
                nc.value = f["n"]
                nc.font = Font(size=9, italic=True, color="79797F")
            nc.alignment = Alignment(wrap_text=True, vertical="top")
        for col in range(1, 4):
            ws.cell(row=r, column=col).border = BORDE
        ws.cell(row=r, column=3).fill = SITIO_FILL
        r += 1

    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 66
    ws.column_dimensions["C"].width = 44
    ws.freeze_panes = "A5"


for nombre, titulo, sub, filas in SHEETS:
    hoja(nombre, titulo, sub, filas)

# ------------------------------------------------------------------ cómo usarlo
wi = wb.create_sheet("Cómo usarlo", 0)
wi["A1"] = "CÓMO USAR ESTO"
wi["A1"].font = Font(bold=True, size=16, color="FFFFFF")
wi["A1"].fill = TITULO
wi.merge_cells("A1:B1")
wi.row_dimensions[1].height = 30

PASOS = [
    ("Qué es", "Todo lo que me has dictado, en tu orden, en un sitio donde puedas corregirlo."),
    ("Las columnas", "COORDINADORA · lo de coordinación.  TIENDA · lo de tienda.  "
                     "MODIFICACIONES · aquí escribes tú."),
    ("El fallo que he corregido",
     "Antes mezclé la mañana y la tarde de tienda. Ahora son DOS hojas separadas: "
     "«Tienda mañana» (lo que acabas de dictar, en tu orden) y «Tienda tarde» "
     "(lo que había en tu Excel, con su turno respetado)."),
    ("La hoja de la tarde",
     "No es definitiva. Es lo que había, ya separado de la mañana, para que lo corrijas "
     "o lo dictes de nuevo como has hecho con la mañana."),
    ("Las filas verdes", "Son apartados, no tareas. No las cuentes."),
    ("Si falta una tarea", "Escríbela debajo del apartado que le toca."),
    ("", ""),
    ("SUGERENCIAS TUYAS QUE HE APLICADO", ""),
    ("1", "«Preparar la primera hornada: pan y una bandeja de bollería grande»"),
    ("2", "«Decidir si hace falta bollería pequeña y, si sí, apuntarla para la 3.ª hornada»"),
    ("4", "«Preparar las cajas de cobro para el día»"),
    ("Sin aplicar", "La 3 y la 5, como dijiste."),
]
r = 3
for a, b in PASOS:
    ca = wi.cell(row=r, column=1, value=a)
    cb = wi.cell(row=r, column=2, value=b)
    cb.alignment = Alignment(wrap_text=True, vertical="top")
    if a == "SUGERENCIAS TUYAS QUE HE APLICADO":
        ca.font = Font(bold=True, size=12, color=VERDE_OSC)
    elif a in ("Qué es", "Las columnas", "El fallo que he corregido", "La hoja de la tarde",
               "Las filas verdes", "Si falta una tarea"):
        ca.font = Font(bold=True, size=10)
    else:
        ca.font = Font(bold=True, size=10)
    r += 1
wi.column_dimensions["A"].width = 46
wi.column_dimensions["B"].width = 96

del wb["Sheet"]
wb.save("docs/tareas-coordinadora.xlsx")
print("  escrito docs/tareas-coordinadora.xlsx")
print(f"  hojas: {wb.sheetnames}")
