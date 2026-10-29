"""Genera el catalogo de tareas en JSON y una vista HTML para poder verlo.

El catalogo es DATO, no codigo: se puede importar a la aplicacion mas adelante.
Si alguna tarea de las plantillas no tiene clasificacion, el script FALLA, para que
no se cuele ninguna sin clasificar.
"""
import json
import sys
from collections import defaultdict
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
wb = load_workbook(r".tools\tareas.xlsx", data_only=True)

# ---------------------------------------------------------------- lectura

def parsear(hoja):
    ws = wb[hoja]
    dia = None
    turno = None
    salida = defaultdict(list)
    for r in range(1, ws.max_row + 1):
        v1 = ws.cell(row=r, column=1).value
        v2 = ws.cell(row=r, column=2).value
        v3 = ws.cell(row=r, column=3).value
        for v in (v1, v2):
            if isinstance(v, str) and "ORDINARIAS" in v.upper():
                dia = v.strip().upper().replace("TAREAS ORDINARIAS", "").strip()
                turno = None
        if isinstance(v1, str) and "ORDINARIAS" in v1.upper():
            continue
        if not isinstance(v2, str) or not v2.strip():
            continue
        t = v2.strip()
        # "Fichar" marca el principio de cada turno: el 1.o la manana, el 2.o la tarde.
        # Por eso la plantilla mete filas vacias entre la manana y la tarde.
        if t.upper() == "FICHAR":
            turno = "M" if turno is None else "T"
            continue
        if t.upper() in ("TAREAS", "\u221a") or t.startswith("*"):
            continue
        salida[dia].append((t, str(v3).strip() if v3 else "", turno))
    return salida


# ------------------------------------------------- clasificacion (mi criterio)

# Las dos hojas escriben la misma tarea de dos formas. Al unirlas hay que dejar UNA:
# la mas descriptiva. Solo se aplica a personas de tienda.
UNIFICAR = {
    "Arreglar fruta y verdura y etiquetar de oferta":
        "Arreglar fruta y verdura tocada y etiquetar de oferta",
    "Reponer y colocar chuches":
        "Reponer y colocar chuches  (cajones y cubetas)",
    "Frentear baldas y rellenar con sobrantes (zonas)":
        "Frentear baldas, reponer y rellenar con sobrantes",
    "Limpiar una balda de los yogures (alternar)":
        "Limpiar balda de yogures (alternar) + Por fuera entero",
    "Reponer charcu":
        "Reponer charcu y avisar si se vende carne",
    "Reponer charcu y carne":
        "Reponer charcu y avisar si se vende carne",
    "Revisar TODA la fruta":
        "Revisar que esté TODA la fruta guardada",
    "Limpiar y Ordenar Charcu exposición + Cristales (todos)":
        "Limpiar Charcu (puertas abajo, exposición, todos cristales)",
    "Al fregar comprobar congeladores y cámaras de frío":
        "Al apagar luces comprobar congeladores y cámaras frío",
    "Colocar Monta":
        "Colocar Monta y tienda en general (frentear)",
    "Reponer leche / Yogures / Fruta / Congelado":
        "Frentear y Reponer leche / Yogures / Fruta / Congelado",
}

# Tareas que NO son tareas aunque esten en la hoja.
# La "Tarea Diaria Urgente" es un HUECO que rellenan coordinacion y gerencia cada
# dia: no es una tarea fija, asi que no puede vivir en el catalogo.
EXCLUIR = {"Tarea Diaria Urgente"}

# Tareas que NO estan en ninguna plantilla: las ha dicho la propiedad.
# El pedido del asador NO va aqui: eso es el bloque de PEDIDOS, no una tarea.
ANADIDAS = {
    "coordinadora": [
        {"nombre": "Hacer pedidos y pasarlos", "familia": "Pedidos",
         "importancia": "alta", "aplazable": False,
         "nota": "Hacer los pedidos a proveedor y pasarlos. El calculo y las reglas van en el bloque de PEDIDOS"},
        {"nombre": "Llamar por teléfono", "familia": "Dirigir el día",
         "importancia": "media", "aplazable": True,
         "nota": "Añadida por la propiedad. La lista es viva: se pueden añadir más como esta"},
    ],
}

# nombre exacto -> (familia, importancia, aplazable, nota)
TIENDAS = {
    "Al apagar luces comprobar congeladores y cámaras frío": ("Seguridad del género", "critica", False, "Cerrados y encendidos"),
    "Al fregar comprobar congeladores y cámaras de frío": ("Seguridad del género", "critica", False, "Cerrados y encendidos"),
    "Vaciar Agua Cámara Fruta (las 2 bandejas) y colocar BIEN": ("Seguridad del género", "critica", False, "La plantilla la marca con !!!!"),
    "Revisar que esté TODA la fruta guardada": ("Seguridad del género", "critica", False, "TODA"),
    "Revisar TODA la fruta": ("Seguridad del género", "critica", False, ""),
    "REVISAR TODO EL GÉNERO DEL EXPOSITOR DE VERDURA": ("Seguridad del género", "critica", False, "Apuntar lo mirado"),
    "Revisar charcu plásticos y puertas": ("Seguridad del género", "alta", False, "Limpiar termoselladora"),
    "Limpiar Baño": ("Seguridad del género", "alta", False, ""),
    "Tirar basura si está llena": ("Seguridad del género", "alta", False, ""),
    "Tirar cartones (hay que deshacerlos) y plásticos": ("Seguridad del género", "media", True, "Cartón al azul"),
    "Abrir puerta lateral calle (puerta cerrada pero sin cerrojo)": ("Seguridad del género", "media", False, ""),
    "Poner cartones en las escaleras (felpudo)": ("Seguridad del género", "baja", True, ""),
    "Envasar Pollos": ("Asador y bollería", "critica", False, ""),
    "Congelar Pollos / Congelar Salsa": ("Asador y bollería", "critica", False, ""),
    "Contar Total Pollos                   /Total Codillos": ("Asador y bollería", "alta", False, ""),
    "Contar Total Patatas Norm               /Total Bravas": ("Asador y bollería", "alta", False, ""),
    "Limpiar Envasadora (con un paño y agua)": ("Asador y bollería", "media", True, ""),
    "Frentear y Reponer leche / Yogures / Fruta / Congelado": ("Cliente y reposición", "critica", False, "A lo largo del turno"),
    "Frentear baldas, reponer y rellenar con sobrantes": ("Cliente y reposición", "alta", True, "Frentear toda la tienda"),
    "Frentear baldas y rellenar con sobrantes (zonas)": ("Cliente y reposición", "alta", True, ""),
    "Reponer bebidas frías (no pegar atrás) (2 cámaras)": ("Cliente y reposición", "alta", False, ""),
    "Reponer charcu y avisar si se vende carne": ("Cliente y reposición", "alta", False, ""),
    "Reponer charcu y carne": ("Cliente y reposición", "alta", False, ""),
    "Reponer charcu": ("Cliente y reposición", "alta", False, ""),
    "Reponer y colocar fruta": ("Cliente y reposición", "alta", False, ""),
    "Reponer leche / Yogures / Fruta / Congelado": ("Cliente y reposición", "alta", False, ""),
    "Ordenar leche por fechas (cajas enteras y lineales)": ("Cliente y reposición", "alta", False, "Vaciar cajas y recolocar"),
    "Arreglar fruta y verdura tocada y etiquetar de oferta": ("Cliente y reposición", "alta", True, "Caja encima de lechugas"),
    "Arreglar fruta y verdura y etiquetar de oferta": ("Cliente y reposición", "alta", True, ""),
    "Reponer y colocar chuches": ("Cliente y reposición", "media", True, "Rellenar todo"),
    "Reponer y colocar chuches  (cajones y cubetas)": ("Cliente y reposición", "media", True, ""),
    "Reponer y colocar paquetería snacks": ("Cliente y reposición", "media", True, "Matutano, Grefusa, Tosfrit"),
    "Ordenar Galletas 1€ / Dulcesol": ("Cliente y reposición", "baja", True, ""),
    "Centrar agua (cajas de 1,5l y garrafas)": ("Cliente y reposición", "baja", True, ""),
    "Colocar Monta": ("La Monta (montacargas)", "alta", False, "Apuntar lo que se coloca"),
    "Subir Monta": ("La Monta (montacargas)", "alta", False, "1.er paso: la prepara la coordinadora"),
    "Colocar Monta y tienda en general (frentear)": ("La Monta (montacargas)", "alta", False, ""),
    "Limpiar caja de cobro (delante/pantalla/detrás) con brocha": ("Caja", "alta", False, ""),
    "Limpiar/Ordenar Zona Caja (caja,baldas blancas, TPV)": ("Caja", "media", True, ""),
    "Limpiar zona txutxes (izquierda de caja y frente de caja)": ("Caja", "media", True, "Baldas, cubetas, Kinder"),
    "Tickar todo lo que llega y comprobar que pase": ("Recepción de mercancía", "alta", False, ""),
    "Apuntar Pan": ("Recepción de mercancía", "media", False, ""),
    "Apuntar Pan y Periódicos": ("Recepción de mercancía", "media", False, ""),
    "Fregar y Recoger Cocina (todo, utillaje incluído)": ("Limpieza y orden", "critica", False, "LIMPIAR FREGADERAS"),
    "Limpiar Charcu (puertas abajo, exposición, todos cristales)": ("Limpieza y orden", "media", True, "La cámara entera a fondo"),
    "Limpiar y Ordenar Charcu exposición + Cristales (todos)": ("Limpieza y orden", "media", True, "Mantener"),
    "Limpiar mesa charcu (mueble+suelo)": ("Limpieza y orden", "media", True, ""),
    "Limpiar Cámara Pollos": ("Limpieza y orden", "media", True, ""),
    "Limpiar Horno de Pan": ("Limpieza y orden", "media", True, ""),
    "Limpiar Fregonas": ("Limpieza y orden", "media", True, ""),
    "Limpiar suelos (bordes oscurecidos)": ("Limpieza y orden", "media", True, "Apuntar zona"),
    "Limpiar suelo bajo mesa horno": ("Limpieza y orden", "media", True, ""),
    "Limpiar mueble bandejas pan / bajo cesto mimbre": ("Limpieza y orden", "media", True, ""),
    "Limpiar mueble madera donde se ponen bandejas bollería": ("Limpieza y orden", "media", True, "A la derecha de Zuaza"),
    "Limpiar muebles pan Zuaza (mesa azul y donde periódicos)": ("Limpieza y orden", "media", True, ""),
    "Limpiar una balda de los yogures (alternar)": ("Limpieza y orden", "media", True, ""),
    "Limpiar balda de yogures (alternar) + Por fuera entero": ("Limpieza y orden", "media", True, ""),
    "Limpiar 2 cubetas congelado (alternar) o tarrinas": ("Limpieza y orden", "media", True, ""),
    "Limpiar congeladores fuera (bordes, bajo cristal,…)": ("Limpieza y orden", "media", True, ""),
    "Limpiar etiqueteros por zonas y apuntar cuáles": ("Limpieza y orden", "media", True, "Con esponja escurrida"),
    "Fregar Cámara Fruta": ("Limpieza y orden", "media", True, ""),
    "Hacer bandejas de bollería": ("Asador y bollería", "alta", True, "Surtido"),
    "Hacer bolsitas txutxes y torcidas": ("Suministros internos", "baja", True, "Coger de la TRASTIENDA"),
    "Bandejas: charcu (gr/med/peq)": ("Suministros internos", "baja", True, ""),
    "Bolsas: fruta / charcu / bollería (gr/peq) / pan (gr/peq) / gominolas / compra (asas)": ("Suministros internos", "baja", True, ""),
    "Papel: pan / charcu (gr/peq)": ("Suministros internos", "baja", True, ""),
    "Reponer utillaje (1)": ("Suministros internos", "baja", True, ""),
}

COORDINADORAS = {
    "Organizar trabajo del día": ("Dirigir el día", "critica", False, "LA TAREA CLAVE: reparte el trabajo de las demás"),
    "Reunión": ("Dirigir el día", "alta", False, ""),
    "Cambiar plantillas semanales (tareasx2, revistas, pollos)": ("Dirigir el día", "alta", False, "Aqui se cambian las dos hojas de personas de tienda"),
    "Recepción de Mercancía: tickar (ud o peso) y guardar": ("Recepción y control", "critica", False, ""),
    "Subir Panes Especiales": ("Recepción y control", "alta", False, ""),
    "Bajar Berly's / Cadagua": ("Recepción y control", "alta", False, ""),
    "Subir Berly's / Cadagua": ("Recepción y control", "media", False, ""),
    "Subir Berly's / Cadagua (lo que esté fuera de la cámara)": ("Recepción y control", "media", False, ""),
    "Subir Berly's / Cadagua (lo que queda dentro de la cámara)": ("Recepción y control", "media", False, ""),
    "Hacer sitio para los pedidos que llegan hoy": ("Recepción y control", "alta", False, ""),
    "Guardar Fruta / Uvesa / Gonvador / Berly's / Frigo": ("Recepción y control", "alta", False, ""),
    "Camión: Colocar mercancía y Precios nuevos": ("Recepción y control", "alta", False, ""),
    "Quitar revistas Pronto y apuntar devolución": ("Recepción y control", "media", False, ""),
    "Viene Matutano Preventa (sacar para que reponga él)": ("Recepción y control", "media", False, "EVENTO: viene el proveedor"),
    "Llega Donuts": ("Recepción y control", "media", False, "EVENTO: viene el proveedor"),
    "Precios nuevos": ("Precios y ofertas", "alta", False, ""),
    "Ordenar Lineal (Producto-Precio)": ("Precios y ofertas", "alta", False, "Que el precio de la balda coincida con la caja"),
    "Quitar / Poner Ofertas Coaliment": ("Precios y ofertas", "media", False, ""),
    "Ofertas Finde de Yogures": ("Precios y ofertas", "media", False, ""),
    "Limpiar pollos si hiciera falta": ("Asador y pan", "critica", False, "Dice 'si hiciera falta' pero SE HACE SIEMPRE. Es lo que hace posible el sabado"),
    "Hacer Pan y Bollería": ("Asador y pan", "critica", False, "Domingo"),
    "Sacar pollos y salsa": ("Asador y pan", "alta", False, ""),
    "Sacar bollería grande y peque de Malato": ("Asador y pan", "alta", False, "Bandejas 1EUR y 2EUR"),
    "Sacar, reponer, colocar fruta y ARREGLAR si hiciera falta": ("Cliente y reposición", "critica", False, ""),
    "Reponer leche / Yogures / Fruta / Congelado": ("Cliente y reposición", "alta", False, "SOLAPE con personas de tienda"),
    "Reponer y colocar fruta": ("Cliente y reposición", "alta", False, "SOLAPE con personas de tienda"),
    "Preparar Monta": ("Cliente y reposición", "alta", False, "1.er paso del ciclo de la Monta"),
    "Reponer Vending": ("Cliente y reposición", "media", False, ""),
    "Colocar Danone": ("Cliente y reposición", "media", False, ""),
    "Limpiar fregonas": ("Limpieza y orden", "media", True, "SOLAPE con personas de tienda"),
    "Quitar pelos de fregona de ruedas, carros, muebles, baldas,...": ("Limpieza y orden", "media", True, ""),
    "Ordenar trastienda": ("Limpieza y orden", "media", True, ""),
    "Ordenar cámara fruta": ("Limpieza y orden", "media", True, ""),
    "Recoger, limpiar y ordenar balda de fideos, gelina, …": ("Limpieza y orden", "media", True, ""),
    "Ordenar cestos": ("Limpieza y orden", "baja", True, ""),
}

# Tareas que NO tienen dia fijo. Se hacen cuando se necesitan, y la tienda no
# tiene siempre las mismas necesidades. Se eligen POR ZONA.
# La lista esta ABIERTA: la propiedad ira diciendo mas.
ZONAS = ["Fruta", "Verdura", "Txutxes", "Lineales", "Carne", "Yogures",
         "Quesos", "Charcutería", "Pan y bollería", "Toda la tienda"]

# "*" = vale para cualquier zona
BANCO = [
    ("Limpiar lineales", ["*"], ""),
    ("Limpiar suelos", ["*"], "Bordes y rincones incluidos"),
    ("Limpiar una pared", ["*"], ""),
    ("Limpiar una puerta", ["*"], ""),
    ("Limpiar cristales", ["*"], ""),
    ("Quitar telarañas", ["Toda la tienda"], "Dentro y fuera del local"),
    ("Hacer paquetes de gominolas de 1 €", ["Txutxes"], ""),
    ("Hacer paquetes de torcidas de 1 €", ["Txutxes"], ""),
    ("Cortar y envasar embutido", ["Charcutería"], ""),
    ("Solo cortar embutido", ["Charcutería"], ""),
    ("Solo envasar embutido", ["Charcutería"], ""),
]

# Las coordinadoras SOLO trabajan de manana. Por eso su hoja no trae separacion
# entre manana y tarde: no hay nada que separar.
TURNO_UNICO = {"coordinadora": "M"}

# ---------------------------------------------------------------- montaje

DATOS = [("tienda", "Tienda", "1TareasDiariasMañanaTardeOperar", TIENDAS),
         ("tienda", "Tienda", "2TareasDiariasMañanaTardeOperar", TIENDAS),
         ("coordinadora", "Coordinadoras", "Tareas Coordinadoras", COORDINADORAS)]

catalogo = {
    "puestos": [],
    "banco": {
        "titulo": "Tareas para los huecos",
        "explicacion": ("No tienen día fijo. Se hacen cuando se necesitan, porque la tienda no tiene "
                        "siempre las mismas necesidades. Se elige la zona y luego la tarea."),
        "zonas": ZONAS,
        "tareas": [{"nombre": n, "zonas": z, "nota": nota} for n, z, nota in BANCO],
    },
    "reglas": {
        "lista_viva": ("La lista de tareas es VIVA: se puede añadir, cambiar y quitar. "
                       "De momento solo la pueden cambiar coordinadoras y gerencia."),
        "quien_puede_cambiarla": ["gerencia", "coordinadora"],
        "acceso": {
            "gerencia": ["gerencia", "coordinadora", "tienda"],
            "coordinadora": ["coordinadora", "tienda"],
            "tienda": ["tienda"],
        },
        "acceso_explicado": ("La gerencia ve y hace lo de coordinadoras y personas de tienda; "
                             "las coordinadoras ven y hacen lo de personas de tienda; "
                             "las personas de tienda ven lo suyo."),
        "si_sobra_tiempo": ("Cuando las coordinadoras han terminado su trabajo, pueden hacer "
                            "tareas opcionales o tareas de las personas de tienda."),
    },
}
por_puesto = {}
faltan = []
# La BASE SEMANAL: el orden de cada dia tal como esta en las hojas.
# Es la base de la propiedad y NO se reordena.
semana = {}
for puesto, etiqueta, hoja, mapa in DATOS:
    for dia, lista in parsear(hoja).items():
        if not dia:
            continue
        d3 = dia[:3]
        for tarea, obs, turno in lista:
            # Unificar las dos formas de escribir la misma tarea (solo personas de tienda)
            if puesto == "tienda":
                tarea = UNIFICAR.get(tarea, tarea)
            if tarea in EXCLUIR:
                continue
            if tarea not in mapa:
                faltan.append((etiqueta, tarea))
                continue
            fam, imp, apl, nota = mapa[tarea]
            clave = (puesto, tarea)
            if clave not in por_puesto:
                por_puesto[clave] = {
                    "puesto": puesto, "nombre": tarea, "familia": fam,
                    "importancia": imp, "aplazable": apl,
                    "nota": nota or obs, "dias": set(), "en_plantilla": True,
                }
            por_puesto[clave]["dias"].add(d3)
            # guardar el orden del dia (con su turno), sin repetir
            orden_dia = semana.setdefault(puesto, {}).setdefault(d3, [])
            if not any(x["k"] == clave for x in orden_dia):
                orden_dia.append({"k": clave, "t": turno or TURNO_UNICO.get(puesto)})

# Tareas dichas por la propiedad que no estan en ninguna plantilla
for puesto, lista in ANADIDAS.items():
    for t in lista:
        clave = (puesto, t["nombre"])
        if clave in por_puesto:
            continue
        por_puesto[clave] = {
            "puesto": puesto, "nombre": t["nombre"], "familia": t["familia"],
            "importancia": t["importancia"], "aplazable": t["aplazable"],
            "nota": t["nota"], "dias": set(), "en_plantilla": False,
        }

if faltan:
    print("!! TAREAS SIN CLASIFICAR -- el script se detiene para no colar ninguna:")
    for etiqueta, t in sorted(set(faltan)):
        print(f"   [{etiqueta}] {t}")
    sys.exit(1)

for (puesto, _), v in por_puesto.items():
    v["dias"] = sorted(v["dias"])
    v["n_dias"] = len(v["dias"])

ORDEN_IMP = ["critica", "alta", "media", "baja"]
DIAS = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
for puesto, etiqueta in (("tienda", "Tienda"), ("coordinadora", "Coordinadoras")):
    items = [v for (p, _), v in por_puesto.items() if p == puesto]
    items.sort(key=lambda x: (ORDEN_IMP.index(x["importancia"]), -x["n_dias"], x["nombre"].lower()))
    for i, v in enumerate(items, 1):
        v["id"] = f"{puesto[:3]}-{i:03d}"
    # La base semanal: orden original de cada dia, con su turno, ya en ids
    id_de = {k: v["id"] for k, v in por_puesto.items() if k[0] == puesto}
    base = {d: [{"id": id_de[x["k"]], "t": x["t"]}
                for x in semana.get(puesto, {}).get(d, []) if x["k"] in id_de]
            for d in DIAS}
    catalogo["puestos"].append({"clave": puesto, "etiqueta": etiqueta,
                                "turnos": [TURNO_UNICO[puesto]] if puesto in TURNO_UNICO else ["M", "T"],
                                "tareas": items, "semana": base})

with open("docs/tareas-catalogo.json", "w", encoding="utf-8") as f:
    json.dump(catalogo, f, ensure_ascii=False, indent=2)

for p in catalogo["puestos"]:
    print(f"  {p['etiqueta']}: {len(p['tareas'])} tareas")
print("  escrito docs/tareas-catalogo.json")
