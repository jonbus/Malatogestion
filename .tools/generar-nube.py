"""Genera la app de la nube: login + las pantallas de tienda y coordinación
   + sincronización. Reutiliza los datos ya generados en docs/momentos/."""
import base64
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


def extraer(ruta):
    h = open(ruta, encoding="utf-8").read()
    m = re.search(r"const D = (\{.*?\});\n", h, re.S)
    if not m:
        raise SystemExit(f"no encuentro los datos en {ruta}")
    return json.loads(m.group(1))


# Los turnos REALES, sacados de PlantillasHorarios.xlsx (carpeta de siempre).
# Cuadran con el documento: tienda 20,33 h/semana · coord. 31,25 y 21,0.
#
# Horas de cada tramo: 11-14,30=3,5 · 9,30-14,30=5 · 10,30-15=4,5 · 17-21,30=4,5
#   9-15=6 · 7-14,30=7,5 · 8-15=7 · 10-15=5 · 7-13,30=6,5 · 9-12=3 · 7-13=6 · 8-10=2

# Los tres turnos de tienda (lunes=0 ... domingo=6)
TURNOS_TIENDA = {
    "A": {"nombre": "Mañanas y sábado",
          "dias": {1: 3.5, 2: 3.5, 3: 5, 4: 3.5, 5: 4.5}},            # 20,0 h
    "B": {"nombre": "Lunes mañana y tardes",
          "dias": {0: 3.5, 1: 4.5, 2: 4.5, 3: 4.5, 4: 4.5}},          # 21,5 h
    "C": {"nombre": "Domingo entero y tardes",
          "dias": {0: 4.5, 5: 4.5, 6: 10.5}},                          # 19,5 h
}
TIENDA_ANCLA = "2026-10-19"          # la semana que se dictó...
TIENDA_SEMANA_ANCLA = 3              # ...era la semana 3 del ciclo
TIENDA_SEMANAS = {
    1: {1: "A", 2: "B", 3: "C"},
    2: {1: "B", 2: "C", 3: "A"},
    3: {1: "C", 2: "A", 3: "B"},
}

# Las cuatro semanas de coordinación, tal cual la hoja
COORD_SEMANAS = {
    1: {1: {0: 7.5, 3: 7.5, 4: 7.5, 5: 7, 6: 6},
        2: {2: 6.5, 3: 3}},
    2: {1: {0: 7.5, 2: 6.5, 3: 7.5, 5: 5, 6: 6},
        2: {3: 3, 4: 7.5, 5: 7, 6: 7}},
    3: {1: {0: 7.5, 2: 6.5, 3: 7.5},
        2: {3: 3, 4: 7.5, 5: 7, 6: 6}},
    4: {1: {2: 6.5, 3: 7.5, 4: 7.5, 5: 7, 6: 7},
        2: {0: 6.5, 3: 3, 4: 6, 5: 5, 6: 6}},
}

# Las cuatro semanas de la oficina (hoja «Turnos Gerencia»)
OFICINA_SEMANAS = {
    1: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5, 4: 7.5, 6: 7},
    2: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5, 4: 7.5},
    3: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5, 4: 7.5, 5: 2, 6: 7},
    4: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5},
}
AUSENCIAS = [
    {"puesto": "coordinacion", "numero": 2, "desde": "2026-10-19",
     "hasta": "2026-10-25", "cubre": "Jefa"},
]

# El lunes 26/10/2026 empieza la semana 1 de coordinación y oficina.
CICLO_ANCLA = "2026-10-26"

OP = extraer("docs/momentos/tienda.html")
CO = extraer("docs/momentos/coordinacion.html")

# ============================================================== GERENCIA
# La gerencia no recorre una lista: elige de una bandeja. Pero la bandeja
# tiene un orden, que es el de las fechas.
GER_ENTRADA = [
    {"t": "En la tienda hasta las 9:00",
     "n": "Ayudando a coordinación y/o haciendo tareas de coordinación y tienda · "
          "en verano se entra a las 8:00, así que es una hora"},
]

# Los miércoles: adelantar los pedidos
GER_MIERCOLES = [
    {"t": "Digasa · preparar o adelantar el pedido"},
    {"t": "Cofresa · preparar o adelantar el pedido"},
]

# Frutas Tito: los lunes y los viernes
GER_FRUTAS = [
    {"t": "Frutas Tito · precios y etiquetas",
     "partes": ["Precios", "Etiquetas"]},
]

GER_HOY = [
    {"t": "Mirar los bancos"},
    {"t": "Hacer la caja", "n": "Del día o de días anteriores · se acumula",
     "partes": ["Caja del día", "Cajas pendientes de días anteriores"]},
    {"t": "Dar entrada a todo el género que llega"},
    {"t": "Actualizar precios"},
    {"t": "Sacar etiquetas de precios", "n": "Por género nuevo o por actualización"},
]

GER_LUNES = [
    {"t": "Cofresa · antes de las 11:00", "hora": "11:00",
     "partes": ["Preparar el pedido", "Validar el pedido", "Transmitir (DiTrans)"]},
    {"t": "Digasa · contar y pedir al comercial",
     "partes": ["Contar leche", "Contar refrescos", "Contar cervezas",
                "Pedir al comercial por WhatsApp"]},
    {"t": "La oferta manual del comercial",
     "partes": ["Estudiarla", "Preparar el pedido", "Pedir al comercial por WhatsApp"]},
    {"t": "Digasa · el pedido de planta", "n": "Empieza hoy y acaba el martes",
     "partes": ["Mirar el stock del almacén", "Mirar el stock de la tienda",
                "Ir haciendo el pedido con la pistola", "Validar en la pistola",
                "Cargar en «pedidos planta»", "Dejarlo pendiente hasta el martes"]},
]

GER_MARTES = [
    {"t": "Cerrar el pedido de planta",
     "partes": ["Revisar", "Validar", "Transmitir a la central (DiTrans)"]},
    {"t": "Hacer los talones"},
    {"t": "Organizar los papeles"},
]

GER_MES = [
    {"t": "Relación de horas a la asesoría laboral",
     "n": "2 últimos días del mes y 3 primeros del siguiente · domingos, festivos y vacaciones",
     "cuando": "horas"},
    {"t": "Asesoría fiscal: ventas, comisiones de datáfonos y de bancos",
     "n": "10 primeros días del mes", "cuando": "asesoria"},
    {"t": "Transferencia de la hipoteca",
     "n": "El último día hábil antes del 17", "cuando": "hipoteca"},
    {"t": "Extracto bancario y cotejo",
     "n": "Del 20 al 30, en martes o miércoles", "cuando": "extracto",
     "partes": ["Sacar el extracto en Excel",
                "Comprobar que los cargos e ingresos son facturas o ventas",
                "Cotejar los dos documentos",
                "Apuntar desde qué día va el siguiente"]},
]

GER_OFERTAS = [
    {"t": "Preparar las ofertas", "n": "Jueves o viernes antes del «hasta»",
     "partes": ["Dar de alta las ofertas nuevas", "Sacar las etiquetas",
                "Organizar los stoppers", "Marcar que está preparado"]},
    {"t": "Pegar la cartelería grande", "n": "El lunes del «hasta»"},
]

# Los 15 festivos de 2026 (para saber qué día es hábil)
FESTIVOS_2026 = [
    "2026-01-01", "2026-01-06", "2026-03-19", "2026-04-02", "2026-04-03",
    "2026-04-06", "2026-04-28", "2026-05-01", "2026-07-25", "2026-08-15",
    "2026-10-12", "2026-11-01", "2026-12-06", "2026-12-08", "2026-12-25",
]

DATOS = {
    "tienda": {
        "manana": OP["manana"],
        "tarde": OP["tarde"],
        "cierre": OP["cierre"],
        # la lista del desplegable "Con qué producto" de las tareas de limpieza.
        # Se quedaba fuera, y al llegar a esas tareas la app se caía.
        "productos": OP.get("productos", ["AL28", "Otro (¿cuál?)"]),
    },
    "coordinacion": {
        "apertura": CO["apertura"],
        "dia": CO["dia"],
        "cierre": CO["cierre"],
    },
    "turnos": {
        "tienda": TURNOS_TIENDA,
        "tiendaAncla": TIENDA_ANCLA,
        "tiendaSemanaAncla": TIENDA_SEMANA_ANCLA,
        "tiendaSemanas": TIENDA_SEMANAS,
        "coord": COORD_SEMANAS,
        "oficina": OFICINA_SEMANAS,
        "cicloAncla": CICLO_ANCLA,
        "ausencias": AUSENCIAS,
    },
    "gerencia": {
        "entrada": GER_ENTRADA,
        "hoy": GER_HOY, "lunes": GER_LUNES, "martes": GER_MARTES,
        "mes": GER_MES, "ofertas": GER_OFERTAS, "festivos": FESTIVOS_2026,
        "miercoles": GER_MIERCOLES, "frutas": GER_FRUTAS,
    },
}

LOGO = "data:image/png;base64," + base64.b64encode(
    open("docs/marca/logo-o-blanco.png", "rb").read()).decode()

print(f"  tienda: mañana {len(OP['manana']['rutina'])} + tarde {len(OP['tarde']['rutina'])} "
      f"+ cierre {len(OP['cierre'])} bloques")
print(f"  coordinación: apertura {len(CO['apertura'])} patrones + "
      f"día {len(CO['dia']['rutina'])} + cierre {len(CO['cierre'])}")

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tienda Malato · tareas</title>
<meta name="theme-color" content="#1E9A45">
<style>
  :root{
    --verde:#2EC258; --verde-oscuro:#1E9A45; --verde-claro:#5CD47F;
    --verde-suave:#EFFAF2; --tinta:#13251A; --gris:#5E6E63; --borde:#D6EDDD;
    --azul:#1E6FA8; --rojo:#B3261E; --ambar:#D97706;
  }
  *{box-sizing:border-box}
  html,body{margin:0; padding:0}
  body{background:var(--verde-suave); color:var(--tinta);
       font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.5;
       -webkit-tap-highlight-color:transparent}
  button{font-family:inherit}

  /* ------------------------------------------------ entrar */
  #login{max-width:520px; margin:0 auto; padding:26px 20px 60px}
  .caja-login{background:#fff; border:1px solid var(--borde); border-radius:18px;
              padding:24px 20px; box-shadow:0 2px 10px rgba(19,37,26,.05)}
  .marca{display:flex; align-items:center; gap:14px; margin-bottom:22px}
  .marca .cubo{width:62px; height:62px; background:linear-gradient(135deg,var(--verde),var(--verde-oscuro));
               border-radius:16px; display:flex; align-items:center; justify-content:center; padding:9px}
  .marca .cubo img{max-width:100%; max-height:100%; object-fit:contain}
  .marca h1{margin:0; font-size:21px; line-height:1.2}
  .marca p{margin:2px 0 0; font-size:13px; color:var(--gris)}
  .rotulo{font-size:12.5px; font-weight:700; color:var(--verde-oscuro);
          text-transform:uppercase; letter-spacing:.04em; margin:18px 0 8px}
  .opciones{display:flex; gap:8px; flex-wrap:wrap}
  .op{border:2px solid var(--borde); background:#fff; border-radius:11px; padding:11px 16px;
      font-size:14.5px; font-weight:600; color:var(--verde-oscuro); cursor:pointer}
  .op[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .op:disabled{opacity:.35; cursor:not-allowed}
  .entrar{width:100%; margin-top:24px; border:none; border-radius:13px; padding:16px;
          font-size:16.5px; font-weight:700; color:#fff; cursor:pointer;
          background:linear-gradient(135deg,var(--verde),var(--verde-oscuro))}
  .entrar:disabled{opacity:.4; cursor:not-allowed}
  .aviso-mini{margin-top:14px; font-size:12px; color:var(--gris); text-align:center}

  /* ------------------------------------------------ app */
  header{background:linear-gradient(135deg,var(--verde) 0%,var(--verde-oscuro) 100%);
         color:#fff; padding:14px 18px; position:sticky; top:0; z-index:10;
         text-shadow:0 1px 2px rgba(0,0,0,.18)}
  .fila-sup{display:flex; align-items:center; gap:12px}
  .logo{width:46px; height:46px; flex:0 0 auto; background:#fff; border-radius:12px;
        display:flex; align-items:center; justify-content:center; padding:6px}
  .logo img{max-width:100%; max-height:100%; object-fit:contain}
  header h1{margin:0; font-size:17px}
  header .sub{font-size:11.5px; opacity:.95}
  .quien{margin-left:auto; text-align:right; font-size:11.5px; line-height:1.35}
  .quien b{font-size:13px; display:block}
  .quien button{background:rgba(255,255,255,.22); border:none; color:#fff; border-radius:8px;
                padding:4px 9px; font-size:11px; margin-top:4px; cursor:pointer}
  .prog{margin-top:10px}
  .prog .txt{display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px; opacity:.95}
  .prog .barra{height:8px; background:rgba(255,255,255,.28); border-radius:5px; overflow:hidden}
  .prog .barra i{display:block; height:100%; background:#fff; width:0; transition:width .3s; border-radius:5px}

  .estado-sync{font-size:11.5px; padding:6px 18px; background:#fff; border-bottom:1px solid var(--borde);
               display:flex; align-items:center; gap:7px; color:var(--gris)}
  .punto{width:8px; height:8px; border-radius:50%; background:var(--borde); flex:0 0 auto}
  .punto.ok{background:var(--verde)}
  .punto.error{background:var(--rojo)}
  .punto.trabajando{background:var(--ambar)}

  main{max-width:760px; margin:0 auto; padding:14px 16px 80px}
  .tabs{display:flex; gap:7px; margin-bottom:12px; overflow-x:auto; padding-bottom:3px}
  .tab{flex:1 0 auto; border:2px solid var(--verde); background:#fff; color:var(--verde-oscuro);
       border-radius:10px; padding:9px 12px; font-size:13.5px; font-weight:700; cursor:pointer; white-space:nowrap}
  .tab[aria-pressed=true]{background:var(--verde); color:#fff}
  .subtabs{display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px}
  .st{border:1px solid var(--borde); background:#fff; border-radius:9px; padding:6px 12px;
      font-size:12.5px; font-weight:600; cursor:pointer; color:var(--verde-oscuro)}
  .st[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dias{display:flex; gap:5px; overflow-x:auto; padding-bottom:5px; margin-bottom:12px}
  .fechas{display:flex; gap:6px; align-items:center; margin-bottom:12px; flex-wrap:wrap}
  .fecha-inp{border:1px solid var(--borde); border-radius:9px; padding:6px 10px;
             font-family:inherit; font-size:13px; background:#fff; color:var(--tinta)}
  .mes{display:grid; grid-template-columns:repeat(7,1fr); gap:4px;
       background:#fff; border:1px solid var(--borde); border-radius:12px; padding:10px}
  .mes-cab{text-align:center; font-size:11.5px; font-weight:700; color:var(--gris); padding:4px 0}
  .mes-dia{text-align:center; padding:9px 0; border-radius:8px; font-size:13px;
           cursor:pointer; color:var(--tinta)}
  .mes-dia:hover{background:var(--verde-suave)}
  .mes-dia.hoy{box-shadow:0 0 0 2px var(--verde-claro) inset}
  .mes-dia.sel{background:var(--verde); color:#fff; font-weight:700}
  .arrastre-de{display:block; font-size:10.5px; color:var(--ambar); margin-top:3px; font-weight:600}
  .bloque-arrastre{color:var(--ambar); border-bottom-color:var(--ambar)}
  .bloque-arrastre small{color:var(--ambar)}
  .venia{display:block; font-size:10.5px; color:var(--azul); margin-top:3px; font-weight:600}
  .bloque-pasadas{color:var(--azul); border-bottom-color:var(--azul)}
  .bloque-pasadas small{color:var(--azul)}
  .pasarlo{padding:0 14px 10px 45px}
  .btn-pasar{border:1px solid var(--ambar); background:#fff; color:var(--ambar);
             border-radius:8px; padding:5px 11px; font-size:12px; font-weight:600; cursor:pointer}
  .menu-pasar{display:flex; flex-direction:column; gap:5px; padding:0 14px 12px 45px}
  .op-pasar{border:1px solid var(--borde); background:#fff; color:var(--tinta);
            border-radius:8px; padding:8px 12px; font-size:12.5px; text-align:left; cursor:pointer}
  .op-pasar:hover{background:var(--verde-suave)}
  .otro-dia{display:flex; align-items:center; gap:7px; font-size:12px; color:var(--gris);
            margin-top:3px}
  .otro-dia input{border:1px solid var(--borde); border-radius:7px; padding:5px 8px;
                  font-family:inherit; font-size:12px}
  /* ---- el calendario ---- */
  .cal-cab{display:flex; align-items:center; gap:8px; margin-bottom:10px}
  .cal-mes{flex:1 1 auto; text-align:center; font-size:15px; font-weight:700;
           color:var(--verde-oscuro); text-transform:capitalize}
  .mes-dia{position:relative}
  .punto-nota{position:absolute; bottom:3px; left:50%; transform:translateX(-50%);
              width:5px; height:5px; border-radius:50%; background:var(--azul)}
  .mes-dia.sel .punto-nota{background:#fff}
  .notas{background:#fff; border:1px solid var(--borde); border-radius:12px;
         margin-bottom:10px; overflow:hidden}
  .notas-cab{font-size:11.5px; font-weight:700; text-transform:uppercase;
             letter-spacing:.03em; padding:9px 14px; border-bottom:1px solid var(--borde)}
  .notas.general .notas-cab{color:var(--verde-oscuro); background:var(--verde-suave)}
  .notas.personal .notas-cab{color:#8A4B00; background:#FFF8E6}
  .nota{display:flex; align-items:flex-start; gap:10px; padding:10px 14px;
        border-top:1px solid #F2F7F3}
  .nota:first-of-type{border-top:none}
  .nota-t{flex:1 1 auto; font-size:14px}
  .nota-q{font-size:10.5px; color:var(--gris); white-space:nowrap}
  .nota-x{border:none; background:transparent; color:var(--gris); font-size:13px;
          cursor:pointer; padding:0 2px}
  .nota-x:hover{color:var(--rojo)}
  .nueva-nota{display:flex; gap:6px; align-items:center; background:#fff;
              border:1px solid var(--borde); border-radius:12px; padding:10px;
              margin-top:12px; flex-wrap:wrap}
  .nueva-nota input[type=text]{flex:1 1 200px; border:1px solid var(--borde);
              border-radius:8px; padding:9px 11px; font-family:inherit; font-size:13.5px}
  .nueva-nota select{border:1px solid var(--borde); border-radius:8px; padding:9px 8px;
              font-family:inherit; font-size:13px; background:#fff}
  .btn-add{border:none; border-radius:9px; padding:10px 16px; font-size:13.5px;
           font-weight:700; color:#fff; cursor:pointer;
           background:linear-gradient(135deg,var(--verde),var(--verde-oscuro))}
  /* ---- gerencia ---- */
  .ger-cab{display:flex; justify-content:space-between; align-items:baseline;
           background:#fff; border:1px solid var(--borde); border-radius:12px;
           padding:11px 15px; margin-bottom:12px; font-size:13.5px}
  .ger-cab b{font-size:14.5px; color:var(--verde-oscuro)}
  .ger-cab span{color:var(--gris); font-size:12px}
  .bloque-apagado{color:var(--gris); border-bottom-color:var(--borde)}
  .bloque-apagado small{color:var(--gris); font-style:italic}
  .ventana{display:flex; gap:10px; align-items:baseline; flex-wrap:wrap;
           padding:11px 14px; border-top:1px solid #F2F7F3}
  .ventana:first-child{border-top:none}
  .v-nombre{flex:1 1 160px; font-size:13.5px; font-weight:600}
  .v-plazo{font-size:11.5px; color:var(--gris); white-space:nowrap}
  .v-estado{font-size:11px; font-weight:700; border-radius:6px; padding:2px 8px;
            background:#EFEFEF; color:var(--gris); white-space:nowrap}
  .ventana.abierta .v-estado{background:#FFF8E6; color:#8A4B00}
  .ventana.abierta .v-nombre{color:var(--verde-oscuro)}
  /* ---- encargos ---- */
  .aviso-extra{background:#F3EBF7; border:1px solid #D9C2E6; border-left:4px solid #7B2D8E;
               border-radius:11px; padding:11px 15px; margin-bottom:12px; font-size:13px}
  .aviso-extra b{display:block; color:#7B2D8E; font-size:13.5px}
  .aviso-extra span{color:var(--gris); font-size:12px}
  .extra-de{display:block; font-size:10.5px; color:#7B2D8E; margin-top:3px; font-weight:600}
  .bloque-encargo{color:#7B2D8E; border-bottom-color:#7B2D8E}
  .bloque-encargo small{color:#7B2D8E}
  .btn-borrar{border:1px solid var(--rojo); background:#fff; color:var(--rojo);
              border-radius:8px; padding:5px 11px; font-size:12px; font-weight:600;
              cursor:pointer}
  #fallo{display:none; position:sticky; top:0; z-index:98; background:#B3261E;
         color:#fff; font-size:12.5px; padding:10px 16px; line-height:1.45}
  #fallo b{display:block}
  #pie{max-width:760px; margin:0 auto; padding:0 16px 40px; font-size:11px;
       color:var(--gris); text-align:center}
  #logo-login{cursor:pointer}
  #caja-clave{margin-top:16px}
  #caja-clave input{width:100%; border:1px solid var(--borde); border-radius:10px;
                    padding:12px 14px; font-family:inherit; font-size:15px;
                    margin-bottom:10px}
  .turno-fila{display:flex; gap:10px; align-items:baseline; padding:11px 14px;
              border-top:1px solid #F2F7F3; flex-wrap:wrap}
  .turno-fila:first-child{border-top:none}
  .turno-fila.libre{color:var(--gris)}
  .turno-fila.es-hoy{background:var(--verde-suave)}
  .t-nombre{flex:0 0 130px; font-weight:600; font-size:13.5px}
  .t-turno{flex:1 1 auto; font-size:12.5px; color:var(--gris)}
  .tag.apagado{background:#EFEFEF; color:var(--gris)}
  .tag.ausente{background:#FDE7C8; color:#8A4B00}
  .item.es-urgente .cab-item{border-left:3px solid var(--rojo); padding-left:9px}
  .tag.urgente{background:#FDE8E6; color:var(--rojo); font-weight:700}
  /* ENCARGOS: lo que tiene que llamar la atención */
  .encargo-gordo{background:#FFF4E0; border:2px solid var(--ambar); border-radius:12px;
                 padding:14px 16px; margin-bottom:12px}
  .encargo-gordo.enc-rojo{background:#FDE8E6; border-color:var(--rojo)}
  .encargo-gordo.enc-verde{background:#EAF7EE; border-color:var(--verde-oscuro)}
  .enc-cab{font-size:11px; font-weight:800; letter-spacing:.06em; color:#8A4B00;
           text-transform:uppercase; margin-bottom:6px}
  .enc-rojo .enc-cab{color:var(--rojo)}
  .enc-verde .enc-cab{color:var(--verde-oscuro)}
  .enc-que{font-size:16px; font-weight:700; color:var(--tinta); line-height:1.3}
  .enc-cuando{font-size:11.5px; color:var(--gris); margin-top:4px}
  .enc-btn{margin-top:10px}
  .bloque-arreglar{color:#8A4B00; border-bottom-color:var(--ambar)}
  /* las tareas extra del aviso: se marcan y se pasan */
  .extra-linea{display:flex; align-items:center; gap:9px; margin-top:9px;
               cursor:pointer; font-size:13.5px; color:var(--tinta);
               font-weight:600; line-height:1.3}
  .extra-linea .caja{flex:0 0 auto; width:18px; height:18px; border-radius:6px;
                     border:2px solid rgba(139,92,246,.55); background:#fff}
  .extra-linea.activa .caja{background:rgba(139,92,246,.55)}
  /* la que ya está hecha: tachada, con la casilla llena y sin poder tocarse */
  .extra-linea.hecha{cursor:default; opacity:.62}
  .extra-linea.hecha .caja{background:rgba(139,92,246,.55);
                           border-color:rgba(139,92,246,.55)}
  .extra-linea.hecha .extra-txt{text-decoration:line-through}
  .extra-txt{flex:1 1 auto}
  .btn-llamar{display:inline-flex; flex-direction:column; align-items:center;
              justify-content:center; min-width:54px; padding:5px 10px; border-radius:11px;
              background:var(--verde-oscuro); color:#fff; font-size:19px;
              line-height:1.05; text-decoration:none}
  .btn-llamar small{font-size:9.5px; font-weight:800; letter-spacing:.03em; margin-top:1px}
  #toast{position:fixed; top:10px; left:50%; transform:translateX(-50%); z-index:99;
         background:var(--verde-oscuro); color:#fff; padding:11px 18px; border-radius:12px;
         font-size:13px; font-weight:700; box-shadow:0 6px 20px rgba(0,0,0,.22); display:none;
         max-width:92vw; text-align:center}
  #toast.malo{background:var(--rojo)}
  .menu-dibujo{font-size:22px; line-height:1; margin-bottom:5px}
  .casc-panel{border:1.5px solid var(--ambar); background:#FFFBF2; border-radius:12px;
              padding:10px 12px; margin:10px 0}
  .casc-linea{display:flex; align-items:center; gap:6px; flex-wrap:wrap;
              margin:2px 0 0 27px; font-size:11.5px; color:var(--gris)}
  .casc-icono{color:var(--ambar); font-weight:800}
  .casc-linea .btn-add-2,.casc-linea .btn-borrar{font-size:10.5px; padding:2px 8px}
  .pista.tarde{color:var(--rojo); font-weight:700}
  .guardado{font-size:11px; color:var(--verde-oscuro); font-weight:700; margin-left:8px}
  /* EL MENÚ DEL GRUPO */
  /* los bloques que se abren y se cierran */
  h2.bloque.plega{display:flex; align-items:center; gap:8px; cursor:pointer;
                  user-select:none; pointer-events:auto}
  h2.bloque.plega .flecha{font-size:12px; color:var(--gris); width:12px; flex:0 0 12px}
  h2.bloque.plega .bloque-tit{flex:1 1 auto}
  h2.bloque.plega small{flex:0 0 auto; margin-left:auto}
  h2.bloque.plega.hecho .bloque-tit{color:var(--verde-oscuro)}
  .bloque-ok{color:var(--verde-oscuro) !important; font-weight:800}
  .menu-grupo{display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin:14px 0}
  .menu-btn{position:relative; display:flex; flex-direction:column; align-items:center;
            justify-content:center; min-height:82px; padding:12px 8px; border-radius:14px;
            border:1.5px solid var(--borde); background:#fff; cursor:pointer;
            font-family:inherit; color:var(--tinta)}
  .menu-btn b{font-size:13.5px; font-weight:700; line-height:1.25; text-align:center}
  .menu-btn:active{background:#F4F1EA}
  .menu-btn.activo{background:var(--verde-oscuro); border-color:var(--verde-oscuro)}
  .menu-btn.activo b{color:#fff}
  .cal-menu{margin:10px 0 4px}
  .menu-btn.con-pendientes{border-color:#C084FC; background:#FBF5FF}
  .menu-num{position:absolute; top:8px; right:9px; min-width:20px; height:20px;
            border-radius:10px; background:#8B5CF6; color:#fff; font-size:11px;
            font-weight:800; display:flex; align-items:center; justify-content:center;
            padding:0 5px}
  @media (min-width: 620px){ .menu-grupo{grid-template-columns:repeat(3, 220px)} }
  .sug-caja{display:none; position:relative; width:100%; max-height:190px;
            overflow-y:auto; background:#fff; border:1px solid var(--borde);
            border-radius:9px; margin-top:-2px; box-shadow:0 6px 16px rgba(0,0,0,.08); z-index:5}
  .sug-linea{padding:9px 12px; font-size:12.5px; color:var(--tinta); cursor:pointer;
             border-bottom:1px solid #F2F0EC}
  .sug-linea:last-child{border-bottom:none}
  .sug-linea:hover,.sug-linea:active{background:#F7F4EE}
  .casc-caja{border-left:3px solid var(--ambar); background:#FFFBF2; border-radius:0 10px 10px 0;
             padding:8px 12px; margin:8px 0}
  .casc-tit{display:block; font-size:11px; letter-spacing:.05em; color:#8A4B00;
            text-transform:uppercase; margin-bottom:4px}
  .casc-fila{gap:6px}
  .casc-fila select{font-size:11.5px; padding:5px 6px}
  .extra-pasar{display:flex; align-items:center; gap:7px; flex-wrap:wrap;
               margin:5px 0 2px 27px}
  .extra-pasar .inp-enc{font-size:11.5px; padding:3px 6px; border-radius:6px;
                        border:1px solid rgba(139,92,246,.4); background:#fff}
  .item.es-arreglar .cab-item{border-left:3px solid var(--ambar); padding-left:9px}
  .tag.arreglar{background:#FDF1DC; color:#8A4B00; font-weight:700}
  /* ---- el recuento del lunes ---- */
  .recuento{display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; padding:14px}
  .rec-campo{display:flex; flex-direction:column; gap:5px; font-size:12px; color:var(--gris)}
  .rec-campo b{font-size:17px; color:var(--tinta)}
  .tahona{grid-template-columns:1fr}
  .rec-campo input{border:1px solid var(--borde); border-radius:8px; padding:9px 10px;
                   font-family:inherit; font-size:15px; font-weight:700; color:var(--tinta)}
  .rec-tabla{padding:6px 0}
  .rec-fila{display:grid; grid-template-columns:repeat(5, 1fr); gap:6px;
            padding:8px 14px; font-size:12.5px; border-top:1px solid #F2F7F3}
  .rec-fila:first-child{border-top:none}
  .rec-fila span:not(:first-child){text-align:right}
  .rec-cab{font-size:10.5px; font-weight:700; color:var(--gris);
           text-transform:uppercase; letter-spacing:.04em}
  .rec-hoy{background:var(--verde-suave); font-weight:700}
  /* ---- lo que viene ---- */
  .ofertas-hechas{margin-top:10px; border-top:2px solid #F2F7F3; padding-top:4px}
  .ofertas-cab{display:block; padding:8px 14px 4px; font-size:10.5px; font-weight:700;
               color:var(--gris); text-transform:uppercase; letter-spacing:.06em}
  .bloque-viene{color:var(--ambar); border-bottom-color:var(--ambar)}
  .lista-viene{background:#FFFBF3}
  .viene-fila{display:flex; gap:10px; align-items:baseline; padding:10px 14px;
              border-top:1px solid #FBF2E3; flex-wrap:wrap}
  .viene-fila:first-child{border-top:none}
  .viene-dia{flex:0 0 66px; font-weight:700; font-size:12px; color:var(--ambar)}
  .viene-que{flex:1 1 170px; font-size:13px}
  .viene-quien{font-size:10.5px; color:var(--gris); text-transform:uppercase; letter-spacing:.04em}
  /* ---- tareas extra desde el calendario ---- */
  .fila-tarea{justify-content:space-between}
  .btn-add-2{border:1px dashed #7B2D8E; background:#fff; color:#7B2D8E;
             border-radius:9px; padding:9px 15px; font-size:13px; font-weight:700;
             cursor:pointer}
  .pista{font-size:11.5px; color:var(--gris)}
  .notas.encargos .notas-cab{color:#7B2D8E; background:#F3EBF7}
  .punto-nota.es-encargo{background:#7B2D8E}
  .mes-dia.sel .punto-nota.es-encargo{background:#fff}
  .dia-btn{flex:0 0 auto; border:1px solid var(--borde); background:#fff; border-radius:9px;
           padding:6px 10px; font-size:12px; font-weight:600; cursor:pointer;
           color:var(--verde-oscuro); min-width:44px; text-align:center}
  .dia-btn[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dia-btn.hoy{box-shadow:0 0 0 2px var(--verde-claro) inset}

  h2.bloque{font-size:15px; margin:18px 0 8px; padding-bottom:6px;
            border-bottom:2px solid var(--verde); color:var(--verde-oscuro);
            display:flex; justify-content:space-between; align-items:baseline; gap:10px}
  h2.bloque small{font-weight:400; font-size:11px; color:var(--gris)}
  .nota-patron{background:#E8F2FA; border:1px solid #C3DDF0; border-left:4px solid var(--azul);
               border-radius:10px; padding:10px 14px; font-size:12.5px; color:#14506F; margin-bottom:12px}
  .lista{background:#fff; border:1px solid var(--borde); border-radius:12px; overflow:hidden}
  .item{border-top:1px solid #F2F7F3}
  .item:first-child{border-top:none}
  .cab-item{display:flex; gap:10px; align-items:flex-start; padding:11px 14px; cursor:pointer}
  .item.hecha .cab-item{background:var(--verde-suave)}
  .caja{width:20px; height:20px; flex:0 0 auto; border-radius:6px; border:2px solid var(--borde);
        margin-top:1px; display:flex; align-items:center; justify-content:center; font-size:11px; color:#fff}
  .item.hecha .caja{background:var(--verde); border-color:var(--verde)}
  .item.hecha .caja::after{content:"✓"}
  .caja.parcial{background:var(--verde-claro); border-color:var(--verde-claro)}
  .caja.parcial::after{content:"–"}
  .txt{flex:1 1 auto; font-size:14px}
  .item.hecha .txt b{text-decoration:line-through; color:var(--gris)}
  .txt b{font-weight:500}
  .n{display:block; font-size:11.5px; color:var(--gris); margin-top:2px}
  .quien-marco{display:block; font-size:10.5px; color:var(--azul); margin-top:3px}
  .tag{font-size:10.5px; font-weight:700; color:var(--azul); background:#E8F2FA;
       border-radius:5px; padding:1px 7px; margin-left:6px; white-space:nowrap}
  .aviso-item{padding:12px 14px; font-size:12.5px; color:var(--gris); font-style:italic}
  .partes{display:none; padding:0 14px 12px 44px}
  .item.abierta .partes{display:block}
  .parte{display:flex; gap:9px; align-items:flex-start; padding:5px 0; cursor:pointer;
         font-size:13px; color:var(--gris)}
  .parte .pc{width:16px; height:16px; flex:0 0 auto; border-radius:5px;
             border:1.5px solid var(--borde); margin-top:2px; display:flex;
             align-items:center; justify-content:center; font-size:9px; color:#fff}
  .parte.hecha .pc{background:var(--verde); border-color:var(--verde)}
  .parte.hecha .pc::after{content:"✓"}
  .parte.hecha{color:var(--tinta); text-decoration:line-through}
  .producto{display:flex; align-items:center; gap:8px; margin-top:9px; font-size:12.5px; color:var(--gris)}
  .producto select{border:1px solid var(--borde); border-radius:8px; padding:6px 9px;
                   font-family:inherit; font-size:12.5px; background:#fff; color:var(--tinta)}
</style>
</head>
<body>

<section id="login">
  <div class="caja-login">
    <div class="marca">
      <div class="cubo" id="logo-login" title=""><img src="__LOGO__" alt=""></div>
      <div><h1>Tienda Malato</h1><p>Las tareas del día</p></div>
    </div>

    <div class="rotulo">¿En qué puesto estás?</div>
    <div class="opciones" id="op-puesto"></div>

    <div class="rotulo">¿Cuál eres?</div>
    <div class="opciones" id="op-numero"></div>

    <div id="op-pin" hidden></div>

    <div id="caja-clave" hidden>
      <div class="rotulo">Clave</div>
      <input type="password" id="pin-inp" autocomplete="off" placeholder="••••••••">
      <button class="entrar" id="btn-clave">Entrar</button>
      <p class="aviso-mini" id="aviso-pin"></p>
    </div>

    <button class="entrar" id="btn-entrar" disabled>Entrar</button>
    <p class="aviso-mini" id="aviso-pin"></p>
    <p class="aviso-mini">Lo que marques lo verán las demás al momento.</p>
  </div>
</section>

<section id="app" hidden>
  <header>
    <div class="fila-sup">
      <div class="logo"><img src="__LOGO_VERDE__" alt=""></div>
      <div><h1 id="titulo">Tienda Malato</h1><div class="sub" id="sub"></div></div>
      <div class="quien"><b id="q-nombre">—</b><span id="q-hora"></span>
        <button id="btn-salir">Salir</button></div>
    </div>
    <div class="prog">
      <div class="txt"><span id="ptxt">0 de 0</span><span id="ppct">0 %</span></div>
      <div class="barra"><i id="pbar"></i></div>
    </div>
  </header>

  <div class="estado-sync"><span class="punto" id="punto"></span><span id="txt-sync">Conectando…</span></div>

  <div id="fallo"><b>La aplicación ha tenido un fallo</b><span></span></div>
<main>
    <div class="tabs" id="tabs"></div>
    <div id="subopciones"></div>
    <div id="cuerpo"></div>
  </main>
</section>

<footer id="pie"><span id="version"></span></footer>

<script>
const DATOS = __DATOS__;
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
const HOY_SEMANA = ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date().getDay()];

let quien = null;          // { puesto, numero, id }
let DIA = "";              // AAAA-MM-DD de hoy, lo dice el servidor
let fechaSel = "";         // el día que se está mirando
let marcas = {};           // lo que hay guardado (compartido)
let traslados = {};        // claves con «para cuándo»
let notas = {};            // el calendario: { "AAAA-MM-DD": [ {id,q,t,a,h} ] }
let encargos = [];         // tareas que alguien manda a otro puesto
const OPCIONES = {};       // lo elegido en cada desplegable
let textoNota = "", ambitoNota = "general";
let formTarea = false, textoTarea = "", puestoTarea = "tienda";
let formOfertas = false, ofertasDesde = "", ofertasHasta = "", ofertasTitulo = "";
let recuentos = {};   // el recuento del lunes, por fecha del lunes
let tahona = {};      // el pan del panadero, por fecha
let encargosFecha = [];   // los encargos: series con fecha
let agenda = [];          // los proveedores, con sus teléfonos
let turnoTarea = "", tipoTarea = "extra";
/* la cascada que se está montando: cuando se haga esta tarea, qué nace */
let cascHijos = [];
const NOMBRE_PUESTO = { tienda: "Tienda", coordinacion: "Coordinación", gerencia: "Gerencia" };
let versionVista = -1;
let pendientes = {};       // cambios sin enviar
let tab = "", patron = (HOY_SEMANA === "DOM" ? "B" : "A");
let estadoSync = "trabajando";
const REG = {};
const ARR = {};   // pendientes sin día: clave -> {t, f, k, partes, hechasN}
const PAS = {};   // pasadas a este día
const OPC = {};   // opciones del menú de pasar
const PICK = {};  // qué menú está abierto
const ENC = {};   // tareas extra en pantalla

/* ------------------------------------------------------------------ entrar */
const PUESTOS = [["tienda","Tienda",3],["coordinacion","Coordinación",2]];
let selPuesto = null, selNumero = null;
let errorPin = "";

/* La clave de la Jefa, una vez metida, vale hasta las 15:00 del día. */
function horaCierreJefa(){
  const d = new Date();
  d.setHours(15, 0, 0, 0);
  return d.getTime();
}

function gerenciaAbierta(){
  try{
    const hasta = Number(localStorage.getItem("gerencia-hasta") || 0);
    return hasta > Date.now();
  }catch(e){ return false; }
}

function recordarGerencia(abrir){
  try{
    if(abrir) localStorage.setItem("gerencia-hasta", String(horaCierreJefa()));
    else localStorage.removeItem("gerencia-hasta");
  }catch(e){}
}

function pintarLogin(){
  const c1 = document.getElementById("op-puesto"); c1.innerHTML = "";
  PUESTOS.forEach(([k,n])=>{
    const b = document.createElement("button");
    b.className = "op"; b.type = "button"; b.textContent = n;
    b.setAttribute("aria-pressed", k === selPuesto);
    b.addEventListener("click", ()=>{ selPuesto = k; selNumero = null; pintarLogin(); });
    c1.appendChild(b);
  });
  const c2 = document.getElementById("op-numero"); c2.innerHTML = "";
  const cuantos = selPuesto ? (PUESTOS.find(p=>p[0]===selPuesto)[2]) : 0;
  if(!cuantos){
    c2.innerHTML = '<span class="aviso-mini" style="margin:0">Elige primero el puesto.</span>';
  }
  for(let i = 1; i <= cuantos; i++){
    const b = document.createElement("button");
    b.className = "op"; b.type = "button"; b.textContent = i;
    b.setAttribute("aria-pressed", i === selNumero);
    b.addEventListener("click", ()=>{ selNumero = i; pintarLogin(); });
    c2.appendChild(b);
  }
  const c3 = document.getElementById("op-pin"); c3.hidden = true; c3.innerHTML = "";
  document.getElementById("btn-entrar").disabled = !(selPuesto && selNumero);
}

document.getElementById("btn-entrar").addEventListener("click", ()=>{
  quien = { puesto: selPuesto, numero: selNumero,
            id: (selPuesto === "tienda" ? "op" : "co") + selNumero };
  try { localStorage.setItem("tienda-quien", JSON.stringify(quien)); } catch(e){}
  entrar();
});

/* ---------------------------------------------- la puerta escondida del logo */
document.getElementById("logo-login").addEventListener("click", ()=>{
  /* si ya se metió la clave y no son las 15:00, no se vuelve a pedir */
  if(gerenciaAbierta()){
    quien = { puesto: "gerencia", numero: 1, id: "ge1" };
    try { localStorage.setItem("tienda-quien", JSON.stringify(quien)); } catch(e){}
    entrar();
    return;
  }
  const caja = document.getElementById("caja-clave");
  caja.hidden = !caja.hidden;
  if(!caja.hidden){
    const i = document.getElementById("pin-inp");
    i.value = ""; document.getElementById("aviso-pin").textContent = "";
    i.focus();
  }
});

document.getElementById("btn-clave").addEventListener("click", async ()=>{
  const pin = document.getElementById("pin-inp").value;
  const aviso = document.getElementById("aviso-pin");
  aviso.textContent = "";
  document.getElementById("btn-clave").disabled = true;
  try{
    const r = await fetch("/api/entrar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin: pin })
    });
    const d = await r.json();
    if(!d.ok){
      aviso.textContent = "Esa clave no es.";
      document.getElementById("btn-clave").disabled = false;
      return;
    }
  }catch(e){
    aviso.textContent = "Sin conexión. Inténtalo otra vez.";
    document.getElementById("btn-clave").disabled = false;
    return;
  }
  document.getElementById("btn-clave").disabled = false;
  document.getElementById("caja-clave").hidden = true;
  recordarGerencia(true);
  quien = { puesto: "gerencia", numero: 1, id: "ge1" };
  try { localStorage.setItem("tienda-quien", JSON.stringify(quien)); } catch(e){}
  entrar();
});

document.getElementById("pin-inp").addEventListener("keydown", e=>{
  if(e.key === "Enter"){ e.preventDefault(); document.getElementById("btn-clave").click(); }
});
document.getElementById("btn-salir").addEventListener("click", async ()=>{
  /* sin reloj: el turno lo pone la plantilla */
  if(quien && quien.puesto === "gerencia") recordarGerencia(false);
  try { localStorage.removeItem("tienda-quien"); } catch(e){}
  quien = null; document.getElementById("app").hidden = true;
  document.getElementById("login").hidden = false; pintarLogin();
});

/* ------------------------------------------------------------------ sincronizar */
/* un aviso que se ve siempre, arriba, cuando algo se guarda */
function toast(texto, malo){
  let caja = document.getElementById("toast");
  if(!caja){
    caja = document.createElement("div");
    caja.id = "toast";
    document.body.appendChild(caja);
  }
  caja.className = "toast" + (malo ? " malo" : "");
  caja.textContent = (malo ? "⚠ " : "✓ ") + texto;
  caja.style.display = "block";
  clearTimeout(toast.tiempo);
  toast.tiempo = setTimeout(()=>{ caja.style.display = "none"; }, 2600);
}

function ponerSync(estado, texto){
  estadoSync = estado;
  const p = document.getElementById("punto");
  if(p){ p.className = "punto " + estado; }
  const tx = document.getElementById("txt-sync");
  if(tx){ tx.textContent = texto; }
  /* todo lo que se guarda avisa, y se ve: no hay que adivinar si guardó */
  if(estado === "ok" || estado === "error") toast(texto, estado === "error");
}

async function cargar(){
  try{
    const r = await fetch("/api/estado", { cache: "no-store" });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.dia) DIA = d.dia;
    if(d.version >= versionVista){
      marcas = d.marcas || {};
      traslados = d.traslados || {};
      notas = d.notas || {};
      encargos = d.encargos || [];
      recuentos = d.recuentos || {};
      tahona = d.tahona || {};
      encargosFecha = d.encargosFecha || [];
      proveedores = d.proveedores || [];
      cascadas = d.cascadas || {};
      plantilla = d.plantilla || {};
      aplicarPlantilla();
      versionVista = d.version;
    }
    ponerSync("ok", "Al día · se guarda en la nube");
    return true;
  }catch(e){
    ponerSync("error", "Sin conexión · se guardará al volver");
    return false;
  }
}

let temporizador = null;
function programarEnvio(){
  if(temporizador) clearTimeout(temporizador);
  temporizador = setTimeout(enviar, 700);
}

async function enviar(){
  const cambios = pendientes;
  pendientes = {};
  if(!Object.keys(cambios).length) return;
  ponerSync("trabajando", "Guardando…");
  try{
    const r = await fetch("/api/marcas", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, cambios: cambios })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Guardado");
  }catch(e){
    // no se pierde: vuelve a la cola
    Object.assign(pendientes, cambios);
    ponerSync("error", "No se pudo guardar · se reintenta");
    setTimeout(enviar, 4000);
  }
}

/* vuelve a preguntar cada 5 s, para ver lo que marcan las demás */
setInterval(async ()=>{
  if(!quien) return;
  if(Object.keys(pendientes).length) return;
  const antes = versionVista;
  await cargar();
  if(versionVista !== antes) pinta();
}, 5000);

/* ------------------------------------------------------------------ fechas */
/* Una fecha que no vale rompe todo lo que venga detrás: el cálculo del
   turno acaba leyendo de undefined y la aplicación se cae. */
function fechaBuena(f){
  return /^\d{4}-\d{2}-\d{2}$/.test(String(f || "")) ? String(f) : DIA;
}

function semanaDe(f){                     // "2026-10-22" -> "JUE"
  f = fechaBuena(f);
  const [a, m, d] = f.split("-").map(Number);
  return ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date(a, m - 1, d).getDay()];
}
function sumarDias(f, n){
  f = fechaBuena(f);
  const [a, m, d] = f.split("-").map(Number);
  const x = new Date(a, m - 1, d);
  x.setDate(x.getDate() + n);
  return x.toLocaleDateString("en-CA");
}
function bonito(f){
  f = fechaBuena(f);
  const [a, m, d] = f.split("-").map(Number);
  return d + " de " + ["enero","febrero","marzo","abril","mayo","junio","julio",
    "agosto","septiembre","octubre","noviembre","diciembre"][m - 1];
}

/* ------------------------------------------------------------------ claves */
function prefijoPuesto(){ return quien.puesto === "tienda" ? "op" : "co"; }
function claveEn(f, k){ return f + "|" + prefijoPuesto() + "|" + k; }
function hechaEn(f, k){ return !!marcas[claveEn(f, k)]; }
function clave(k){ return claveEn(fechaSel, k); }
function hecha(k){ return !!marcas[clave(k)]; }
function tocarEn(f, k, valor){
  const c = claveEn(f, k);
  if(valor){ marcas[c] = { q: quien.id, h: new Date().toLocaleTimeString("es-ES",
              { hour:"2-digit", minute:"2-digit" }) }; }
  else { delete marcas[c]; }
  pendientes[c] = !!valor;
  pinta();
  programarEnvio();
}
/* ---------------------------------------------------------- LAS CASCADAS
   Una tarea que, al hacerse, hace nacer la siguiente.
   El hijo NO EXISTE hasta que el padre se hace. */
let cascadas = {};
const TXTENC = {};        /* id del encargo -> su texto, para lanzar la cascada */

async function lanzarCascada(tarea, fecha){
  if(!tarea) return;
  try{
    const r = await fetch("/api/cascada-lanzar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, tarea: tarea, fecha: fecha || fechaSel })
    });
    if(!r.ok) return;
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    const nacidos = d.nacidos || [];
    if(nacidos.length){
      ponerSync("ok", "Ha nacido: " + nacidos.map(x => x.t).join(" · "));
      pinta();
    }
  }catch(e){ /* si falla, no se rompe la tarea que sí se marcó */ }
}

function tocar(k, valor){
  tocarEn(fechaSel, k, valor);
  /* si esta tarea tiene cascada y se acaba de hacer, nacen las siguientes */
  if(valor && REG[k]) lanzarCascada(REG[k].t, fechaSel);
  /* hay tareas que, al hacerse, mandan un encargo a otro puesto */
  const t = REG[k];
  if(valor && t && t.avisa === "bolleria"){
    mandarEncargo({
      t: "Etiquetar la bollería a granel",
      p: "gerencia",
      diario: true,
      clave: "bolleria:" + fechaSel,
      que: OPCIONES[k] || ""
    });
  }
}

async function mandarEncargo(c){
  ponerSync("trabajando", "Pasando el encargo…");
  try{
    const r = await fetch("/api/encargo", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.assign({ quien: quien.id, f: DIA }, c))
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Encargo pasado");
    pinta();
  }catch(e){ ponerSync("error", "No se pudo pasar el encargo"); }
}

async function encargoHecho(id, deshacer){
  /* una llamada no se tacha sin apuntar lo que dijeron */
  if(!deshacer){
    const e = (encargos || []).find(x => String(x.id) === String(id));
    if(e && e.tipo === "llamada" && !String(e.respuesta || "").trim()){
      ponerSync("error", "Apunta primero la respuesta de la llamada");
      return;
    }
  }
  ponerSync("trabajando", deshacer ? "Deshaciendo…" : "Marcando…");
  try{
    const r = await fetch("/api/encargo-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, quien: quien.id, deshacer: !!deshacer })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Hecho");
    pinta();
    /* si esta tarea extra tiene cascada y se acaba de hacer, nacen las siguientes */
    if(!deshacer && TXTENC[id]) lanzarCascada(TXTENC[id], DIA);
  }catch(e){ ponerSync("error", "No se pudo marcar"); }
}

async function encargoBorrar(id){
  ponerSync("trabajando", "Borrando el encargo…");
  try{
    const r = await fetch("/api/encargo-borrar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Encargo borrado");
    pinta();
  }catch(e){ ponerSync("error", "No se pudo borrar"); }
}

/* Los encargos de un puesto: los de ese día, y los que son «hasta que se haga». */
async function moverEncargo(id, f){
  ponerSync("trabajando", "Pasando la tarea…");
  try{
    const r = await fetch("/api/encargo-mover", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, f: f })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Pasada al " + bonito(f));
  }catch(e){
    ponerSync("error", "No se pudo pasar");
  }
  pinta();
}

function bloqueEncargos(puesto, fecha, turno, titulo){
  /* el turno NO esconde la tarea: se ve en las dos pestañas y el turno va escrito.
     Esconderla seria peor que repetirla. */
  const lista = (encargos || []).filter(e => !e.hecho && e.p === puesto &&
    (e.diario || e.f === fecha));
  if(!lista.length) return "";
  let html = "";
  lista.forEach((e, i)=>{
    const k = "enc" + i;
    ENC[k] = e;
    const que = e.que ? `<span class="n">${e.que}</span>` : "";
    const cuando = e.diario ? "hasta que se haga · sale todos los días"
                            : (e.f ? "para el " + bonito(e.f) : "");
    const turnoTxt = e.turno === "tarde" ? " · por la tarde"
                   : e.turno === "manana" ? " · por la mañana" : "";
    const de = "la puso " + nombreDe(e.q) + (e.h ? " · " + e.h : "") + turnoTxt;
    const urgente = e.tipo === "urgente" || e.urgente === true;
    const arreglo = e.tipo === "arreglar";
    const etiqueta = urgente ? `<span class="tag urgente">URGENTE</span>`
                   : arreglo ? `<span class="tag arreglar">PARA ARREGLAR</span>` : "";
    /* se puede pasar a otro día, igual que las del día */
    const mover = `<div class="pasarlo"><span class="pista">Si no da tiempo:</span>` +
      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}"` +
      ` onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)"` +
      ` title="Pasarlo a otro día"></div>`;
    const borrar = (quien.puesto === "gerencia")
      ? `<div class="pasarlo"><button class="btn-borrar" data-borrar-enc="${e.id}">Borrar</button></div>`
      : "";
    html += `<div class="item ${urgente ? "es-urgente" : ""}${arreglo ? " es-arreglar" : ""} es-extra" data-k="${k}">
        <div class="cab-item" onclick="encargoHecho('${e.id}')"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${etiqueta}${que}
        <span class="extra-de">${de}</span></span></div>${mover}${borrar}</div>`;
  });
  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino: va a SIN HACER.
   La rutina y el «antes de irse» NO se arrastran nunca. */
/* El día en que se empezó a usar de verdad. Antes de esa fecha no se mira
   hacia atrás: lo de antes fueron pruebas y aparecía como «sin hacer». */
const ARRANQUE = "2026-10-26";
const DIAS_ATRAS = 7;

function tablaDia(){
  if(quien.puesto === "tienda"){
    return (tab && DATOS.tienda[tab] && DATOS.tienda[tab].porDia) || null;
  }
  return DATOS.coordinacion.dia.porDia;
}

function sinDia(pre){
  const salida = [];
  const tabla = tablaDia();
  if(!tabla) return salida;
  for(let i = 1; i <= DIAS_ATRAS; i++){
    const f = sumarDias(fechaSel, -i);
    if(f < ARRANQUE) continue;          // lo de antes del arranque no cuenta
    const lista = tabla[semanaDe(f)] || [];
    lista.forEach((t, idx)=>{
      if(t.aviso) return;
      const k = pre + idx;
      const ck = claveEn(f, k);
      if(traslados[ck]) return;            // ya tiene destino
      const partes = t.partes || [];
      const hn = partes.filter((_, j) => hechaEn(f, k + "." + j)).length;
      if(partes.length ? hn === partes.length : hechaEn(f, k)) return;  // ya está hecha
      salida.push({ t: t, f: f, k: k, partes: partes, hechasN: hn });
    });
  }
  return salida;
}

/* Las que se pasaron a la fecha que se está mirando. */
function pasadasA(){
  const salida = [];
  const tabla = tablaDia();
  if(!tabla) return salida;
  for(const ck in traslados){
    const tr = traslados[ck];
    if(!tr || !tr.f || tr.f !== fechaSel) continue;
    const trozos = ck.split("|");
    const f = trozos[0], k = trozos[2];
    if(!k) continue;
    const lista = tabla[semanaDe(f)] || [];
    const idx = parseInt(String(k).replace(/^[a-z]+/, ""), 10);
    const t = lista[idx];
    if(!t || t.aviso) continue;
    const tabOrigen = quien.puesto === "tienda" ? (k[0] === "m" ? "manana" : "tarde") : "dia";
    const tabDestino = tr.t || tabOrigen;
    if(tabDestino !== tab) continue;
    if(hechaEn(f, k)) continue;
    salida.push({ t: t, f: f, k: k, partes: t.partes || [],
                  hechasN: (t.partes || []).filter((_, j) => hechaEn(f, k + "." + j)).length });
  }
  return salida;
}

/* ------------------------------------------------------------------ pintar */
/* ---------------------------------------------------------- desplegar bloques
   Un bloque enseña solo su título y cómo va. Se abre al tocarlo.
   Cuando está completo se cierra solo y lo dice. */
let PLEGADOS = {};      /* clave del bloque -> true si está cerrado */

function claveBloque(pre, titulo){
  return pre + "|" + titulo;
}

function plegar(clave){
  PLEGADOS[clave] = !PLEGADOS[clave];
  pinta();
}

/* cuántas van hechas de este bloque */
function cuentaBloque(tareas, pre){
  let tot = 0, hec = 0;
  (tareas || []).forEach((t, i)=>{
    if(t.aviso) return;
    const k = pre + i, partes = t.partes || [];
    if(partes.length){
      tot += partes.length;
      partes.forEach((_, j)=>{ if(hecha(k + "." + j)) hec++; });
    } else {
      tot += 1;
      if(hecha(k)) hec++;
    }
  });
  return { tot: tot, hec: hec };
}

function bloque(titulo, tareas, pre, extra){
  if(!tareas || !tareas.length) return extra || "";
  const cuenta = cuentaBloque(tareas, pre);
  const completo = cuenta.tot > 0 && cuenta.hec === cuenta.tot;
  const claveB = claveBloque(pre, titulo);
  /* por defecto, cerrados. Los completos, siempre cerrados. */
  /* aunque esté terminado se puede abrir: para mirar y para corregir */
  const cerrado = (PLEGADOS[claveB] === undefined) ? true : PLEGADOS[claveB];
  const comoVa = completo
    ? `<small class="bloque-ok">✓ completo</small>`
    : `<small>${cuenta.hec} de ${cuenta.tot}</small>`;
  let html = `<h2 class="bloque plega${completo ? " hecho" : ""}" ` +
    `onclick="plegar('${claveB}')">` +
    `<span class="flecha">${cerrado ? "▸" : "▾"}</span>` +
    `<span class="bloque-tit">${titulo}</span>${comoVa}</h2>`;
  /* Se pinta todo y, si está cerrado, se corta por la marca.
     Antes solo se saltaba la cabecera y las tareas salían igual. */
  const MARCA = "\u00A7CORTE\u00A7";
  html += cerrado ? MARCA : `<div class="lista">`;
  tareas.forEach((t, i)=>{
    if(t.aviso){ html += `<div class="aviso-item">${t.aviso}</div>`; return; }
    const k = pre + i; REG[k] = t;
    const partes = t.partes || [];
    const hp = partes.filter((_, j) => hecha(k + "." + j)).length;
    const abierta = hecha("ab:" + k);
    const completa = partes.length ? hp === partes.length : hecha(k);
    const parcial = partes.length && hp > 0 && hp < partes.length;
    let sub = "";
    if(partes.length){
      sub = `<div class="partes">` + partes.map((p, j)=>
        `<div class="parte ${hecha(k+"."+j)?"hecha":""}" data-parte="${k+"."+j}">
           <span class="pc"></span><span>${p}</span></div>`).join("");
      if(t.producto){
        sub += `<div class="producto"><span>Con qué producto:</span><select>` +
          (DATOS.tienda.productos || []).map(x=>`<option>${x}</option>`).join("") +
          `</select></div>`;
      }
      sub += `</div>`;
    }
    /* desplegable de opciones: el tipo de bollería, por ejemplo */
    if(t.opciones && t.opciones.length){
      sub += `<div class="producto"><span>¿Cuál?</span>` +
        `<select data-opciones="${k}"><option value="">— elige —</option>` +
        t.opciones.map(x=>`<option>${x}</option>`).join("") + `</select></div>`;
    }
    const m = marcas[clave(k)];
    const quienMarco = (m && m.q) ? `<span class="quien-marco">${nombreDe(m.q)} · ${m.h||""}</span>` : "";
    const tag = partes.length ? `<span class="tag">${hp} / ${partes.length} partes</span>` : "";
    const n = t.n ? `<span class="n">${t.n}</span>` : "";
    html += `<div class="item ${completa?"hecha":""} ${abierta?"abierta":""}" data-k="${k}">
        <div class="cab-item"><span class="caja ${parcial?"parcial":""}"></span>
        <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}` + lineaCascada(k, t.t) + `<div class="casc-linea">` +
           `<button class="btn-add-2" type="button" onclick="abrirPlantilla('${k}')">` +
           `✎ cambiar</button></div>` + `</div>`;
  });
  /* si el bloque está cerrado, se corta por la marca: solo queda el título */
  if(cerrado){
    const i = html.indexOf(MARCA);
    if(i >= 0) html = html.slice(0, i);
    return html;
  }
  return html + "</div>";
}

/* El bloque de lo que se quedó sin hacer, con el día del que viene. */
/* LO QUE VIENE · tareas extra de días futuros.
   Es un bloque CERRADO: solo se mira. No se marca y no se mezcla con lo de hoy,
   para que la pantalla del día siga pudiendo terminarse. */
function bloqueViene(desde, dias){
  dias = dias || 21;
  const hasta = sumarDias(desde, dias);
  const fut = (encargos || [])
    .filter(e => !e.hecho && e.f && e.f > desde && e.f <= hasta)
    .sort((a, b) => a.f < b.f ? -1 : a.f > b.f ? 1 : 0);
  if(!fut.length) return "";
  let html = `<h2 class="bloque bloque-viene">Viene en los próximos días` +
    `<small>${fut.length} ${fut.length === 1 ? "tarea" : "tareas"} · solo para mirar</small></h2>` +
    `<div class="lista lista-viene">`;
  fut.forEach(e=>{
    const w = semanaDe(e.f);
    html += `<div class="viene-fila">
        <span class="viene-dia">${DIAS.find(x=>x[0]===w)[1].slice(0,3)} ${e.f.slice(8)}/${e.f.slice(5,7)}</span>
        <span class="viene-que">${e.t}</span>
        <span class="viene-quien">${NOMBRE_PUESTO[e.p] || e.p}</span></div>`;
  });
  html += `</div>`;
  return html;
}

/* Las ofertas ya dadas de alta, para meterlas DENTRO del bloque «Las ofertas».
   Cada una lleva su título (que ya incluye las fechas) y el día en que toca.
   Se ordenan por fecha; si coinciden, por título. No se marcan: son un registro. */
function listaOfertas(){
  /* se ordenan por la fecha de INICIO de la oferta, que va dentro de la clave
     (ofertas:AAAA-MM-DD:prep) — no por el día en que se dio de alta. */
  const inicioDe = (e) => String(e.clave || "").split(":")[1] || String(e.f || "");
  const ofs = (encargos || [])
    .filter(e => String(e.clave || "").endsWith(":prep"))
    .sort((a, b) => inicioDe(a).localeCompare(inicioDe(b)) ||
                    String(a.t || "").localeCompare(String(b.t || "")));
  if(!ofs.length) return "";
  let html = `<div class="ofertas-hechas"><span class="ofertas-cab">` +
    `Dadas de alta · ${ofs.length}</span>`;
  ofs.forEach(e=>{
    const inicio = inicioDe(e);
    const w = semanaDe(inicio);
    html += `<div class="viene-fila">
        <span class="viene-dia">${DIAS.find(x=>x[0]===w)[1].slice(0,3)} ${inicio.slice(8)}/${inicio.slice(5,7)}</span>
        <span class="viene-que">${e.t}</span>
        <span class="viene-quien">${e.hecho ? "preparada" : "pendiente"}</span></div>`;
  });
  html += `</div>`;
  return html;
}

/* ---------------------------------------------------------- el recuento del lunes
   Lo que sobró del asador el fin de semana: es el stock inicial antes de pedir.
   Lo cuenta tienda el lunes, lo apunta coordinación, y la Jefa lo mira el jueves
   para hacer los pedidos. */
const RECUENTO_CAMPOS = [
  ["pollos", "Pollos"], ["codillos", "Codillos"],
  ["patatas", "Patatas normales"], ["bravas", "Patatas bravas"]
];

/* el lunes de la semana de una fecha */
function lunesDe(f){
  f = fechaBuena(f);
  const [a, m, d] = f.split("-").map(Number);
  const x = new Date(a, m - 1, d);
  const w = (x.getDay() + 6) % 7;          // lunes = 0
  x.setDate(x.getDate() - w);
  return x.toLocaleDateString("en-CA");
}

function ddmm(f){ return f ? f.slice(8) + "/" + f.slice(5, 7) : ""; }

/* editable: puede apuntar los números. conHistorico: enseña los lunes anteriores. */
async function aprobarRecuento(){
  const lunes = lunesDe(fechaSel);
  ponerSync("trabajando", "Dando el visto bueno…");
  try{
    const r = await fetch("/api/recuento-aprobar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: lunes })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    recuentos = d.recuentos || {};
    ponerSync("ok", "Visto bueno dado");
  }catch(e){
    ponerSync("error", "No se pudo dar el visto bueno");
  }
  pinta();
}

function bloqueRecuento(editable, conHistorico){
  const lunes = lunesDe(fechaSel);
  const r = (recuentos || {})[lunes] || null;
  const sinVisto = r && !r.aprobado;
  let html = `<h2 class="bloque">Recuento del lunes ${ddmm(lunes)}` +
    `<small>${r ? "apuntado por " + nombreDe(r.q) + " · " + (r.h || "") +
                  (r.aprobado ? "  ·  con el visto bueno de " + nombreDe(r.qAprueba)
                              : "  ·  SIN visto bueno")
                : "sin apuntar"}</small></h2>`;
  html += `<div class="lista"><div class="recuento">`;
  RECUENTO_CAMPOS.forEach(([k, nombre])=>{
    const v = r && r[k] !== undefined ? r[k] : "";
    if(editable){
      html += `<label class="rec-campo"><span>${nombre}</span>` +
        `<input type="number" min="0" step="0.5" inputmode="decimal" ` +
        `data-rec="${k}" value="${v}"></label>`;
    } else {
      html += `<div class="rec-campo"><span>${nombre}</span>` +
        `<b>${v === "" ? "—" : v}</b></div>`;
    }
  });
  html += `</div>`;
  if(editable){
    html += `<p class="pista">Lo que ha sobrado del asador el fin de semana.` +
      ` Es el stock del que se parte para pedir.</p>` +
      `<button id="rec-guardar" class="btn-add" type="button"
        onclick="guardarRecuento()">Guardar el recuento</button>`;
    /* coordinación da el visto bueno */
    if(sinVisto && quien.puesto === "coordinacion"){
      html += ` <button id="rec-ok" class="btn-add" type="button" ` +
        `onclick="aprobarRecuento()" ` +
        `style="background:linear-gradient(135deg,#2E7D32,#1B5E20)">` +
        `Dar el visto bueno</button>`;
    }
  }
  html += `</div>`;

  /* el histórico, para poder pedir mirando cómo han ido los lunes anteriores */
  if(conHistorico){
    const lunesTodos = Object.keys(recuentos || {}).sort().reverse().slice(0, 8);
    if(lunesTodos.length){
      html += `<h2 class="bloque bloque-viene">Los lunes anteriores` +
        `<small>${lunesTodos.length} · de más reciente a más antiguo</small></h2>` +
        `<div class="lista lista-viene"><div class="rec-tabla">` +
        `<div class="rec-fila rec-cab"><span>Lunes</span><span>Pollos</span>` +
        `<span>Codillos</span><span>Patatas</span><span>Bravas</span></div>`;
      lunesTodos.forEach(f=>{
        const x = recuentos[f] || {};
        html += `<div class="rec-fila ${f === lunes ? "rec-hoy" : ""}">` +
          `<span>${ddmm(f)}</span><span>${x.pollos ?? "—"}</span>` +
          `<span>${x.codillos ?? "—"}</span><span>${x.patatas ?? "—"}</span>` +
          `<span>${x.bravas ?? "—"}</span></div>`;
      });
      html += `</div></div>`;
    }
  }
  return html;
}

async function guardarRecuento(){
  const vals = {};
  document.querySelectorAll("[data-rec]").forEach(i=>{ vals[i.dataset.rec] = i.value; });
  const lunes = lunesDe(fechaSel);
  const jueves = sumarDias(lunes, 3);
  ponerSync("trabajando", "Guardando el recuento…");
  try{
    const r = await fetch("/api/recuento", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: lunes, valores: vals })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    recuentos = d.recuentos || {};
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Recuento guardado");
    /* la cascada: al apuntarlo, la Jefa recibe el encargo del jueves */
    await mandarEncargo({
      t: "Hacer los pedidos con el recuento del " + ddmm(lunes),
      p: "gerencia", f: jueves, clave: "recuento:" + lunes + ":pedido",
      partes: ["Mirar el recuento del lunes", "Hacer los pedidos"]
    });
  }catch(e){
    ponerSync("error", "No se pudo guardar el recuento");
  }
  pinta();
}

/* ---------------------------------------------------------- la tahona
   El pan del panadero: entra por la mañana y se devuelve lo que no se vende.
   A fin de mes se suma entradas y se restan devoluciones, para cotejar con su factura. */
function euros(n){
  if(n === null || n === undefined || n === "") return "—";
  return Number(n).toFixed(2).replace(".", ",") + " €";
}

const PANES_TAHONA = [
  ["txapata", "Txapata"], ["txapatita", "Txapatita"], ["barra", "Barra"],
  ["cuarto", "Cuarto"], ["txoripan", "Txoripan"]
];

function bloqueTahona(cual){
  /* cual: "entrada" (coordinación, por la mañana) o "devolucion" (tienda, por la tarde) */
  const esEntrada = cual === "entrada";
  const dia = (tahona || {})[fechaSel] || {};
  const valores = dia[cual] || {};
  const apuntado = PANES_TAHONA.some(([k]) => valores[k] !== null && valores[k] !== undefined);
  const titulo = esEntrada ? "Tahona · entrada del pan" : "Tahona · devolución";
  const pista = esEntrada
    ? "Lo que trae el panadero por la mañana."
    : "Lo que se le devuelve por la noche.";
  let html = `<h2 class="bloque">${titulo}<small>${
    apuntado ? "apuntado" : "sin apuntar"}</small></h2>`;
  html += `<div class="lista"><div class="recuento tahona">`;
  PANES_TAHONA.forEach(([k, nombre])=>{
    const v = valores[k];
    html += `<label class="rec-campo"><span>${nombre}</span>` +
      `<input type="number" min="0" step="1" inputmode="numeric" ` +
      `data-tah="${k}" value="${v !== null && v !== undefined ? v : ""}"></label>`;
  });
  html += `</div>`;
  html += `<p class="pista" style="padding:0 14px">${pista}</p>`;
  html += `<div class="nueva-nota" style="border:none; margin-top:0">` +
    `<button id="tah-guardar" class="btn-add" type="button" ` +
    `data-cual="${cual}" onclick="guardarTahona(this.dataset.cual)">` +
    `Guardar el pan</button>` +
    (dia["guardado_" + cual]
      ? `<span class="guardado">✓ guardado a las ${dia["guardado_" + cual]}</span>` : "") +
    `</div></div>`;
  return html;
}

/* el resumen del mes anterior: solo para la Jefa, del 1 al 5 */
/* ---------------------------------------------------- sacar el informe fuera
   El texto de WhatsApp NO lleva columnas: WhatsApp usa una letra de ancho
   distinto para cada carácter, así que alinear con espacios es imposible.
   Va una línea por pan con el neto, que se lee bien en cualquier móvil. */
const MESES_LARGOS = ["enero","febrero","marzo","abril","mayo","junio","julio",
                      "agosto","septiembre","octubre","noviembre","diciembre"];

let panDesde = "", panHasta = "";     /* el rango del informe */
let panCorrige = "";                  /* el día que se está corrigiendo */

function mesPan(){
  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7));
  if(diaMes <= 5){ m = m - 1; if(m < 1){ m = 12; a--; } }
  const pref = a + "-" + String(m).padStart(2, "0");
  return { a: a, m: m, prefijo: pref,
           nombre: MESES_LARGOS[m - 1] + " de " + a,
           desde: pref + "-01",
           hasta: pref + "-" + String(new Date(a, m, 0).getDate()).padStart(2, "0") };
}

/* el rango que se está mirando (por defecto, el mes) */
function rangoPan(){
  const mes = mesPan();
  const d = /^\d{4}-\d{2}-\d{2}$/.test(panDesde) ? panDesde : mes.desde;
  const h = /^\d{4}-\d{2}-\d{2}$/.test(panHasta) ? panHasta : mes.hasta;
  return d <= h ? { desde: d, hasta: h } : { desde: h, hasta: d };
}

function diasPan(){
  const r = rangoPan();
  return Object.keys(tahona || {}).filter(f => f >= r.desde && f <= r.hasta).sort();
}

function filasPan(){
  const dias = diasPan();
  return PANES_TAHONA.map(([k, nombre])=>{
    let e = 0, d = 0;
    dias.forEach(f=>{
      const dia = tahona[f] || {};
      if(dia.entrada && dia.entrada[k]) e += Number(dia.entrada[k]);
      if(dia.devolucion && dia.devolucion[k]) d += Number(dia.devolucion[k]);
    });
    return { nombre: nombre, entra: e, sale: d, queda: e - d };
  });
}

function nombreRango(){
  const r = rangoPan();
  const dd = (f) => f.slice(8) + "/" + f.slice(5, 7);
  return "del " + dd(r.desde) + " al " + dd(r.hasta);
}

function textoPan(){
  const filas = filasPan();
  let te = 0, td = 0;
  let t = "MALATO · LA TAHONA\\n" + nombreRango() + "\\n\\n";
  filas.forEach(f=>{
    te += f.entra; td += f.sale;
    t += f.nombre + ": " + f.queda +
         (f.entra || f.sale ? "   (" + f.entra + " − " + f.sale + ")" : "") + "\\n";
  });
  t += "\\nTOTAL: " + (te - td) + "   (" + te + " − " + td + ")\\n";
  t += "\\nEntradas menos devoluciones. Unidades.";
  return t;
}

function csvPan(){
  const filas = filasPan();
  const r = rangoPan();
  let te = 0, td = 0;
  let c = "Malato · La tahona;" + nombreRango() + "\\n\\n";
  c += "Pan;Entra;Sale;Queda\\n";
  filas.forEach(f=>{
    te += f.entra; td += f.sale;
    c += f.nombre + ";" + f.entra + ";" + f.sale + ";" + f.queda + "\\n";
  });
  c += "TOTAL;" + te + ";" + td + ";" + (te - td) + "\\n";
  /* el detalle día a día, para poder cuadrar la factura */
  c += "\\nDía;Pan;Entra;Sale\\n";
  Object.keys(tahona || {}).filter(f => f >= r.desde && f <= r.hasta).sort()
    .forEach(f=>{
      const dia = tahona[f] || {};
      PANES_TAHONA.forEach(([k, nombre])=>{
        const e = (dia.entrada && dia.entrada[k]) || 0;
        const d = (dia.devolucion && dia.devolucion[k]) || 0;
        if(e || d) c += f + ";" + nombre + ";" + e + ";" + d + "\\n";
      });
    });
  return c;
}

async function compartirPan(){
  const texto = textoPan();
  try{
    if(navigator.share){
      await navigator.share({ title: "La tahona", text: texto });
      ponerSync("ok", "Compartido");
    }else{
      await navigator.clipboard.writeText(texto);
      ponerSync("ok", "Copiado · pégalo en WhatsApp");
    }
  }catch(e){
    if(String(e && e.name) === "AbortError") return;
    ponerSync("error", "No se pudo compartir");
  }
}

/* el detalle, para mandarselo al proveedor: una linea por pan y dia */
function csvDetalle(){
  const r = rangoPan();
  const filas = filasPan();
  const dd = (f) => f.slice(8) + "/" + f.slice(5, 7) + "/" + f.slice(0, 4);
  let c = "Malato · La tahona\\n";
  c += "Detalle del " + dd(r.desde) + " al " + dd(r.hasta) + "\\n\\n";
  c += "DIA;PAN;ENTRA;SALE\\n";
  let te = 0, td = 0;
  Object.keys(tahona || {}).filter(f => f >= r.desde && f <= r.hasta).sort()
    .forEach(f=>{
      const dia = tahona[f] || {};
      PANES_TAHONA.forEach(([k, nombre])=>{
        const e = (dia.entrada && dia.entrada[k]) || 0;
        const d = (dia.devolucion && dia.devolucion[k]) || 0;
        if(e || d){
          c += dd(f) + ";" + nombre + ";" + e + ";" + d + "\\n";
          te += e; td += d;
        }
      });
    });
  c += "\\nTOTAL;;" + te + ";" + td + "\\n\\n";
  c += "Entradas menos devoluciones: " + (te - td) + "\\n\\n";
  /* el resumen por pan, al final, para cuadrar de un vistazo */
  c += "PAN;ENTRA;SALE;QUEDA\\n";
  filas.forEach(f=>{ c += f.nombre + ";" + f.entra + ";" + f.sale + ";" + f.queda + "\\n"; });
  c += "TOTAL;" + te + ";" + td + ";" + (te - td) + "\\n";
  return c;
}

function descargarDetalle(){
  const csv = csvDetalle();
  const blob = new Blob(["\\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  const r = rangoPan();
  a.download = "tahona-detalle-" + r.desde + "-a-" + r.hasta + ".csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(()=> URL.revokeObjectURL(a.href), 2000);
  ponerSync("ok", "Detalle descargado");
}

function descargarPan(){
  const csv = csvPan();
  const blob = new Blob(["\\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  const r = rangoPan();
  a.download = "tahona-" + r.desde + "-a-" + r.hasta + ".csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(()=> URL.revokeObjectURL(a.href), 2000);
  ponerSync("ok", "Descargado para Excel");
}

/* corregir un día: se abre con sus diez casillas y se guarda tal cual */
async function guardarPanDia(dia){
  const ent = {}, dev = {};
  document.querySelectorAll("[data-pane]").forEach(i=>{ ent[i.dataset.pane] = i.value; });
  document.querySelectorAll("[data-pand]").forEach(i=>{ dev[i.dataset.pand] = i.value; });
  if(!Object.keys(ent).length && !Object.keys(dev).length){
    ponerSync("error", "No hay casillas que guardar");
    return;
  }
  ponerSync("trabajando", "Corrigiendo el " + dia + "…");
  try{
    for(const cual of ["entrada", "devolucion"]){
      const r = await fetch("/api/tahona", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quien: quien.id, fecha: dia, cual: cual,
                               valores: cual === "entrada" ? ent : dev })
      });
      if(!r.ok) throw new Error("HTTP " + r.status);
      const d = await r.json();
      tahona = d.tahona || {};
    }
    panCorrige = "";
    ponerSync("ok", "Corregido el " + dia);
  }catch(e){
    ponerSync("error", "No se pudo corregir");
  }
  pinta();
}

function bloqueTahonaResumen(){
  const mes = mesPan();
  const r = rangoPan();
  const filas = filasPan();
  const dias = diasPan();
  let html = `<h2 class="bloque bloque-viene">Tahona · el pan` +
    `<small>${nombreRango()} · entradas menos devoluciones</small></h2>`;

  /* el rango: de qué día a qué día */
  html += `<div class="lista lista-viene"><div class="nueva-nota">` +
    `<span class="pista">Desde</span>` +
    `<input type="date" id="pan-desde" value="${r.desde}" onchange="panDesde=this.value; pinta()">` +
    `<span class="pista">hasta</span>` +
    `<input type="date" id="pan-hasta" value="${r.hasta}" onchange="panHasta=this.value; pinta()">` +
    `<button class="btn-add-2" type="button" onclick="panDesde='${mes.desde}';` +
    `panHasta='${mes.hasta}'; pinta()">Este mes</button></div>`;

  html += `<div class="rec-tabla">` +
    `<div class="rec-fila rec-cab"><span>Pan</span><span>Entra</span>` +
    `<span>Sale</span><span>Queda</span><span></span></div>`;
  let totE = 0, totD = 0;
  filas.forEach(f=>{
    totE += f.entra; totD += f.sale;
    html += `<div class="rec-fila"><span>${f.nombre}</span><span>${f.entra}</span>` +
      `<span>${f.sale}</span><span><b>${f.queda}</b></span><span></span></div>`;
  });
  html += `<div class="rec-fila rec-hoy"><span>Total</span><span>${totE}</span>` +
    `<span>${totD}</span><span><b>${totE - totD}</b></span><span></span></div>`;
  html += `</div>`;

  /* los botones para sacarlo */
  html += `<div class="nueva-nota" style="border:none; margin-top:10px">` +
    `<button class="btn-add" type="button" onclick="compartirPan()">Compartir</button>` +
    `</div><div class="nueva-nota" style="border:none">` +
    `<button class="btn-add" type="button" onclick="descargarPan()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Resumen para Excel</button>` +
    ` <button class="btn-add" type="button" onclick="descargarDetalle()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Detalle por día para el proveedor</button>` +
    `</div>`;

  /* corregir: los días del rango, uno a uno */
  html += `</div><h2 class="bloque bloque-viene">Corregir un día` +
    `<small>si algún dato no cuadra con la factura</small></h2>` +
    `<div class="lista lista-viene"><div class="nueva-nota">` +
    `<span class="pista">Día</span>` +
    `<input type="date" id="pan-dia" value="${panCorrige || r.desde}" ` +
    `onchange="panCorrige=this.value; pinta()">` +
    `<button class="btn-add-2" type="button" onclick="panCorrige=document.getElementById('pan-dia').value; pinta()">Abrir</button>` +
    `</div>`;

  const f = panCorrige || "";
  if(f){
    const dia = (tahona || {})[f] || {};
    html += `<div class="rec-tabla"><div class="rec-fila rec-cab">` +
      `<span>Pan</span><span>Entrada</span><span></span>` +
      `<span>Devolución</span><span></span></div>`;
    PANES_TAHONA.forEach(([k, nombre])=>{
      const e = dia.entrada && dia.entrada[k] !== null && dia.entrada[k] !== undefined
        ? dia.entrada[k] : "";
      const d = dia.devolucion && dia.devolucion[k] !== null && dia.devolucion[k] !== undefined
        ? dia.devolucion[k] : "";
      html += `<div class="rec-fila"><span>${nombre}</span>` +
        `<span><input type="number" min="0" step="1" inputmode="numeric" ` +
        `data-pane="${k}" value="${e}" style="width:64px"></span><span></span>` +
        `<span><input type="number" min="0" step="1" inputmode="numeric" ` +
        `data-pand="${k}" value="${d}" style="width:64px"></span><span></span></div>`;
    });
    html += `</div><div class="nueva-nota" style="border:none">` +
      `<button class="btn-add" type="button" ` +
      `onclick="guardarPanDia('${f}')">Guardar ese día</button></div>`;
  }
  html += `</div>`;
  return html;
}

async function guardarTahona(cual){
  const valores = {};
  document.querySelectorAll("[data-tah]").forEach(i=>{ valores[i.dataset.tah] = i.value; });
  ponerSync("trabajando", "Guardando el pan…");
  try{
    const r = await fetch("/api/tahona", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: fechaSel, cual: cual, valores: valores })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    tahona = d.tahona || {};
    if(tahona[fechaSel]) tahona[fechaSel]["guardado_" + cual] = horaAhora();
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Pan guardado");
  }catch(e){
    ponerSync("error", "No se pudo guardar el pan");
  }
  pinta();
}

/* ---------------------------------------------------------- ¿algo para arreglar?
   Casi todos los días hay algo: un caducado, fruta con mala presencia…
   Lo apunta CUALQUIERA (sobre todo tienda) y NO desaparece hasta que se arregla.
   Va a coordinación, que es quien lo resuelve. */
let textoArreglo = "";

function bloqueArreglar(){
  return `<h2 class="bloque bloque-arreglar">Para arreglar` +
    `<small>lo ve coordinación · no desaparece hasta que se arregla</small></h2>` +
    `<div class="lista"><div class="nueva-nota" style="border:none; margin-top:0">` +
    `<input type="text" id="arr-txt" maxlength="200" ` +
    `placeholder="Un caducado, fruta con mala presencia…" value="${textoArreglo}">` +
    `<button id="arr-add" class="btn-add" type="button" onclick="anadirArreglo()">Apuntar</button></div>` +
    `<p class="pista" style="padding:0 14px">Se apunta como una tarea más: se tacha al hacerla, o se pasa a otro día si no da tiempo.</p></div>`;
}

async function anadirArreglo(){
  const txt = (textoArreglo || "").trim();
  if(!txt) return;
  textoArreglo = "";
  /* la clave evita que se apunte dos veces lo mismo mientras no se arregle */
  const clave = "arreglar:" + txt.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 40);
  await mandarEncargo({ t: txt, p: "coordinacion", f: fechaSel, diario: true,
                        tipo: "arreglar", clave: clave });
  ponerSync("ok", "Apuntado para arreglar");
  pinta();
}

/* ---------------------------------------------------------- ENCARGOS
   Algo que hay que TENER un día. Si hay que pedirlo antes, aparece un aviso
   el día que toca pedirlo. Se guarda la serie; las fechas se deducen. */
function esDiaDeEntrega(e, f){
  f = fechaBuena(f);
  if(f < e.desde || f > (e.hasta || e.desde)) return false;
  if(e.tipo === "dia") return f === e.desde;
  if(e.tipo === "semana"){
    const p = f.split("-").map(Number);
    const w = (new Date(p[0], p[1] - 1, p[2]).getDay() + 6) % 7;
    return (e.dias || []).map(Number).includes(w);
  }
  return true;                      // rango: todos los días
}

/* ¿hoy toca pedir algo para una entrega futura? */
function encargosParaPedir(f){
  const salida = [];
  (encargosFecha || []).forEach(e=>{
    if(!e.antelacion) return;                  // no hay que pedirlo
    const para = sumarDias(f, e.antelacion);
    if(!esDiaDeEntrega(e, para)) return;
    if(e.pedidos && e.pedidos[para]) return;   // ya se pidió
    salida.push({ e: e, para: para });
  });
  return salida;
}

/* ¿hoy hay que recibir algo? */
function encargosParaRecibir(f){
  return (encargosFecha || []).filter(e => esDiaDeEntrega(e, f));
}

const DIAS_CORTOS = ["L","M","X","J","V","S","D"];

function textoEncargo(e){
  const quien = e.cliente ? `<b>${e.cliente}</b> · ` : "";
  return `${quien}${e.que}`;
}

function cuandoEncargo(e, f){
  if(e.tipo === "dia") return "para hoy";
  const p = e.desde.split("-").map(Number), q = (e.hasta || e.desde).split("-").map(Number);
  const dd = (x) => x[2] + "/" + String(x[1]).padStart(2, "0");
  const dias = (e.dias || []).map(d => DIAS_CORTOS[d]).join("");
  return `${e.tipo === "semana" ? "los " + dias + " " : "todos los días "}` +
         `del ${dd(p)} al ${dd(q)}`;
}

/* EL AVISO GORDO: lo primero de la pantalla */
function bloqueEncargosAviso(){
  const pedir = encargosParaPedir(fechaSel);
  const recibir = encargosParaRecibir(fechaSel);
  if(!pedir.length && !recibir.length) return "";
  let html = "";
  pedir.forEach(({e, para})=>{
    html += `<div class="encargo-gordo">
        <div class="enc-cab">⚠ PEDIR HOY · PARA EL ${para.slice(8)}/${para.slice(5,7)}</div>
        <div class="enc-que">${textoEncargo(e)}</div>
        <div class="enc-cuando">${cuandoEncargo(e, fechaSel)} · lo pide ${nombreDe(e.quienPide)}</div>
        <button class="btn-add enc-btn" type="button"
                onclick="marcarEncargo('${e.id}','pedido','${para}')">Pedido hecho</button>
      </div>`;
  });
  recibir.forEach(e=>{
    const ya = (e.pedidos || {})[fechaSel];
    if(e.antelacion && !ya){
      html += `<div class="encargo-gordo enc-rojo">
          <div class="enc-cab">✕ PARA HOY · NO SE PIDIÓ</div>
          <div class="enc-que">${textoEncargo(e)}</div>
          <div class="enc-cuando">${cuandoEncargo(e, fechaSel)} · tenía que pedirlo ${nombreDe(e.quienPide)}</div>
        </div>`;
      return;
    }
    const hecho = (e.recibidos || {})[fechaSel];
    html += `<div class="encargo-gordo enc-verde">
        <div class="enc-cab">✓ PARA HOY · ${hecho ? "RECIBIDO" : "HA LLEGADO"}</div>
        <div class="enc-que">${textoEncargo(e)}</div>
        <div class="enc-cuando">${cuandoEncargo(e, fechaSel)}</div>
        ${hecho ? "" : `<button class="btn-add enc-btn" type="button"
            onclick="marcarEncargo('${e.id}','recibido','${fechaSel}')">Recibido</button>`}
      </div>`;
  });
  return html;
}

async function marcarEncargo(id, cual, fecha){
  ponerSync("trabajando", "Apuntando…");
  try{
    const r = await fetch("/api/encargo-fecha-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, cual: cual, fecha: fecha, quien: quien.id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    encargosFecha = d.encargosFecha || [];
    ponerSync("ok", cual === "pedido" ? "Pedido apuntado" : "Recibido");
  }catch(e){
    ponerSync("error", "No se pudo apuntar");
  }
  pinta();
}

/* ---------------------------------------------------- el alta de un encargo */
let formEncargo = false, encQue = "", encCliente = "", encTipo = "dia",
    encDesde = "", encHasta = "", encDias = [], encAntes = "1", encPide = "coordinacion";

function bloqueFormEncargo(){
  const lunes = proximoLunes();
  const d = encDesde || fechaSel || lunes;
  let html = `<h2 class="bloque">Encargos<small>lo que hay que tener un día</small></h2>`;
  if(!formEncargo){
    return html + `<div class="lista"><div class="nueva-nota fila-tarea">
        <button id="enc-nueva" class="btn-add-2" type="button"
                onclick="formEncargo=true; pinta();">+ Añadir un encargo</button>
        <span class="pista">Si hay que pedirlo antes, saldrá un aviso el día de pedirlo</span>
      </div></div>`;
  }
  html += `<div class="lista"><div class="nueva-nota">
      <input type="text" id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"
             oninput="encQue=this.value" value="${encQue}">
      <input type="text" id="enc-cli" maxlength="60" placeholder="Para quién"
             oninput="encCliente=this.value" value="${encCliente}" style="flex:0 1 130px">
    </div>
    <div class="nueva-nota">
      <select id="enc-tipo" onchange="encTipo=this.value; pinta();">
        <option value="dia"${encTipo==="dia"?" selected":""}>Un día</option>
        <option value="rango"${encTipo==="rango"?" selected":""}>Todos los días</option>
        <option value="semana"${encTipo==="semana"?" selected":""}>Varios días de la semana</option>
      </select>
      <input type="date" id="enc-desde" onchange="encDesde=this.value" value="${d}">
      ${encTipo === "dia" ? "" : `<span class="pista">hasta</span>
        <input type="date" id="enc-hasta" onchange="encHasta=this.value" value="${encHasta || d}">`}
    </div>`;
  if(encTipo === "semana"){
    html += `<div class="nueva-nota"><span class="pista">Los días:</span>` +
      DIAS_CORTOS.map((n, i) =>
        `<button class="dia-btn enc-dia${encDias.includes(i) ? " hoy" : ""}" type="button"
                 onclick="alternarDiaEnc(${i})">${n}</button>`).join("") + `</div>`;
  }
  html += `<div class="nueva-nota">
      <span class="pista">¿Hay que pedirlo?</span>
      <select id="enc-antes" onchange="encAntes=this.value">
        <option value="0"${encAntes==="0"?" selected":""}>No, ya está en la tienda</option>
        <option value="1"${encAntes==="1"?" selected":""}>Sí, 1 día antes</option>
        <option value="2"${encAntes==="2"?" selected":""}>Sí, 2 días antes</option>
        <option value="3"${encAntes==="3"?" selected":""}>Sí, 3 días antes</option>
        <option value="7"${encAntes==="7"?" selected":""}>Sí, 1 semana antes</option>
      </select>
      <span class="pista">lo pide</span>
      <select id="enc-pide" onchange="encPide=this.value">
        <option value="coordinacion"${encPide==="coordinacion"?" selected":""}>Coordinación</option>
        <option value="gerencia"${encPide==="gerencia"?" selected":""}>Jefa</option>
        <option value="tienda"${encPide==="tienda"?" selected":""}>Tienda</option>
      </select>
    </div>
    <div class="nueva-nota" style="border:none">
      <button id="enc-add" class="btn-add" type="button"
              onclick="guardarEncargo()">Añadir el encargo</button>
    </div></div>`;
  return html;
}

function alternarDiaEnc(i){
  encDias = encDias.includes(i) ? encDias.filter(x => x !== i) : encDias.concat([i]);
  pinta();
}

async function guardarEncargo(){
  const que = String(valorDe("enc-que", encQue) || "").trim();
  if(!que){ ponerSync("error", "Escribe qué es"); return; }
  const tipo = valorDe("enc-tipo", encTipo) || "dia";
  const d = valorDe("enc-desde", encDesde) || fechaSel;
  const hasta = valorDe("enc-hasta", encHasta) || d;
  const cuerpo = {
    quien: quien.id, que: que,
    cliente: String(valorDe("enc-cli", encCliente) || "").trim(),
    tipo: tipo,
    desde: d, hasta: tipo === "dia" ? d : hasta,
    dias: tipo === "semana" ? encDias : [],
    antelacion: Number(valorDe("enc-antes", encAntes)) || 0,
    quienPide: valorDe("enc-pide", encPide) || "coordinacion"
  };
  ponerSync("trabajando", "Guardando el encargo…");
  try{
    const r = await fetch("/api/encargo-fecha", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo)
    });
    const res = await r.json();
    if(!r.ok) throw new Error(res.error || ("HTTP " + r.status));
    encargosFecha = res.encargosFecha || [];
    formEncargo = false; encQue = ""; encCliente = "";
    ponerSync("ok", "Encargo añadido");
  }catch(e){
    ponerSync("error", "No se pudo: " + e.message);
  }
  pinta();
}

function bloqueSinDia(pre){
  const arr = sinDia(pre);
  if(!arr.length) return "";
  let html = `<h2 class="bloque bloque-arrastre">SIN HACER<small>${
    arr.length} ${arr.length===1?"tarea":"tareas"} · sin día</small></h2><div class="lista">`;
  arr.forEach((a, i)=>{
    const k = "arr" + i;
    ARR[k] = a;
    const partes = a.partes || [];
    const hp = a.hechasN;
    const completa = partes.length ? hp === partes.length : hechaEn(a.f, a.k);
    const parcial = partes.length && hp > 0 && hp < partes.length;
    let sub = "";
    if(partes.length){
      sub = `<div class="partes">` + partes.map((p, j)=>
        `<div class="parte ${hechaEn(a.f, a.k+"."+j)?"hecha":""}" data-parte="${k+"."+j}">
           <span class="pc"></span><span>${p}</span></div>`).join("") + `</div>`;
    }
    const dias = Math.round((new Date(fechaSel) - new Date(a.f)) / 86400000);
    const etiqueta = DIAS.find(x=>x[0]===semanaDe(a.f))[1] + " " + bonito(a.f) +
      (dias === 1 ? " · de ayer" : " · hace " + dias + " días");
    const tag = partes.length ? `<span class="tag">${hp} / ${partes.length} partes</span>` : "";
    const n = a.t.n ? `<span class="n">${a.t.n}</span>` : "";
    const abierto = PICK[k];
    const menu = abierto ? menuPasar(a, k) : "";
    html += `<div class="item ${completa?"hecha":""} ${hechaEn(a.f,"ab:"+a.k)?"abierta":""}"
        data-k="${k}">
        <div class="cab-item"><span class="caja ${parcial?"parcial":""}"></span>
        <span class="txt"><b>${a.t.t}</b>${tag}${n}
        <span class="arrastre-de">${etiqueta}</span></span></div>
        <div class="pasarlo"><button class="btn-pasar" data-pasar="${k}">
          ¿Para cuándo lo pasas?</button></div>${menu}${sub}</div>`;
  });
  return html + "</div>";
}

/* Las que ya tienen día: salen en su día, con la marca de donde vienen. */
function bloquePasadas(){
  const arr = pasadasA();
  if(!arr.length) return "";
  let html = `<h2 class="bloque bloque-pasadas">Pasadas a este día<small>${
    arr.length} ${arr.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;
  arr.forEach((a, i)=>{
    const k = "pas" + i;
    PAS[k] = a;
    const partes = a.partes || [];
    const hp = a.hechasN;
    const completa = partes.length ? hp === partes.length : hechaEn(a.f, a.k);
    const parcial = partes.length && hp > 0 && hp < partes.length;
    let sub = "";
    if(partes.length){
      sub = `<div class="partes">` + partes.map((p, j)=>
        `<div class="parte ${hechaEn(a.f, a.k+"."+j)?"hecha":""}" data-parte="${k+"."+j}">
           <span class="pc"></span><span>${p}</span></div>`).join("") + `</div>`;
    }
    const etiqueta = "venía del " + DIAS.find(x=>x[0]===semanaDe(a.f))[1] + " " + bonito(a.f);
    const tag = partes.length ? `<span class="tag">${hp} / ${partes.length} partes</span>` : "";
    const n = a.t.n ? `<span class="n">${a.t.n}</span>` : "";
    html += `<div class="item ${completa?"hecha":""} ${hechaEn(a.f,"ab:"+a.k)?"abierta":""}"
        data-k="${k}">
        <div class="cab-item"><span class="caja ${parcial?"parcial":""}"></span>
        <span class="txt"><b>${a.t.t}</b>${tag}${n}
        <span class="venia">${etiqueta}</span></span></div>${sub}</div>`;
  });
  return html + "</div>";
}

/* El menú de «¿para cuándo?» */
function menuPasar(a, k){
  const man = sumarDias(DIA, 1);
  const dos = sumarDias(DIA, 2);
  const opciones = [];
  if(quien.puesto === "tienda"){
    opciones.push([`Mañana por la mañana · ${bonito(man)}`, { f: man, t: "manana" }]);
    opciones.push([`Mañana por la tarde · ${bonito(man)}`, { f: man, t: "tarde" }]);
  } else {
    opciones.push([`Mañana · ${bonito(man)}`, { f: man }]);
  }
  opciones.push([`Dentro de dos días · ${bonito(dos)}`, { f: dos, t: tab }]);
  opciones.push(["La próxima vez que yo vuelva", { proxima: true, q: quien.id }]);

  let html = `<div class="menu-pasar">`;
  /* Cada opción lleva SU clave y SU destino escritos en el propio botón.
     Antes se buscaban en ARR[] y OPC[k] al pulsar; si esa búsqueda fallaba,
     el manejador hacía `return` y no pasaba NADA, sin ningún aviso. */
  const claveDeEsta = claveEn(a.f, a.k);
  opciones.forEach(([texto, destino], j)=>{
    html += `<button class="op-pasar" data-clave="${claveDeEsta}"` +
      ` data-destino='${JSON.stringify(destino)}'>${texto}</button>`;
  });
  html += `<div class="otro-dia"><span>Otro día:</span>
    <input type="date" class="inp-pasar" data-clave="${claveDeEsta}" min="${DIA}"></div>`;
  html += `</div>`;
  OPC[k] = opciones;
  return html;
}

/* La gerencia no tiene pestañas: tiene una bandeja. */
function pintaTabs(){
  const c = document.getElementById("tabs"); c.innerHTML = "";
  const s = document.getElementById("subopciones"); s.innerHTML = "";
  /* sin barra de pestañas: un solo botón para volver al menú, para todos */
  tab = tab || "menu";
  if(tab === "menu") return;
  const b = document.createElement("button");
  b.className = "tab";
  b.type = "button";
  b.textContent = "◀ Menú";
  b.addEventListener("click", ()=>{ tab = "menu"; pintaTabs(); pinta(); });
  c.appendChild(b);
  return;
  const lista = [];
  lista.forEach(([k,n])=>{
    const b = document.createElement("button");
    b.className = "tab"; b.type = "button"; b.textContent = n;
    b.setAttribute("aria-pressed", k === tab);
    b.addEventListener("click", ()=>{ tab = k; pintaTabs(); pinta(); });
    c.appendChild(b);
  });
  if(tab === "apertura"){
    const d = document.createElement("div"); d.className = "subtabs";
    Object.entries(DATOS.coordinacion.apertura).forEach(([k, v])=>{
      const b = document.createElement("button");
      b.className = "st"; b.type = "button";
      b.textContent = v.nombre + " · abre " + v.abre;
      b.setAttribute("aria-pressed", k === patron);
      b.addEventListener("click", ()=>{ patron = k; pintaTabs(); pinta(); });
      d.appendChild(b);
    });
    s.appendChild(d);
  }
  if(tab === "dia" ||
     (quien.puesto === "gerencia" && tab === "general") ||
     (quien.puesto === "tienda" && tab !== "cierre")){
    const d = document.createElement("div"); d.className = "fechas";

    const ant = document.createElement("button");
    ant.className = "dia-btn"; ant.type = "button"; ant.textContent = "◀";
    ant.title = "Día anterior";
    ant.addEventListener("click", ()=>{ fechaSel = sumarDias(fechaSel, -1); pintaTabs(); pinta(); });
    d.appendChild(ant);

    const inp = document.createElement("input");
    inp.type = "date"; inp.className = "fecha-inp"; inp.value = fechaSel;
    inp.addEventListener("change", ()=>{ if(inp.value){ fechaSel = inp.value; pintaTabs(); pinta(); } });
    d.appendChild(inp);

    const sig = document.createElement("button");
    sig.className = "dia-btn"; sig.type = "button"; sig.textContent = "▶";
    sig.title = "Día siguiente";
    sig.addEventListener("click", ()=>{ fechaSel = sumarDias(fechaSel, 1); pintaTabs(); pinta(); });
    d.appendChild(sig);

    const hoy = document.createElement("button");
    hoy.className = "dia-btn" + (fechaSel === DIA ? " hoy" : "");
    hoy.type = "button"; hoy.textContent = "Hoy";
    hoy.addEventListener("click", ()=>{ fechaSel = DIA; pintaTabs(); pinta(); });
    d.appendChild(hoy);

    const mes = document.createElement("button");
    mes.className = "dia-btn"; mes.type = "button"; mes.textContent = "Mes";
    mes.title = "Ver el mes entero";
    mes.addEventListener("click", ()=>{ verMes(); });
    d.appendChild(mes);

    s.appendChild(d);
  }
}

/* Una rejilla del mes: se pincha un día y se va a él. */
function verMes(){
  const c = document.getElementById("cuerpo");
  const [a, m] = fechaSel.split("-").map(Number);
  const primero = new Date(a, m - 1, 1);
  const dias = new Date(a, m, 0).getDate();
  const hueco = (primero.getDay() + 6) % 7;   // lunes = 0
  let h = `<h2 class="bloque">${["enero","febrero","marzo","abril","mayo","junio","julio",
    "agosto","septiembre","octubre","noviembre","diciembre"][m-1]} de ${a}` +
    `<small>pincha un día</small></h2><div class="mes">`;
  ["L","M","X","J","V","S","D"].forEach(x => h += `<div class="mes-cab">${x}</div>`);
  for(let i = 0; i < hueco; i++) h += `<div></div>`;
  for(let d = 1; d <= dias; d++){
    const f = `${a}-${String(m).padStart(2,"0")}-${String(d).padStart(2,"0")}`;
    const clases = "mes-dia" + (f === DIA ? " hoy" : "") + (f === fechaSel ? " sel" : "");
    h += `<div class="${clases}" data-f="${f}">${d}</div>`;
  }
  h += `</div>`;
  c.innerHTML = h;
  c.querySelectorAll(".mes-dia").forEach(el=>{
    el.addEventListener("click", ()=>{ fechaSel = el.dataset.f; pintaTabs(); pinta(); });
  });
}

/* Cómo se llama cada uno en pantalla. La oficina no dice «gerencia»:
   dice dónde está, que es la entreplanta. */
function nombreDe(id){
  const s = String(id || "");
  if(!s) return "";
  if(s.startsWith("ge")) return "Jefa";
  const m = s.match(/^([a-z]+)([0-9]+)$/);
  if(!m) return s;
  if(m[1] === "op") return "Tienda " + m[2];
  if(m[1] === "co") return "Coordinadora " + m[2];
  return s;
}
const MESES = ["enero","febrero","marzo","abril","mayo","junio","julio",
               "agosto","septiembre","octubre","noviembre","diciembre"];

/* Lo que puede ver cada uno: lo general lo ve todo el mundo,
   lo personal solo su dueña (y gerencia, cuando exista). */
function notasDe(f){
  return (notas[f] || []).filter(n => n.a === "general" || n.q === quien.id);
}

function abrirCal(k){
  calBloque = (calBloque === k) ? "" : k;
  /* al abrir «Tareas» se abre el formulario entero, no un botón que hay que pulsar */
  if(calBloque === "tareas") formTarea = true;
  pinta();
}

/* ------------------------------------------- cascada de CUALQUIER tarea
   Vale para las del día y para las extra. Se monta y se quita desde aquí. */
let cascPara = "";          /* la tarea cuya cascada se está montando */

function normNombre(x){
  return String(x || "").toLowerCase().normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim();
}

function cascadaDe(tarea){
  return (cascadas || {})[normNombre(tarea)] || [];
}

function abrirCascadaDe(k){
  const t = REG[k];
  if(!t) return;
  cascPara = t.t;
  cascHijos = cascadaDe(t.t).map(h => ({
    que: h.que, p: h.p || "tienda", turno: h.turno || "",
    cuando: String(h.cuando || 0)
  }));
  if(!cascHijos.length) cascHijos = [hijoNuevo()];
  pinta();
  window.scrollTo(0, 0);
}

function cerrarCascada(){
  cascPara = "";
  cascHijos = [];
  pinta();
}

async function guardarCascadaTarea(){
  if(!cascPara) return;
  const hijos = (cascHijos || []).filter(h => (h.que || "").trim());
  ponerSync("trabajando", "Guardando la cascada…");
  try{
    const r = await fetch("/api/cascada", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, tarea: cascPara,
        hijos: hijos.map(h => ({ que: h.que, p: h.p, turno: h.turno || null,
                                 cuando: Number(h.cuando) || 0 })) })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    cascadas = d.cascadas || {};
    ponerSync("ok", hijos.length ? "Cascada guardada" : "Cascada quitada");
    cascPara = ""; cascHijos = [];
  }catch(e){
    ponerSync("error", "No se pudo guardar la cascada");
  }
  pinta();
}

async function quitarCascada(tarea){
  ponerSync("trabajando", "Quitando la cascada…");
  try{
    const r = await fetch("/api/cascada", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, tarea: tarea, hijos: [] })
    });
    const d = await r.json();
    cascadas = d.cascadas || {};
    ponerSync("ok", "Cascada quitada · las tareas que ya nacieron se quedan");
  }catch(e){
    ponerSync("error", "No se pudo quitar");
  }
  pinta();
}

/* el panel para montarla, arriba de la pantalla */
function panelCascada(){
  if(!cascPara) return "";
  return `<div class="casc-panel">
      <b class="casc-tit">Cascada de «${cascPara}»</b>
      <span class="pista">Cuando se haga esta tarea, nacerán estas</span>` +
    cascHijos.map((h, i) => filaHijo(h, i)).join("") +
    `<div class="nueva-nota" style="border:none">
        <button class="btn-add-2" type="button" onclick="anadirHijo()">+ otra</button>
        <button class="btn-add" type="button" onclick="guardarCascadaTarea()">Guardar la cascada</button>
        <button class="btn-add-2" type="button" onclick="cerrarCascada()">Cancelar</button>
      </div></div>`;
}

/* el botoncito que va en cada tarea */
function lineaCascada(k, texto){
  const hijos = cascadaDe(texto);
  const puedeMontar = (quien.puesto === "coordinacion" || quien.puesto === "gerencia");
  if(!puedeMontar) return "";
  if(hijos.length){
    return `<div class="casc-linea"><span class="casc-icono">→</span>` +
      hijos.map(h => `cuando se haga: <b>${h.que}</b> (${NOMBRE_PUESTO[h.p] || h.p})`)
        .join(" · ") +
      ` <button class="btn-borrar" type="button" onclick="abrirCascadaDe('${k}')">cambiar</button></div>`;
  }
  return `<div class="casc-linea"><button class="btn-add-2" type="button" ` +
    `onclick="abrirCascadaDe('${k}')">＋ cuando se haga, crear…</button></div>`;
}

/* la lista de todas las cascadas */
function bloqueListaCascadas(){
  const claves = Object.keys(cascadas || {}).sort();
  if(!claves.length){
    return `<h2 class="bloque">Las cascadas que hay<small>ninguna</small></h2>` +
      `<div class="lista"><p class="pista" style="padding:14px">` +
      `Todavía no hay ninguna. Se montan desde una tarea, con «＋ cuando se haga, crear…».</p></div>`;
  }
  let html = `<h2 class="bloque">Las cascadas que hay` +
    `<small>${claves.length}</small></h2><div class="lista">`;
  claves.forEach(k=>{
    (cascadas[k] || []).forEach(h=>{
      html += `<div class="item"><div class="cab-item"><span class="txt">` +
        `<b>${k}</b><span class="extra-de">cuando se haga → ${h.que} · ` +
        `${NOMBRE_PUESTO[h.p] || h.p}` +
        `${h.turno ? " · " + (h.turno === "tarde" ? "tarde" : "mañana") : ""}` +
        `${Number(h.cuando) ? " · en " + h.cuando + " día(s)" : " · ese día"}</span></span>` +
        `</div><div class="pasarlo"><button class="btn-borrar" type="button" ` +
        `onclick="quitarCascada('${k.replace(/'/g, "")}')">quitar</button></div></div>`;
    });
  });
  return html + `</div>`;
}

function pintaListaCascadas(){
  const claves = Object.keys(cascadas || {}).sort();
  const c = document.getElementById("cuerpo");
  let html = `<h2 class="bloque">Las cascadas que hay` +
    `<small>${claves.length} ${claves.length === 1 ? "cascada" : "cascadas"}</small></h2>`;
  if(!claves.length){
    c.innerHTML = html + `<div class="lista"><p class="pista" style="padding:14px">` +
      `Todavía no hay ninguna. Se montan desde «Tareas» o desde una tarea del día.</p></div>`;
  } else {
    html += `<div class="lista">`;
    claves.forEach(k=>{
      (cascadas[k] || []).forEach(h=>{
        html += `<div class="item"><div class="cab-item">` +
          `<span class="txt"><b>${k}</b>` +
          `<span class="extra-de">cuando se haga → ${h.que} · ` +
          `${NOMBRE_PUESTO[h.p] || h.p}` +
          `${h.turno ? " · " + (h.turno === "tarde" ? "tarde" : "mañana") : ""}` +
          `${Number(h.cuando) ? " · en " + h.cuando + " día(s)" : " · ese día"}</span></span>` +
          `</div><div class="pasarlo">` +
          `<button class="btn-borrar" type="button" ` +
          `onclick="quitarCascada(${JSON.stringify(k).replace(/"/g, "&quot;")})">quitar</button>` +
          `</div></div>`;
      });
    });
    html += `</div>`;
    c.innerHTML = html;
  }
  const s = document.getElementById("sub");
  if(s) s.textContent = "Cascadas · " + bonito(fechaSel);
}

/* ------------------------------------------------ modificar una tarea extra */
let editando = "";      /* el id de la tarea que se está modificando */

function abrirEdicion(id){
  editando = (editando === id) ? "" : id;
  pinta();
  /* el panel sale arriba: si estabas abajo, no lo verias */
  if(editando) window.scrollTo(0, 0);
}

function panelEdicion(){
  if(!editando) return "";
  const e = (encargos || []).find(x => String(x.id) === String(editando));
  if(!e){ editando = ""; return ""; }
  const opc = (v, txt, act) => `<option value="${v}"${act === v ? " selected" : ""}>${txt}</option>`;
  return `<div class="casc-panel">
      <b class="casc-tit">Modificar la tarea</b>
      <div class="nueva-nota">
        <input type="text" id="ed-t" maxlength="300" value="${(e.t || "").replace(/"/g, "&quot;")}">
      </div>
      <div class="nueva-nota">
        <select id="ed-p">${opc("tienda", "Tienda", e.p)}${opc("coordinacion", "Coordinación", e.p)}${opc("gerencia", "Jefa", e.p)}</select>
        <select id="ed-turno">${opc("", "Sin turno", e.turno || "")}${opc("manana", "Mañana", e.turno)}${opc("tarde", "Tarde", e.turno)}</select>
        <select id="ed-tipo">${opc("extra", "Extra", e.tipo)}${opc("urgente", "Urgente", e.tipo)}${opc("arreglar", "Para arreglar", e.tipo)}</select>
        <input type="date" id="ed-f" value="${e.f || fechaSel}">
      </div>
      <div class="nueva-nota" style="border:none">
        <button class="btn-add" type="button" onclick="guardarEdicion('${e.id}')">Guardar los cambios</button>
        <button class="btn-add-2" type="button" onclick="abrirEdicion('${e.id}')">Cancelar</button>
      </div></div>`;
}

async function guardarEdicion(id){
  const c = {
    id: id, quien: quien.id,
    t: valorDe("ed-t", ""),
    p: valorDe("ed-p", ""),
    turno: valorDe("ed-turno", ""),
    tipo: valorDe("ed-tipo", ""),
    f: valorDe("ed-f", fechaSel)
  };
  ponerSync("trabajando", "Guardando los cambios…");
  try{
    const r = await fetch("/api/encargo-editar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(c)
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    encargos = d.encargos || encargos;
    editando = "";
    ponerSync("ok", "Tarea modificada");
  }catch(e){
    ponerSync("error", "No se pudo modificar");
  }
  pinta();
}

/* ---------------------------------------- cambiar una tarea del GUION
   Se cambia el texto y la nota. No se mueve de puesto ni de turno: eso toca
   el guion de verdad y se hace aparte, con su prueba. */
let plantilla = {};
let plantA = "";       /* el texto original de la tarea que se está cambiando */

function normTarea(x){
  return String(x || "").toLowerCase().normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim();
}

/* se aplican los cambios al guion, al arrancar */
function aplicarPlantilla(){
  const cambios = plantilla || {};
  if(!Object.keys(cambios).length) return;
  const visto = new Set();
  const andar = (x)=>{
    if(!x || typeof x !== "object") return;
    if(Array.isArray(x)){ x.forEach(andar); return; }
    if(typeof x.t === "string"){
      const k = normTarea(x.t);
      const c = cambios[k];
      if(c && !visto.has(x)){
        visto.add(x);
        x.t = c.t;
        if(c.n !== undefined && c.n !== null) x.n = c.n;
        else delete x.n;
        return;
      }
    }
    Object.keys(x).forEach(k => andar(x[k]));
  };
  andar(DATOS);
}

function abrirPlantilla(k){
  const t = REG[k];
  if(!t) return;
  plantA = (plantA && normTarea(plantA) === normTarea(t.t)) ? "" : t.t;
  pinta();
  if(plantA) window.scrollTo(0, 0);
}

function panelPlantilla(){
  if(!plantA) return "";
  const t = (function buscar(x){
    if(!x || typeof x !== "object") return null;
    if(Array.isArray(x)){
      for(const y of x){ const r = buscar(y); if(r) return r; }
      return null;
    }
    if(typeof x.t === "string" && normTarea(x.t) === normTarea(plantA)) return x;
    for(const k of Object.keys(x)){ const r = buscar(x[k]); if(r) return r; }
    return null;
  })(DATOS);
  if(!t){ plantA = ""; return ""; }
  return `<div class="casc-panel">
      <b class="casc-tit">Cambiar esta tarea del guion</b>
      <span class="pista">Cambia para todos los días. No la mueve de puesto.</span>
      <div class="nueva-nota">
        <input type="text" id="pl-t" maxlength="300" value="${(t.t || "").replace(/"/g, "&quot;")}">
      </div>
      <div class="nueva-nota">
        <input type="text" id="pl-n" maxlength="300" placeholder="Nota de debajo (si tiene)"
               value="${((t.n || "")).replace(/"/g, "&quot;")}">
      </div>
      <div class="nueva-nota" style="border:none">
        <button class="btn-add" type="button" onclick="guardarPlantilla()">Guardar el cambio</button>
        <button class="btn-add-2" type="button" onclick="plantA=''; pinta()">Cancelar</button>
      </div></div>`;
}

async function guardarPlantilla(){
  const clave = plantA;
  if(!clave) return;
  const nuevo = String(valorDe("pl-t", "") || "").trim();
  const nota = String(valorDe("pl-n", "") || "").trim();
  if(!nuevo){ ponerSync("error", "La tarea no puede quedar vacía"); return; }
  ponerSync("trabajando", "Guardando el cambio…");
  try{
    const r = await fetch("/api/plantilla", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, clave: normTarea(clave), t: nuevo, n: nota })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    plantilla = d.plantilla || {};
    aplicarPlantilla();
    plantA = "";
    ponerSync("ok", "Tarea cambiada para todos los días");
  }catch(e){
    ponerSync("error", "No se pudo guardar el cambio");
  }
  pinta();
}

function pintaCalendario(){
  const trozos = fechaSel.split("-").map(Number);
  const a = trozos[0], m = trozos[1];
  const cuantos = new Date(a, m, 0).getDate();
  const hueco = (new Date(a, m - 1, 1).getDay() + 6) % 7;

  /* el aviso de pedir, también aquí: es donde se mira el mes */
  let html = bloqueEncargosAviso();
  html += `<div class="cal-cab">
      <button class="dia-btn" id="cal-ant" type="button">◀</button>
      <span class="cal-mes">${MESES[m-1]} de ${a}</span>
      <button class="dia-btn" id="cal-sig" type="button">▶</button>
      <button class="dia-btn" id="cal-hoy" type="button">Hoy</button>
    </div><div class="mes">`;
  ["L","M","X","J","V","S","D"].forEach(x => { html += `<div class="mes-cab">${x}</div>`; });
  for(let i = 0; i < hueco; i++) html += `<div></div>`;
  for(let d = 1; d <= cuantos; d++){
    const f = a + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0");
    const hayNota = notasDe(f).length;
    const hayEnc = (encargos || []).some(e => !e.hecho && e.f === f);
    /* el día tiene encargo si ese día hay entrega, o si ese día toca pedirlo */
    const hayEncF = (encargosFecha || []).some(e =>
      esDiaDeEntrega(e, f) ||
      (e.antelacion && esDiaDeEntrega(e, sumarDias(f, e.antelacion))));
    const hay = hayNota || hayEnc || hayEncF;
    const cl = "mes-dia" + (f === DIA ? " hoy" : "") + (f === fechaSel ? " sel" : "") +
               (hay ? " con-nota" : "");
    const punto = hay
      ? `<span class="punto-nota${(hayEnc || hayEncF) ? " es-encargo" : ""}"></span>` : "";
    html += `<div class="${cl}" data-cf="${f}">${d}${punto}</div>`;
  }
  html += `</div>`;

  /* los encargos de este día: los que hay que pedir y los que llegan */
  const encPedir = encargosParaPedir(fechaSel);
  const encLlegan = encargosParaRecibir(fechaSel);
  if(encPedir.length || encLlegan.length){
    html += `<h2 class="bloque">Encargos de este día` +
      `<small>${encPedir.length ? encPedir.length + " que pedir" : ""}` +
      `${encPedir.length && encLlegan.length ? " · " : ""}` +
      `${encLlegan.length ? encLlegan.length + " que llegan" : ""}</small></h2>` +
      `<div class="lista">`;
    encPedir.forEach(({e, para})=>{
      html += `<div class="item es-urgente"><div class="cab-item">` +
        `<span class="caja"></span><span class="txt"><b>Pedir: ${e.que}</b>` +
        `<span class="extra-de">${e.cliente || ""} · para el ${para.slice(8)}/${
          para.slice(5,7)} · lo pide ${nombreDe(e.quienPide)}</span></span></div></div>`;
    });
    encLlegan.forEach(e=>{
      const hecho = (e.recibidos || {})[fechaSel];
      html += `<div class="item"><div class="cab-item">` +
        `<span class="caja${hecho ? " hecha" : ""}"></span><span class="txt">` +
        `<b>Llega: ${e.que}</b><span class="extra-de">${e.cliente || ""}` +
        `${hecho ? " · recibido" : ""}</span></span></div></div>`;
    });
    html += `</div>`;
  }

  const lista = notasDe(fechaSel);
  const gen = lista.filter(n => n.a === "general");
  const per = lista.filter(n => n.a === "personal");

  html += `<h2 class="bloque">${DIAS.find(x=>x[0]===semanaDe(fechaSel))[1]} ${bonito(fechaSel)}` +
          `<small>${lista.length} ${lista.length===1?"nota":"notas"}</small></h2>`;

  const pintaNotas = (titulo, arr, clase) => {
    if(!arr.length) return "";
    let s = `<div class="notas ${clase}"><div class="notas-cab">${titulo}</div>`;
    arr.forEach(n=>{
      s += `<div class="nota"><span class="nota-t">${n.t}</span>` +
           `<span class="nota-q">${nombreDe(n.q)}${n.h ? " · " + n.h : ""}</span>` +
           `<button class="nota-x" data-borrar="${n.id}" title="Borrar">✕</button></div>`;
    });
    return s + `</div>`;
  };
  html += pintaNotas("General · lo ve todo el mundo", gen, "general");
  html += pintaNotas("Personal · solo lo ves tú", per, "personal");

  if(!lista.length){
    html += `<div class="lista"><div class="aviso-item">Este día no tiene notas.</div></div>`;
  }

  /* Las tareas extra NO se listan aquí: van a las tareas del día de su
     puesto, que es donde se trabajan. En el calendario solo se AÑADEN.
     (Antes salían en los dos sitios y se trabajaban en ninguno.) */

  /* los tres botones: el calendario primero, y luego lo que se quiera hacer */
  html += `<div class="menu-grupo cal-menu">` +
    [["encargos", "Encargos", "📦"], ["llamadas", "Llamadas", "📞"],
     ["tareas", "Tareas", "✏️"], ["cascadas", "Cascadas", "🔗"]]
      .map(([k, n, d]) => `<button class="menu-btn${calBloque === k ? " activo" : ""}" ` +
        `type="button" onclick="abrirCal('${k}')">` +
        `<span class="menu-dibujo">${d}</span><b>${n}</b></button>`).join("") +
    `</div>`;

  if(calBloque === "llamadas") html += bloqueLlamada();
  if(calBloque === "encargos") html += bloqueFormEncargo();
  if(calBloque === "cascadas") html += bloqueListaCascadas();

  html += `<div class="nueva-nota">
      <input type="text" id="nota-txt" maxlength="500"
             placeholder="Añadir una nota para este día…" value="${textoNota}">
      <select id="nota-amb">
        <option value="general"${ambitoNota === "general" ? " selected" : ""}>General</option>
        <option value="personal"${ambitoNota === "personal" ? " selected" : ""}>Personal</option>
      </select>
      <button id="nota-add" class="btn-add" type="button">Añadir</button>
    </div>`;

  /* anadir una tarea extra a un puesto para este día */
  if(calBloque === "tareas") html += `<div class="nueva-nota fila-tarea">
      <button id="btn-nueva-tarea" class="btn-add-2" type="button" onclick="formTarea=!formTarea; pinta()">+ Añadir una tarea extra</button>
      <span class="pista">Se le añadirá a sus tareas de ese día y turno</span>
    </div>`;
  if(formTarea && calBloque === "tareas"){
    const ops = `<option value="tienda"${puestoTarea==="tienda"?" selected":""}>Tienda</option>` +
      `<option value="coordinacion"${puestoTarea==="coordinacion"?" selected":""}>Coordinación</option>` +
      `<option value="gerencia"${puestoTarea==="gerencia"?" selected":""}>Jefa</option>`;
    html += `<div class="nueva-nota">
        <input type="text" id="tarea-txt" oninput="alEscribirTarea(this.value)" maxlength="300"
               autocomplete="off" placeholder="Qué hay que hacer…" value="${textoTarea}">
        <div id="tarea-sug" class="sug-caja"></div>
        <select id="tarea-puesto" onchange="puestoTarea=this.value">${ops}</select>
        <select id="tarea-turno" onchange="turnoTarea=this.value">
          <option value=""${turnoTarea===""?" selected":""}>Sin turno</option>
          <option value="manana"${turnoTarea==="manana"?" selected":""}>Mañana</option>
          <option value="tarde"${turnoTarea==="tarde"?" selected":""}>Tarde</option>
        </select>
        <select id="tarea-tipo" onchange="tipoTarea=this.value" title="Extra: cuando se pueda · Urgente: hoy y ya">
          <option value="extra"${tipoTarea==="extra"?" selected":""}>Extra</option>
          <option value="urgente"${tipoTarea==="urgente"?" selected":""}>Urgente</option>
        </select>
        <button id="tarea-add" class="btn-add" type="button" onclick="anadirTareaExtra()">Añadir</button>
      </div>` +
      /* la cascada: solo coordinación y la Jefa (D-278) */
      ((quien.puesto === "coordinacion" || quien.puesto === "gerencia")
        ? `<div class="casc-caja">
             <b class="casc-tit">Cuando se haga, crear…</b>` +
           cascHijos.map((h, i) => filaHijo(h, i)).join("") +
           `<div class="nueva-nota" style="border:none">
              <button class="btn-add-2" type="button" onclick="anadirHijo()">+ otra</button>
              <span class="pista">Se creará sola al tachar esta tarea</span>
            </div></div>`
        : "");
  }

  document.getElementById("cuerpo").innerHTML = html;
  document.getElementById("sub").textContent = "Calendario · " + bonito(fechaSel);
  document.getElementById("ptxt").textContent = "—";
  document.getElementById("ppct").textContent = "";
  document.getElementById("pbar").style.width = "0%";

  document.getElementById("cal-ant").addEventListener("click", ()=>{
    let x = a, y = m - 1;
    if(y < 1){ y = 12; x--; }
    fechaSel = x + "-" + String(y).padStart(2, "0") + "-01";
    pinta();
  });
  document.getElementById("cal-sig").addEventListener("click", ()=>{
    let x = a, y = m + 1;
    if(y > 12){ y = 1; x++; }
    fechaSel = x + "-" + String(y).padStart(2, "0") + "-01";
    pinta();
  });
  document.getElementById("cal-hoy").addEventListener("click", ()=>{ fechaSel = DIA; pinta(); });
  document.querySelectorAll("[data-cf]").forEach(el=>{
    el.addEventListener("click", ()=>{ fechaSel = el.dataset.cf; textoNota = ""; pinta(); });
  });
  const inp = document.getElementById("nota-txt");
  inp.addEventListener("input", ()=>{ textoNota = inp.value; });
  inp.addEventListener("keydown", e=>{ if(e.key === "Enter"){ e.preventDefault(); anadirNota(); } });
  document.getElementById("nota-amb").addEventListener("change", e=>{ ambitoNota = e.target.value; });
  document.getElementById("nota-add").addEventListener("click", anadirNota);
  document.getElementById("tarea-txt") && (()=>{
    const t = document.getElementById("tarea-txt");
    t.addEventListener("input", ()=>{ textoTarea = t.value; });
    t.addEventListener("keydown", e=>{ if(e.key === "Enter"){ e.preventDefault(); anadirTareaExtra(); }});
  })();
  document.querySelectorAll("[data-borrar-enc]").forEach(b=>{
    b.addEventListener("click", async e=>{ e.stopPropagation(); await encargoBorrar(b.dataset.borrarEnc); });
  });
  document.querySelectorAll("[data-borrar]").forEach(b=>{
    b.addEventListener("click", async e=>{ e.stopPropagation(); await borrarNota(b.dataset.borrar); });
  });
}

async function anadirNota(){
  const t = (textoNota || "").trim();
  if(!t) return;
  ponerSync("trabajando", "Guardando la nota…");
  try{
    const r = await fetch("/api/nota", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: fechaSel, texto: t, ambito: ambitoNota })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    notas = d.notas || {};
    textoNota = "";
    ponerSync("ok", "Nota guardada");
    pinta();
  }catch(e){
    ponerSync("error", "No se pudo guardar la nota");
  }
}

/* se lee de la casilla en el momento del clic: asi no depende de que
   el enganche del campo haya funcionado */
function hijoNuevo(){
  return { que: "", p: "tienda", turno: "", cuando: "0" };
}

function ponerHijo(i, campo, valor){
  if(!cascHijos[i]) return;
  cascHijos[i][campo] = valor;
}

/* las mismas sugerencias que el campo de la tarea, pero para un hijo */
let SUGHIJO = {};

async function sugerirHijo(i, v){
  let lista = [];
  if(v && String(v).trim().length >= 2){
    try{
      const r = await fetch("/api/sugerencias", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: v })
      });
      const d = await r.json();
      lista = (d.sugerencias || []).slice(0, 8);
    }catch(e){ lista = []; }
  }
  SUGHIJO[i] = lista;
  const caja = document.getElementById("sugh" + i);
  if(!caja) return;
  caja.style.display = lista.length ? "block" : "none";
  caja.innerHTML = lista.map((_, k) =>
    `<div class="sug-linea" onmousedown="elegirHijo(${i},${k})">${lista[k]}</div>`).join("");
}

function elegirHijo(i, k){
  const txt = (SUGHIJO[i] || [])[k];
  if(!txt) return;
  ponerHijo(i, "que", txt);
  SUGHIJO[i] = [];
  const caja = document.getElementById("sugh" + i);
  if(caja){ caja.style.display = "none"; caja.innerHTML = ""; }
  const inp = document.getElementById("hijoq" + i);
  if(inp) inp.value = txt;
}

function quitarHijo(i){
  cascHijos = cascHijos.filter((_, j) => j !== i);
  pinta();
}

function anadirHijo(){
  cascHijos = cascHijos.concat([hijoNuevo()]);
  pinta();
}

/* un trozo del formulario de la cascada, para cada hijo */
function filaHijo(h, i){
  const opc = (v, txt, actual) =>
    `<option value="${v}"${actual === v ? " selected" : ""}>${txt}</option>`;
  return `<div class="nueva-nota casc-fila">
      <div style="flex:1 1 190px; position:relative">
        <input type="text" id="hijoq${i}" maxlength="200" autocomplete="off"
               placeholder="Qué hay que hacer después"
               oninput="ponerHijo(${i},'que',this.value); sugerirHijo(${i}, this.value)"
               value="${h.que}" style="width:100%">
        <div id="sugh${i}" class="sug-caja" style="position:absolute; left:0; right:0"></div>
      </div>
      <select onchange="ponerHijo(${i},'p',this.value)">
        ${opc("tienda","Tienda",h.p)}${opc("coordinacion","Coordinación",h.p)}${opc("gerencia","Jefa",h.p)}
      </select>
      <select onchange="ponerHijo(${i},'turno',this.value)">
        ${opc("","Sin turno",h.turno)}${opc("manana","Mañana",h.turno)}${opc("tarde","Tarde",h.turno)}
      </select>
      <select onchange="ponerHijo(${i},'cuando',this.value)">
        ${opc("0","Ese día",h.cuando)}${opc("1","Al día siguiente",h.cuando)}
        ${opc("2","En 2 días",h.cuando)}${opc("7","En una semana",h.cuando)}
      </select>
      <button class="btn-borrar" type="button" onclick="quitarHijo(${i})">✕</button>
    </div>`;
}

/* ------------------------------------------------ sugerencias al escribir
   Lo que ya se ha escrito alguna vez se ofrece mientras se escribe.
   Se cambia SOLO el desplegable: la pantalla no se repinta, para no perder el cursor. */
let sugerencias = [], sugTiempo = null;

function pintarSugerencias(){
  const caja = document.getElementById("tarea-sug");
  if(!caja) return;
  if(!sugerencias.length){ caja.innerHTML = ""; caja.style.display = "none"; return; }
  caja.style.display = "block";
  caja.innerHTML = sugerencias.map((s, i) =>
    `<div class="sug-linea" onmousedown="elegirSugerencia(${i})">${s}</div>`).join("");
}

async function buscarSugerencias(txt){
  try{
    const r = await fetch("/api/sugerencias", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q: txt })
    });
    const d = await r.json();
    sugerencias = d.sugerencias || [];
  }catch(e){ sugerencias = []; }
  pintarSugerencias();
}

function alEscribirTarea(v){
  textoTarea = v;
  clearTimeout(sugTiempo);
  if(!v || v.trim().length < 2){
    sugerencias = []; pintarSugerencias(); return;
  }
  sugTiempo = setTimeout(()=> buscarSugerencias(v), 220);
}

function elegirSugerencia(i){
  const txt = sugerencias[i];
  if(!txt) return;
  textoTarea = txt;
  sugerencias = [];
  const caja = document.getElementById("tarea-sug");
  if(caja){ caja.innerHTML = ""; caja.style.display = "none"; }
  const inp = document.getElementById("tarea-txt");
  if(inp){ inp.value = txt; inp.focus(); }
}

/* ---------------------------------------------------------- LLAMADAS
   Llamar a un proveedor es una tarea extra con más datos: a quién, a qué
   número y por qué. Y si tiene hora límite, se avisa. */
let proveedores = [];
let llamProv = "", llamCont = "", llamMotivo = "", llamTipo = "extra";
let llamLetra = "";   /* la letra elegida, para no ver los 31 de golpe */
let llamPara = "";    /* para qué puesto es la llamada */
let calBloque = "";   /* qué bloque del calendario está abierto */

function telBonito(x){
  const d = String(x || "").replace(/[^0-9]/g, "");
  if(d.length !== 9) return d;
  return d.slice(0, 3) + " " + d.slice(3, 5) + " " + d.slice(5, 7) + " " + d.slice(7);
}

/* la primera letra del nombre, sin tildes y en mayúscula */
function letraDe(nombre){
  const n = String(nombre || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  return (n.trim().charAt(0) || "#").toUpperCase();
}

/* las letras que de verdad tienen proveedores, en orden */
function letrasDisponibles(){
  const vistas = [];
  (proveedores || []).forEach(pv=>{
    const l = letraDe(pv.n);
    if(!vistas.includes(l)) vistas.push(l);
  });
  return vistas.sort();
}

/* todos los contactos (los de una letra, si se ha elegido letra) */
function contactosTodos(){
  const salida = [];
  if(!llamLetra) return salida;      /* primero la letra: sin ella, nada */
  (proveedores || []).forEach((pv, i)=>{
    if(letraDe(pv.n) !== llamLetra) return;
    (pv.cs || []).forEach((c, j)=>{
      salida.push({ i: i, j: j, prov: pv, c: c });
    });
  });
  return salida;
}

function elegirLetra(v){
  llamLetra = v;
  llamProv = ""; llamCont = "";
  pinta();
}

function quienSeLlama(){
  const pv = proveedores[llamProv];
  if(!pv) return null;
  const c = (pv.cs || [])[Number(llamCont) || 0];
  return c ? { prov: pv, c: c } : null;
}

function bloqueLlamada(){
  if(!(proveedores || []).length) return "";
  const letras = letrasDisponibles();
  const opcLetras = `<option value="">— elige la letra —</option>` +
    letras.map(l => `<option value="${l}"${l === llamLetra ? " selected" : ""}>${l}</option>`).join("");
  const lista = contactosTodos();
  const opciones = lista.map(x =>
    `<option value="${x.i}-${x.j}"${(String(x.i) === String(llamProv) && String(x.j) === String(llamCont)) ? " selected" : ""}>` +
    `${x.prov.n} · ${x.c.p} · ${telBonito(x.c.t)}</option>`).join("");
  return `<h2 class="bloque">Llamar a un proveedor` +
    `<small>una llamada es una tarea más</small></h2>` +
    `<div class="lista">` +
    `<div class="nueva-nota">` +
    `<select id="ll-letra" onchange="elegirLetra(this.value)">${opcLetras}</select>` +
    (llamLetra
      ? `<select id="ll-prov" onchange="elegirContacto(this.value)" style="flex:1 1 100%">` +
        `<option value="">— elige el contacto —</option>${opciones}</select>`
      : `<span class="pista">Elige la letra y saldrán sus contactos</span>`) +
    `</div>` +
    `<div class="nueva-nota">` +
    `<input type="text" id="ll-motivo" maxlength="200" placeholder="Para qué es la llamada…" ` +
    `oninput="llamMotivo=this.value" value="${llamMotivo}">` +
    `<select id="ll-tipo" onchange="llamTipo=this.value">` +
    `<option value="extra"${llamTipo === "extra" ? " selected" : ""}>Ordinaria</option>` +
    `<option value="urgente"${llamTipo === "urgente" ? " selected" : ""}>Urgente</option>` +
    `</select>` +
    `</div>` +
    `<div class="nueva-nota">` +
    `<span class="pista">la hace</span>` +
    `<select id="ll-para" onchange="llamPara=this.value">` +
    `<option value="tienda"${(llamPara || quien.puesto) === "tienda" ? " selected" : ""}>Tienda</option>` +
    `<option value="coordinacion"${(llamPara || quien.puesto) === "coordinacion" ? " selected" : ""}>Coordinación</option>` +
    `<option value="gerencia"${(llamPara || quien.puesto) === "gerencia" ? " selected" : ""}>Jefa</option>` +
    `</select>` +
    `<button class="btn-add" type="button" onclick="anadirLlamada()">Añadir la llamada</button>` +
    `</div></div>`;
}

function elegirContacto(v){
  const trozos = String(v).split("-");
  llamProv = trozos[0];
  llamCont = trozos[1];
}

async function anadirLlamada(){
  const q = quienSeLlama();
  if(!q){ ponerSync("error", "Elige a quién llamar"); return; }
  const motivo = String(valorDe("ll-motivo", llamMotivo) || "").trim();
  if(!motivo){ ponerSync("error", "Escribe para qué es la llamada"); return; }
  const urgente = (valorDe("ll-tipo", llamTipo) || "extra") === "urgente";
  await mandarEncargo({
    t: q.prov.n + " · " + q.c.p,
    p: valorDe("ll-para", llamPara) || quien.puesto,
    f: fechaSel,
    tipo: "llamada",          /* SIEMPRE llamada: antes se guardaba como extra */
    urgente: urgente,
    tel: q.c.t, motivo: motivo,
    antesDe: q.prov.antes || undefined,
    clave: "llamada:" + q.prov.n + ":" + q.c.p + ":" + fechaSel
  });
  llamMotivo = "";
  ponerSync("ok", "Llamada añadida para el " + bonito(fechaSel));
  pinta();
}

/* ¿ya se ha pasado la hora límite del proveedor? */
function pasadaLaHora(h){
  if(!h) return false;
  const ahora = horaAhora();
  return ahora > h;
}

/* la respuesta de la llamada: sale al llamar y se queda registrada */
function idDeEncargo(id){
  const caja = document.getElementById("resp-" + id);
  return caja ? caja.value : "";
}

async function marcarLlamada(id){
  try{
    await fetch("/api/encargo-respuesta", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, llamado: true, quien: quien.id })
    });
    const d = await fetch("/api/estado").then(x => x.json());
    encargos = d.encargos || encargos;
  }catch(e){ /* si falla, la llamada se hace igual */ }
  pinta();
}

async function guardarRespuesta(id){
  const txt = String(idDeEncargo(id) || "").trim();
  ponerSync("trabajando", "Guardando la respuesta…");
  try{
    const r = await fetch("/api/encargo-respuesta", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, respuesta: txt, quien: quien.id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    encargos = d.encargos || encargos;
    ponerSync("ok", txt ? "Respuesta guardada" : "Respuesta borrada");
  }catch(e){
    ponerSync("error", "No se pudo guardar la respuesta");
  }
  pinta();
}

function horaAhora(){
  const d = new Date();
  return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
}

function valorDe(id, porDefecto){
  const el = document.getElementById(id);
  return el && el.value !== undefined ? el.value : porDefecto;
}

async function anadirTareaExtra(){
  const t = String(valorDe("tarea-txt", textoTarea) || "").trim();
  if(!t){ ponerSync("error", "Escribe qué hay que hacer"); return; }
  const puesto = valorDe("tarea-puesto", puestoTarea) || "tienda";
  const turno = valorDe("tarea-turno", turnoTarea);
  const tipo = valorDe("tarea-tipo", tipoTarea) || "extra";
  const fecha = fechaSel;
  textoTarea = "";
  formTarea = false;
  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined,
                        tipo: tipo });
  /* la cascada, si se ha montado alguna */
  const hijos = (cascHijos || []).filter(h => (h.que || "").trim());
  if(hijos.length){
    try{
      await fetch("/api/cascada", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quien: quien.id, tarea: t,
          hijos: hijos.map(h => ({
            que: h.que, p: h.p, turno: h.turno || null, cuando: Number(h.cuando) || 0
          }))
        })
      });
      cascadas[t.toLowerCase().trim()] = hijos;
    }catch(e){ /* si la cascada falla, la tarea ya está puesta */ }
  }
  cascHijos = [];
  /* se dice A DÓNDE ha ido: cada tarea solo se ve en la pantalla de su puesto,
     así que sin esto no hay forma de comprobar que se ha metido bien. */
  tipoTarea = "extra";
  const dondePuesto = NOMBRE_PUESTO[puesto] || puesto;
  const dondeTurno = turno === "tarde" ? " · tarde"
                   : turno === "manana" ? " · mañana" : "";
  ponerSync("ok", "Añadida a " + dondePuesto + dondeTurno + " · " + bonito(fecha));
  pinta();
}

async function borrarNota(id){
  ponerSync("trabajando", "Borrando la nota…");
  try{
    const r = await fetch("/api/nota-borrar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    notas = d.notas || {};
    ponerSync("ok", "Nota borrada");
    pinta();
  }catch(e){
    ponerSync("error", "No se pudo borrar la nota");
  }
}

/* ---------------------------------------------------- gerencia */
function dosDig(n){ return String(n).padStart(2, "0"); }

function esHabil(f){
  const p = f.split("-").map(Number);
  const wd = new Date(p[0], p[1] - 1, p[2]).getDay();
  if(wd === 0 || wd === 6) return false;
  return !DATOS.gerencia.festivos.includes(f);
}

/* El último día hábil ANTES del día indicado. No vale restar uno:
   si el 16 cae en domingo, la transferencia es el viernes 14. */
function ultimoHabilAntesDe(dia, mes, anio){
  let f = anio + "-" + dosDig(mes) + "-" + dosDig(dia);
  f = sumarDias(f, -1);
  let vueltas = 0;
  while(!esHabil(f) && vueltas < 20){ f = sumarDias(f, -1); vueltas++; }
  return f;
}

function diasHasta(fecha){
  return Math.round((new Date(fecha) - new Date(DIA)) / 86400000);
}

/* Las cuatro ventanas del mes, y si están abiertas hoy. */
function ventanasMes(){
  const p = DIA.split("-").map(Number);
  const a = p[0], m = p[1], d = p[2];
  const ultimo = new Date(a, m, 0).getDate();
  const F = (x, y, z) => x + "-" + dosDig(y) + "-" + dosDig(z);
  const out = [];

  /* 1 · horas: 2 últimos días del mes y 3 primeros del siguiente */
  {
    let plazo, abierta;
    if(d <= 3){ plazo = F(a, m, 3); abierta = true; }
    else if(d >= ultimo - 1){
      const mm = (m === 12) ? 1 : m + 1, aa = (m === 12) ? a + 1 : a;
      plazo = F(aa, mm, 3); abierta = true;
    } else { plazo = F(a, m, 3); abierta = false; }
    out.push({ k: "horas", abierta: abierta, plazo: plazo, dias: diasHasta(plazo) });
  }
  /* 2 · asesoría fiscal: 10 primeros días */
  {
    const plazo = F(a, m, 10);
    out.push({ k: "asesoria", abierta: d <= 10, plazo: plazo, dias: diasHasta(plazo) });
  }
  /* 3 · hipoteca: último hábil antes del 17 */
  {
    const plazo = ultimoHabilAntesDe(17, m, a);
    out.push({ k: "hipoteca", abierta: DIA <= plazo, plazo: plazo, dias: diasHasta(plazo) });
  }
  /* 4 · extracto: del 20 al 30 */
  {
    const fin = (30 > ultimo) ? ultimo : 30;
    const plazo = F(a, m, fin);
    out.push({ k: "extracto", abierta: (d >= 20 && d <= fin), plazo: plazo,
               dias: diasHasta(plazo) });
  }
  return out;
}

const NOMBRE_VENTANA = {
  horas: "Relación de horas",
  asesoria: "Asesoría fiscal",
  hipoteca: "Hipoteca",
  extracto: "Extracto bancario",
};

/* El lunes siguiente a hoy (si hoy es lunes, el de la semana que viene). */
function proximoLunes(){
  const p = DIA.split("-").map(Number);
  const d = new Date(p[0], p[1] - 1, p[2]);
  const w = (d.getDay() + 6) % 7;          // lunes = 0
  d.setDate(d.getDate() + (7 - w));
  return d.toLocaleDateString("en-CA");
}

/* Da de alta las ofertas y lanza la cascada:
   hoy gerencia prepara -> el lunes coordinación cambia los lineales
   y la oficina pega la cartelería grande. */
async function darAltaOfertas(){
  const desde = ofertasDesde || proximoLunes();
  const hasta = ofertasHasta || "";
  const sufijo = "ofertas:" + desde;
  const d = (f) => f ? `${f.slice(8)}/${f.slice(5, 7)}` : "?";
  const fechas = (desde && hasta) ? `del ${d(desde)} al ${d(hasta)}`
                                  : (desde ? `desde el ${d(desde)}` : "");
  /* el título lo pone ella; si no pone nada, se usa el de siempre */
  const titulo = (ofertasTitulo || "").trim() || "Ofertas nuevas";
  const conFechas = (base) => fechas ? `${base} · ${fechas}` : base;

  await mandarEncargo({
    t: conFechas(titulo),
    p: "gerencia",
    f: DIA,
    que: fechas,
    clave: sufijo + ":prep",
    partes: [conFechas("Dar de alta las ofertas y poner el hasta"),
             "Sacar las etiquetas",
             "Organizar los stoppers",
             "Marcar que está preparado"],
    cascada: [
      { t: conFechas(titulo + " · cambiar los lineales"),
        p: "coordinacion", f: desde, clave: sufijo + ":lineales",
        partes: ["Primero: quitar todas las vencidas",
                 "Después: pegar las nuevas en los lineales"] },
      { t: conFechas(titulo + " · cartelería grande"),
        p: "gerencia", f: desde, clave: sufijo + ":cartel" }
    ]
  });
  formOfertas = false;
  ofertasTitulo = "";
  ofertasHasta = "";
  pinta();
}

/* ---------------------------------------------------- los turnos */
function turnoDe(puesto, numero, fecha){
  const T = DATOS.turnos;
  fecha = fechaBuena(fecha);
  const p = fecha.split("-").map(Number);
  const d = new Date(p[0], p[1] - 1, p[2]);
  const dia = (d.getDay() + 6) % 7;

  if(puesto === "tienda"){
    const semanas = Math.floor((new Date(fecha + "T12:00:00") -
                    new Date(T.tiendaAncla + "T12:00:00")) / (7 * 86400000));
    const semana = ((((semanas + (T.tiendaSemanaAncla - 1)) % 3) + 3) % 3) + 1;
    const t = (T.tiendaSemanas[semana] || {})[numero] || "A";
    const turno = T.tienda[t];
    const horas = turno.dias[dia] || 0;
    return { nombre: turno.nombre, clave: t, horas: horas, trabaja: horas > 0 };
  }

  const semanas = Math.floor((new Date(fecha + "T12:00:00") -
                  new Date(T.cicloAncla + "T12:00:00")) / (7 * 86400000));
  const semana = (((semanas % 4) + 4) % 4) + 1;

  if(puesto === "coordinacion"){
    const tabla = ((T.coord[semana] || {})[numero]) || {};
    const horas = tabla[dia] || 0;
    return { nombre: "Semana " + semana + " del ciclo", clave: "S" + semana,
             horas: horas, trabaja: horas > 0 };
  }
  const horas = (T.oficina[semana] || {})[dia] || 0;
  return { nombre: "Semana " + semana + " del ciclo", clave: "S" + semana,
           horas: horas, trabaja: horas > 0 };
}

const GENTE = [
  { puesto: "tienda", numero: 1, nombre: "Tienda 1" },
  { puesto: "tienda", numero: 2, nombre: "Tienda 2" },
  { puesto: "tienda", numero: 3, nombre: "Tienda 3" },
  { puesto: "coordinacion", numero: 1, nombre: "Coordinadora 1" },
  { puesto: "coordinacion", numero: 2, nombre: "Coordinadora 2" },
  { puesto: "gerencia", numero: 1, nombre: "Jefa" },
];

function ausenciaDe(puesto, numero, fecha){
  return (DATOS.turnos.ausencias || []).find(a =>
    a.puesto === puesto && a.numero === numero &&
    fecha >= a.desde && fecha <= a.hasta) || null;
}

/* engancha los clics de las tareas. Antes esto vivía solo dentro de
   pinta(), y la pantalla de la Jefa llamaba a un `enganchar()` que
   no existía: se cortaba y no se podía marcar nada. */
/* UN SOLO ESCUCHADOR, puesto una vez sobre el contenedor.
   Antes se enganchaba tarea por tarea y se perdía al repintar:
   la pantalla se quedaba muerta sin dar ningún error. */
/* De dónde viene una tarea de las de «pasadas a este día».
   Faltaba: el clic la llamaba y reventaba, así que NADA se marcaba. */
function origenDe(k){ return PAS[k] || null; }

function atenderClic(e){
  /* LOS SUB-PASOS, PRIMERO.
     Antes se enganchaban dentro de pinta(), y esa función sale antes de
     llegar ahí cuando entras como Jefa: sus sub-pasos eran botones muertos.
     Aquí valen para todos los perfiles. */
  const pa = e.target.closest(".parte");
  if(pa){
    e.stopPropagation();
    const pk = pa.dataset.parte;
    const duo = pk.startsWith("arr") ? ARR[pk.split(".")[0]]
               : pk.startsWith("pas") ? PAS[pk.split(".")[0]] : null;
    if(duo){
      const k2 = duo.k + "." + pk.split(".")[1];
      tocarEn(duo.f, k2, !hechaEn(duo.f, k2));
      return;
    }
    tocar(pk, !hecha(pk));
    return;
  }

  /* borrar: también para todos. Estos botones se enganchaban en pinta(),
     y la pantalla de la Jefa no pasa por ahí. */
  const bd = e.target.closest("[data-borrar-enc]");
  if(bd){ e.stopPropagation(); encargoBorrar(bd.dataset.borrarEnc); return; }
  const bn2 = e.target.closest("[data-borrar]");
  if(bn2){ e.stopPropagation(); borrarNota(bn2.dataset.borrar); return; }

  /* abrir el menú de «¿para cuándo?», también para todos */
  const bp = e.target.closest(".btn-pasar");
  if(bp){
    e.stopPropagation();
    const kk = bp.dataset.pasar;
    PICK[kk] = !PICK[kk];
    pinta();
    return;
  }

  /* los botones de guardar: van aquí para que valgan en TODOS los puestos.
     Antes vivían en la pantalla de la Jefa, así que en tienda no hacían nada. */
  if(e.target.closest("#rec-guardar")){
    e.stopPropagation(); guardarRecuento(); return;
  }
  if(e.target.closest("#tah-guardar")){
    e.stopPropagation();
    guardarTahona(e.target.closest("#tah-guardar").dataset.cual || "entrada");
    return;
  }
  if(e.target.closest("#arr-add")){
    e.stopPropagation(); anadirArreglo(); return;
  }
  if(e.target.closest("#rec-ok")){
    e.stopPropagation(); aprobarRecuento(); return;
  }

  /* lo que no es la tarea (menús, campos, botones) no se toca aquí */
  if(e.target.closest(".menu-pasar") || e.target.closest(".pasarlo") ||
     e.target.closest("select") || e.target.closest("input") ||
     e.target.closest("button")) return;

  const cab = e.target.closest(".cab-item");
  if(!cab) return;
  const it = cab.closest(".item");
  if(!it) return;
  if(e.target.closest(".partes")) return;
  const k = it.dataset.k;
    /* las de «SIN HACER» se tachan EN SU DÍA, no en el que se está mirando */
    if(String(k).indexOf("arr") === 0){
      const a = ARR[k];
      if(a) tocarEn(a.f, a.k, !hechaEn(a.f, a.k));
      return;
    }
  if(!k) return;
  if(k.startsWith("enc")){
    const enc = ENC[k];
    if(enc) encargoHecho(enc.id);
    return;
  }
  const a = origenDe(k);
  if(a){
    if(a.partes.length) tocarEn(a.f, "ab:" + a.k, !hechaEn(a.f, "ab:" + a.k));
    else tocarEn(a.f, a.k, !hechaEn(a.f, a.k));
    return;
  }
  const tg = REG[k];
  if(tg && tg.partes && tg.partes.length) tocar("ab:" + k, !hecha("ab:" + k));
  else tocar(k, !hecha(k));
}

function engancharItems(){
  const c = document.getElementById("cuerpo");
    c.querySelectorAll(".item").forEach(it=>{
      const k = it.dataset.k;
      it.querySelector(".cab-item").addEventListener("click", e=>{
        if(e.target.closest(".partes") || e.target.closest(".pasarlo")) return;
        if(k.startsWith("enc")){                        // un encargo: se marca y desaparece
          const enc = ENC[k];
          if(enc) encargoHecho(enc.id);
          return;
        }
        const a = origenDe(k);
        if(a){                                          // de otro día: se marca allí
          if(a.partes.length) tocarEn(a.f, "ab:" + a.k, !hechaEn(a.f, "ab:" + a.k));
          else tocarEn(a.f, a.k, !hechaEn(a.f, a.k));
          return;
        }
        const t = REG[k];
        if(t && t.partes && t.partes.length) tocar("ab:" + k, !hecha("ab:" + k));
        else tocar(k, !hecha(k));
      });
    });
}

function pintaTurnos(){
  const W = semanaDe(fechaSel);
  let html = `<div class="ger-cab"><b>${DIAS.find(x=>x[0]===W)[1]} ${bonito(fechaSel)}</b>` +
    `<span>quién trabaja y en qué turno</span></div><div class="lista">`;
  let cuantos = 0;
  GENTE.forEach(g=>{
    const t = turnoDe(g.puesto, g.numero, fechaSel);
    const aus = ausenciaDe(g.puesto, g.numero, fechaSel);
    const marca = aus ? `<span class="tag ausente">de vacaciones</span>`
      : (t.trabaja ? `<span class="tag">${t.horas} h</span>`
                   : `<span class="tag apagado">libre</span>`);
    const quien = aus ? `lo cubre la ${aus.cubre}`
      : (t.trabaja ? t.nombre : "no trabaja");
    if(t.trabaja && !aus) cuantos++;
    html += `<div class="turno-fila ${(!t.trabaja || aus) ? "libre" : ""}">
        <span class="t-nombre">${g.nombre}</span>
        <span class="t-turno">${quien}</span>${marca}</div>`;
  });
  html += `</div><p class="pista" style="margin-top:10px">
    ${cuantos} de ${GENTE.length} trabajan este día.</p>`;

  html += `<h2 class="bloque">Los siete días siguientes</h2><div class="lista">`;
  for(let i = 0; i < 7; i++){
    const f = sumarDias(fechaSel, i);
    const w = semanaDe(f);
    const quien = GENTE.filter(g => turnoDe(g.puesto, g.numero, f).trabaja &&
                                       !ausenciaDe(g.puesto, g.numero, f))
      .map(g => g.nombre.replace("Coordinadora ", "Coord. ").replace("Tienda ", "T."))
      .join(" · ");
    html += `<div class="turno-fila ${f === DIA ? "es-hoy" : ""}">
        <span class="t-nombre">${DIAS.find(x=>x[0]===w)[1].slice(0,3)} ${f.slice(8)}</span>
        <span class="t-turno">${quien || "—"}</span></div>`;
  }
  html += `</div>`;

  document.getElementById("cuerpo").innerHTML = html;
  document.getElementById("sub").textContent = "Turnos · " + bonito(fechaSel);
  document.getElementById("ptxt").textContent = "—";
  document.getElementById("ppct").textContent = "";
  document.getElementById("pbar").style.width = "0%";
}

/* El aviso: solo lo ve quien tiene tareas extra hoy. */
function avisoExtras(){
  /* las hechas NO se esconden: se quedan tachadas, para poder ver qué se hizo */
  const mias = (encargos || []).filter(e =>
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  const pendientesLista = mias.filter(e => !e.hecho);
  const hechasLista = mias.filter(e => e.hecho);
  let html = "";
  if(!pendientesLista.length && !hechasLista.length) return "";
  if(pendientesLista.length){
    html += `<div class="aviso-extra"><b>Tienes ${pendientesLista.length} ` +
      `${pendientesLista.length === 1 ? "tarea extra" : "tareas extra"} hoy</b>`;
  }
  /* cada una se marca tocandola, y se puede pasar a otro dia */
  pendientesLista.forEach(e=>{
    const urgente = e.tipo === "urgente";
    const arreglo = e.tipo === "arreglar";
    const etiqueta = urgente ? `<span class="tag urgente">URGENTE</span>`
                   : arreglo ? `<span class="tag arreglar">PARA ARREGLAR</span>` : "";
    const quienLaPuso = nombreDe(e.q);
    const hecho = e.hecho;
    TXTENC[e.id] = e.t;
    REG["e_" + e.id] = e;
    html += `<div class="extra-linea ${urgente?"es-urgente":""}${hecho?" hecha":""}" ` +
      `onclick="encargoHecho('${e.id}', ${hecho ? "true" : "false"})">` +
      `<span class="caja"></span><span class="extra-txt">` +
      (e.tipo === "llamada" ? "📞 " : "") + `${e.t}</span>${etiqueta}</div>` +
      `<div class="casc-linea"><button class="btn-add-2" type="button" ` +
      `onclick="abrirEdicion('${e.id}')">✎ modificar</button></div>` +
      lineaCascada("e_" + e.id, e.t) +
      (e.tipo === "llamada" && e.tel
        ? `<div class="extra-pasar"><a class="btn-llamar" href="tel:${e.tel}" ` +
          `onclick="marcarLlamada('${e.id}')">📞<small>Llamar</small></a>` +
          `<span class="pista">${telBonito(e.tel)}${e.motivo ? " · " + e.motivo : ""}</span>` +
          (e.antesDe ? `<span class="pista ${pasadaLaHora(e.antesDe) ? "tarde" : ""}">` +
            `${pasadaLaHora(e.antesDe) ? "⚠ se pasó la hora · " : "⏰ "}antes de las ` +
            `${e.antesDe}</span>` : "") + `</div>` +
          (true
            ? `<div class="extra-pasar"><span class="pista">Respuesta:</span>` +
              `<input type="text" maxlength="500" id="resp-${e.id}" ` +
              `placeholder="Lo que dijeron…" value="${(e.respuesta || "").replace(/"/g, "&quot;")}">` +
              `<button class="btn-add-2" type="button" ` +
              `onclick="guardarRespuesta('${e.id}')">Guardar</button></div>`
              + (e.llamadoEn ? `<span class="pista" style="margin-left:27px">llamada hecha${
                  e.hRespuesta ? " · " + e.hRespuesta : ""}</span>` : "")
            : "")
        : "") +
      `<div class="extra-pasar">` +
      `<span class="pista">para el ${bonito(e.f)} · la puso ${quienLaPuso}` +
      `${e.turno === "tarde" ? " · por la tarde" : e.turno === "manana" ? " · por la mañana" : ""}</span>` +
      (hecho ? `<span class="pista">toca para destacharla</span>` :
        `<span class="pista">si no da tiempo:</span>` +
        `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
        `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)">`) +
      `</div>`;
  });
  if(pendientesLista.length) html += `</div>`;

  /* las terminadas, en su propio bloque cerrado: la pantalla se va limpiando */
  if(hechasLista.length){
    const claveH = "extras-hechas";
    const abierto = PLEGADOS[claveH] === false;
    html += `<h2 class="bloque plega hecho" onclick="plegar('${claveH}')">` +
      `<span class="flecha">${abierto ? "▾" : "▸"}</span>` +
      `<span class="bloque-tit">Terminadas</span>` +
      `<small class="bloque-ok">${hechasLista.length} ✓</small></h2>`;
    if(abierto){
      html += `<div class="lista">`;
      hechasLista.forEach(e=>{
        html += `<div class="item"><div class="cab-item">` +
          `<span class="caja hecha"></span><span class="txt"><b>${e.t}</b>` +
          `<span class="extra-de">hecha${e.hHecho ? " · " + e.hHecho : ""}` +
          `${e.turno === "tarde" ? " · por la tarde" : e.turno === "manana" ? " · por la mañana" : ""}` +
          `</span></span></div>` +
          `<div class="casc-linea"><button class="btn-add-2" type="button" ` +
          `onclick="encargoHecho('${e.id}', true)">destachar</button></div></div>`;
      });
      html += `</div>`;
    }
  }
  return html;
}

function pintaGerencia(){
  /* sigue al día elegido en el calendario, igual que tienda y coordinación */
  const W = semanaDe(fechaSel);
  const ES_HOY_G = (fechaSel === DIA);
  const V = ventanasMes();
  const abiertas = V.filter(v => v.abierta);
  let total = 0, hechos = 0;
  const sumar2 = (tareas, pre) => (tareas||[]).forEach((t, i)=>{
    const k = pre + i, partes = t.partes || [];
    if(partes.length){ total += partes.length;
      partes.forEach((_, j)=>{ if(hecha(k + "." + j)) hechos++; });
    } else { total += 1; if(hecha(k)) hechos++; }
  });

  const laborable = (W !== "SAB" && W !== "DOM");
  let html = panelPlantilla() + panelCascada() + panelEdicion() + avisoExtras();   /* el panel de la cascada, y las extra */
  html += `<div class="ger-cab">
      <b>${DIAS.find(x=>x[0]===W)[1]} ${bonito(fechaSel)}</b>
      <span>${abiertas.length
        ? abiertas.length + (abiertas.length === 1 ? " ventana abierta" : " ventanas abiertas")
        : "ninguna ventana abierta"}</span>
    </div>`;

  if(!laborable){
    html += `<div class="lista"><div class="aviso-item">
      Es ${DIAS.find(x=>x[0]===W)[1].toLowerCase()}: la gerencia va de lunes a viernes.
      Abajo tienes todo lo que hay, por si quieres adelantar algo.</div></div>`;
  }

  if(laborable){
    html += bloque("Lo primero", DATOS.gerencia.entrada, "ge");
    sumar2(DATOS.gerencia.entrada, "ge");
    html += "";
    html += bloqueViene(fechaSel);
    html += bloque("Lo de cada día", DATOS.gerencia.hoy, "gh");
    sumar2(DATOS.gerencia.hoy, "gh");
  } else {
    /* las extra van en su bloque, arriba: aqui no se repiten */
    html += bloqueViene(fechaSel);
  }

  if(W === "LUN"){
    if(W === "LUN") html += bloque("Los lunes · los pedidos", DATOS.gerencia.lunes, "gl");
    sumar2(DATOS.gerencia.lunes, "gl");
  } else {
    html += `<h2 class="bloque bloque-apagado">Los lunes · los pedidos<small>hoy no toca</small></h2>
      <div class="lista"><div class="aviso-item">Se hace en lunes. Son los cuatro bloques de pedidos,
      uno con hora límite a las 11:00.</div></div>`;
  }

  if(W === "MAR"){
    if(W === "MAR") html += bloque("Los martes · cerrar lo del lunes",
                      DATOS.gerencia.martes, "gm");
    sumar2(DATOS.gerencia.martes, "gm");
  } else {
    html += `<h2 class="bloque bloque-apagado">Los martes · cerrar lo del lunes<small>hoy no toca</small></h2>`;
  }

  if(abiertas.length){
    const tareas = DATOS.gerencia.mes.filter(t => abiertas.some(v => v.k === t.cuando));
    if(W === "MIE") html += bloque("Los miércoles · adelantar los pedidos",
                      DATOS.gerencia.miercoles, "gmi");
  if(W === "LUN" || W === "VIE") html += bloque("Frutas Tito · precios y etiquetas",
                      DATOS.gerencia.frutas, "gf");
  html += bloque("Abierto este mes", tareas, "gv");
    sumar2(tareas, "gv");
  }

  /* en el mismo bloque de las ofertas van las ya dadas de alta, con su
     título y su fecha, en orden. Pueden convivir varias en las mismas fechas. */
  html += bloqueEncargosAviso();
  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */
  html += bloque("Las ofertas", DATOS.gerencia.ofertas, "go", listaOfertas());

  /* dar de alta las ofertas nuevas y lanzar la cascada */
  const lunes = proximoLunes();
  if(formOfertas){
    html += `<div class="nueva-nota">
        <input type="date" id="of-desde" value="${ofertasDesde || lunes}">
        <span class="pista">empiezan</span>
        <input type="date" id="of-hasta" value="${ofertasHasta || ""}">
        <span class="pista">terminan</span>
      </div>
      <div class="nueva-nota">
        <input type="text" id="of-titulo" maxlength="80"
               placeholder="Título de la oferta (ej.: Vuelta al cole)" value="${ofertasTitulo}">
        <button id="of-add" class="btn-add" type="button">Dar de alta</button>
      </div>`;
  } else {
    html += `<div class="nueva-nota fila-tarea">
        <button id="of-nueva" class="btn-add-2" type="button">
          + Dar de alta las ofertas nuevas</button>
        <span class="pista">Al terminar de prepararlas, la tarea salta a coordinación</span>
      </div>`;
  }
  sumar2(DATOS.gerencia.ofertas, "go");

  /* el informe del pan, junto a las ventanas */
  html += bloqueTahonaResumen();

  /* el estado de las cuatro ventanas */
  html += `<h2 class="bloque">Las cuatro ventanas del mes</h2><div class="lista">`;
  V.forEach(v=>{
    const d = v.dias;
    const cuando = v.abierta
      ? (d === 0 ? "hoy es el último día" : d === 1 ? "queda 1 día" : "quedan " + d + " días")
      : "cerrada";
    html += `<div class="ventana ${v.abierta ? "abierta" : ""}">
        <span class="v-nombre">${NOMBRE_VENTANA[v.k]}</span>
        <span class="v-plazo">hasta el ${bonito(v.plazo)}</span>
        <span class="v-estado">${cuando}</span></div>`;
  });
  if(V.some(v => v.k === "hipoteca" && v.abierta)){
    html += `<div class="aviso-item">La hipoteca va <b>el último día hábil</b> antes del 17:
      los sábados, domingos y festivos no cuentan.</div>`;
  }
  html += `</div>`;

  document.getElementById("cuerpo").innerHTML = html;
  document.getElementById("sub").textContent = "Bandeja · " + bonito(fechaSel) +
    (ES_HOY_G ? "" : "  (no es hoy)");
  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ptxt").textContent = hechos + " de " + total;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";
  /* los botones de las ofertas */
  const at = document.getElementById("arr-txt");
  if(at){
    at.addEventListener("input", ()=>{ textoArreglo = at.value; });
    at.addEventListener("keydown", e=>{ if(e.key === "Enter"){ e.preventDefault(); anadirArreglo(); } });
  }
  const bn = document.getElementById("of-nueva");
  if(bn) bn.addEventListener("click", ()=>{ formOfertas = true; pinta(); });
  const ba = document.getElementById("of-add");
  if(ba) ba.addEventListener("click", darAltaOfertas);
  const dd = document.getElementById("of-desde");
  const dt = document.getElementById("of-titulo");
  if(dt) dt.addEventListener("input", ()=>{ ofertasTitulo = dt.value; });
  if(dd) dd.addEventListener("change", ()=>{ ofertasDesde = dd.value; });
  const dh = document.getElementById("of-hasta");
  if(dh) dh.addEventListener("change", ()=>{ ofertasHasta = dh.value; });
}

/* ---------------------------------------------------------- EL MENÚ
   Al entrar en un grupo se ven botones, no la lista de tareas.
   De izquierda a derecha y de arriba abajo, como pidió la propiedad (D-284). */
const MENU_POR_PUESTO = {
  tienda: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"],
    ["manana", "Mañana", "☀️"],
    ["tarde", "Tarde", "🌤"],
    ["cierre", "Cierre", "🌙"]
  ],
  coordinacion: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"],
    ["apertura", "Apertura", "🔑"],
    ["dia", "El día", "📋"],
    ["cierre", "Cierre", "🌙"]
  ],
  gerencia: [
    ["general", "El día", "📋"],
    ["turno", "Turno", "📅"],
    ["calendario", "Calendario", "🗓"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"]
  ]
};

/* cuántas tareas extra quedan sin hacer para este puesto */
function extrasPendientes(){
  return (encargos || []).filter(e => !e.hecho && (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto)).length;
}

function abrirSeccion(k){
  tab = k;
  pintaTabs();      /* sin esto no aparece el boton de volver */
  pinta();
}

function pintaMenu(){
  const c = document.getElementById("cuerpo");
  /* los avisos, siempre arriba (D-284) */
  let html = panelPlantilla() + panelCascada() + panelEdicion() +
    bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();
  const lista = MENU_POR_PUESTO[quien.puesto] || [];
  html += `<div class="menu-grupo">`;
  lista.forEach(([k, n, dibujo])=>{
    const cuantas = k === "extra" ? extrasPendientes() : 0;
    html += `<button class="menu-btn${cuantas ? " con-pendientes" : ""}" ` +
      `type="button" onclick="abrirSeccion('${k}')">` +
      `<span class="menu-dibujo">${dibujo || ""}</span>` +
      `<b>${n}</b>` +
      (cuantas ? `<span class="menu-num">${cuantas}</span>` : "") +
      `</button>`;
  });
  html += `</div>`;
  c.innerHTML = html;
  const s = document.getElementById("sub");
  if(s) s.textContent = NOMBRE_PUESTO[quien.puesto] + " · " + bonito(fechaSel);
}

/* la sección «Registro de panes»: aquí vive el pan, no dentro de apertura ni cierre */
function pintaPanes(){
  const cual = quien.puesto === "tienda" ? "devolucion" : "entrada";
  const c = document.getElementById("cuerpo");
  c.innerHTML = bloqueTahona(cual);
  const s = document.getElementById("sub");
  if(s) s.textContent = "Registro de panes · " + bonito(fechaSel);
}

/* la sección «Tareas extra» */
function pintaExtra(){
  const c = document.getElementById("cuerpo");
  c.innerHTML = panelPlantilla() + panelCascada() + panelEdicion() + (avisoExtras() ||
    `<div class="lista"><p class="pista" style="padding:14px">` +
    `No hay tareas extra para hoy.</p></div>`);
  const s = document.getElementById("sub");
  if(s) s.textContent = "Tareas extra · " + bonito(fechaSel);
}

function pinta(){
  /* el menú de botones, para TODOS (D-284): la Jefa también */
  if(!tab || tab === "menu"){ pintaMenu(); return; }
  if(tab === "panes"){ pintaPanes(); return; }
  if(tab === "extra"){ pintaExtra(); return; }
  /* la pestaña «General» es de tienda y coordinación; la Jefa tiene la suya */
  if(tab === "general" && quien.puesto !== "gerencia"){ pintaTurnos(); return; }
  if(tab === "calendario"){ pintaCalendario(); return; }
  if(quien.puesto === "gerencia"){
    if(tab === "turno"){ pintaTurnos(); return; }
    if(tab === "calendario"){ pintaCalendario(); return; }
    pintaGerencia(); return;
  }
  let html = panelPlantilla() + panelCascada() + panelEdicion(), total = 0, hechos = 0;   /* las extra viven en el menú y en su sección */
  const sumar = (tareas, pre) => (tareas||[]).forEach((t, i)=>{
    if(t.aviso) return;
    const k = pre + i, partes = t.partes || [];
    if(partes.length){ total += partes.length;
      partes.forEach((_, j)=>{ if(hecha(k+"."+j)) hechos++; });
    } else { total += 1; if(hecha(k)) hechos++; }
  });

  const W = semanaDe(fechaSel);
  const NOMBRE_DIA = DIAS.find(x=>x[0]===W)[1];
  const ES_HOY = (fechaSel === DIA);

  if(quien.puesto === "tienda"){
    const P = DATOS.tienda[tab];
    if(tab === "cierre"){
      P.forEach((s, si)=>{ html += bloque(s.sec, s.tareas, si + "_"); sumar(s.tareas, si + "_"); });
      document.getElementById("sub").textContent = "Cierre · " + NOMBRE_DIA + " " + bonito(fechaSel);
    } else {
      const pre = tab[0] + "d";
      html += bloqueEncargosAviso();                /* lo más gordo, arriba */
      html += bloqueArreglar();
      html += bloque("Lo de siempre · en este orden", P.rutina, tab[0] + "r");
      html += bloque("Lo de hoy · " + NOMBRE_DIA, P.porDia[W] || [], pre,
                     "");
      html += bloquePasadas();
      html += bloqueSinDia(pre);
      if(W === "LUN" && tab === "manana") html += bloqueRecuento(true, false);
      html += bloqueViene(fechaSel);
      html += bloque("Antes de irse", P.antes, tab[0] + "a");
      sumar(P.rutina, tab[0] + "r"); sumar(P.porDia[W], pre); sumar(P.antes, tab[0] + "a");
      document.getElementById("sub").textContent =
        (tab === "manana" ? "Mañana" : "Tarde") + " · " + NOMBRE_DIA + " " + bonito(fechaSel) +
        (ES_HOY ? "" : "  (no es hoy)");
    }
  } else {
    if(tab === "apertura"){
      const P = DATOS.coordinacion.apertura[patron];
      if(P.nota) html += `<div class="nota-patron"><b>${P.nombre}.</b> ${P.nota}</div>`;
      P.bloques.forEach((b, bi)=>{ html += bloque(b.sec, b.tareas, patron + bi + "_");
                                    sumar(b.tareas, patron + bi + "_"); });
      document.getElementById("sub").textContent = "Apertura · " + P.nombre;
    } else if(tab === "dia"){
      html += bloqueEncargosAviso();                /* lo más gordo, arriba */
      html += bloqueArreglar();
      html += bloque("Rutina · todos los días", DATOS.coordinacion.dia.rutina, "dr");
      html += bloque("Lo de hoy · " + NOMBRE_DIA,
                     DATOS.coordinacion.dia.porDia[W] || [], "dd",
                     "");
      html += bloquePasadas();
      html += bloqueSinDia("dd");
      if(W === "LUN") html += bloqueRecuento(true, true);
      html += bloqueViene(fechaSel);
      sumar(DATOS.coordinacion.dia.rutina, "dr");
      sumar(DATOS.coordinacion.dia.porDia[W], "dd");
      document.getElementById("sub").textContent = "El día · " + NOMBRE_DIA + " " + bonito(fechaSel) +
        (ES_HOY ? "" : "  (no es hoy)");
    } else {
      DATOS.coordinacion.cierre.forEach((s, si)=>{
        html += bloque(s.sec, s.tareas, "c" + si + "_"); sumar(s.tareas, "c" + si + "_"); });
      document.getElementById("sub").textContent = "Cierre de coordinación";
    }
  }

  document.getElementById("cuerpo").innerHTML = html;
  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ptxt").textContent = hechos + " de " + total;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";

  const c = document.getElementById("cuerpo");
  const origenDe = (k) => (k.startsWith("arr") ? ARR[k] : (k.startsWith("pas") ? PAS[k] : null));


  /* los desplegables de opciones (el tipo de bollería) */
  c.querySelectorAll("[data-opciones]").forEach(sel=>{
    const k = sel.dataset.opciones;
    if(OPCIONES[k]) sel.value = OPCIONES[k];
    sel.addEventListener("change", ()=>{ OPCIONES[k] = sel.value; });
  });

  /* borrar un encargo (solo la gerencia) */
  document.querySelectorAll("[data-borrar-enc]").forEach(b=>{
    b.addEventListener("click", async e=>{
      e.stopPropagation();
      await encargoBorrar(b.dataset.borrarEnc);
    });
  });

  c.querySelectorAll(".parte").forEach(p=>{
    p.addEventListener("click", e=>{ e.stopPropagation();
      const pk = p.dataset.parte;
      const dueño = pk.startsWith("arr") ? ARR[pk.split(".")[0]]
                  : pk.startsWith("pas") ? PAS[pk.split(".")[0]] : null;
      if(dueño){
        const k2 = dueño.k + "." + pk.split(".")[1];
        tocarEn(dueño.f, k2, !hechaEn(dueño.f, k2));
        return;
      }
      tocar(pk, !hecha(pk)); });
  });

  /* el menú de «¿para cuándo lo pasas?» */
  c.querySelectorAll(".btn-pasar").forEach(b=>{
    b.addEventListener("click", e=>{
      e.stopPropagation();
      const k = b.dataset.pasar;
      PICK[k] = !PICK[k];
      pinta();
    });
  });
  c.querySelectorAll(".op-pasar").forEach(b=>{
    b.addEventListener("click", async e=>{
      e.stopPropagation();
      const clave = b.dataset.clave;
      let destino = null;
      try{ destino = JSON.parse(b.dataset.destino || "null"); }catch(_){ destino = null; }
      if(!clave || !destino){
        ponerSync("error", "No se pudo pasar: falta el destino");
        return;
      }
      Object.keys(PICK).forEach(x=>delete PICK[x]);
      await trasladar(clave, destino);
      pinta();                      /* el menú se cierra siempre, salga bien o mal */
    });
  });
  c.querySelectorAll(".inp-pasar").forEach(inp=>{
    inp.addEventListener("change", async e=>{
      const clave = inp.dataset.clave;
      if(!clave || !inp.value){
        ponerSync("error", "Elige un día");
        return;
      }
      Object.keys(PICK).forEach(x=>delete PICK[x]);
      await trasladar(clave, { f: inp.value, t: tab });
      pinta();
    });
  });
}

/* Manda el destino al servidor. */
async function trasladar(claveCompleta, destino){
  try{
    const r = await fetch("/api/trasladar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, clave: claveCompleta, destino: destino })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    traslados = d.traslados || {};
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Pasada");
  }catch(e){
    ponerSync("error", "No se pudo pasar · se reintenta");
  }
}

/* ------------------------------------------------------------------ arrancar */
async function entrar(){
  document.getElementById("login").hidden = true;
  document.getElementById("app").hidden = false;
  /* el nombre de quien entra: antes solo había dos casos y la Jefa
     caía en «Coordinadora». Ahora tiene el suyo. */
  const COMO_SE_LLAMA = { tienda: "Tienda ", coordinacion: "Coordinadora ", gerencia: "Jefa" };
  const COMO_SE_LLAMA_PUESTO = { tienda: "Tienda", coordinacion: "Coordinación", gerencia: "Jefa" };
  document.getElementById("q-nombre").textContent =
    quien.puesto === "gerencia"
      ? "Jefa"
      : COMO_SE_LLAMA[quien.puesto] + quien.numero;
  document.getElementById("titulo").textContent =
    COMO_SE_LLAMA_PUESTO[quien.puesto] || "";
  tab = "";
  await cargar();
  fechaSel = DIA || new Date().toLocaleDateString("en-CA");   // se empieza en hoy
  pintaTabs();
  pinta();
  /* ya no se apunta la hora: la app ya sabe el turno por la plantilla */
}

/* NADA DE FALLOS CALLADOS: si algo revienta, se ve aquí. */
function ensenarFallo(que){
  try{
    const c = document.getElementById("fallo");
    c.style.display = "block";
    c.querySelector("span").textContent = String(que).slice(0, 220);
  }catch(e){}
}
window.addEventListener("error", e => ensenarFallo((e.message||"error") +
  (e.filename ? "  (linea " + e.lineno + ")" : "")));
window.addEventListener("unhandledrejection", e =>
  ensenarFallo("promesa: " + (e.reason && e.reason.message || e.reason)));

/* el escuchador de las tareas: se pone UNA vez y no se vuelve a tocar */
document.getElementById("cuerpo").addEventListener("click", atenderClic);

/* arranque */
const VERSION = "v-2026-10-26-77";
try{ document.getElementById("version").textContent = VERSION; }catch(e){}

pintarLogin();
try{
  const g = localStorage.getItem("tienda-quien");
  if(g){ const q = JSON.parse(g); selPuesto = q.puesto; selNumero = q.numero;
         pintarLogin(); quien = q; entrar(); }
}catch(e){}
</script>
</body>
</html>
"""

_LOGO_VERDE = "data:image/png;base64," + __import__("base64").b64encode(
    open("docs/marca/logo-o-verde.png", "rb").read()).decode()
html = (HTML.replace("__LOGO_VERDE__", _LOGO_VERDE)
            .replace("__LOGO__", LOGO)
            .replace("__DATOS__", json.dumps(DATOS, ensure_ascii=False)))
open("docs/nube/public/index.html", "w", encoding="utf-8").write(html)
print(f"\n  escrito docs/nube/public/index.html ({len(html):,} caracteres)")