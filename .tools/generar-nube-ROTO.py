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
  /* ---- lo que viene ---- */
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
let turnoTarea = "";
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
  quien = { puesto: "gerencia", numero: 1, id: "ge1" };
  try { localStorage.setItem("tienda-quien", JSON.stringify(quien)); } catch(e){}
  entrar();
});

document.getElementById("pin-inp").addEventListener("keydown", e=>{
  if(e.key === "Enter"){ e.preventDefault(); document.getElementById("btn-clave").click(); }
});
document.getElementById("btn-salir").addEventListener("click", async ()=>{
  /* sin reloj: el turno lo pone la plantilla */
  try { localStorage.removeItem("tienda-quien"); } catch(e){}
  quien = null; document.getElementById("app").hidden = true;
  document.getElementById("login").hidden = false; pintarLogin();
});

/* ------------------------------------------------------------------ sincronizar */
function ponerSync(estado, texto){
  estadoSync = estado;
  const p = document.getElementById("punto");
  p.className = "punto " + estado;
  document.getElementById("txt-sync").textContent = texto;
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
/* Una fecha que no vale rompe todo lo que venga detrás. Antes, una fecha
   vacía hacía que el cálculo del turno leyera de `undefined` y la aplicación
   se cayera con «Cannot read properties of undefined (reading '2')». */
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
function tocar(k, valor){
  tocarEn(fechaSel, k, valor);
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

async function encargoHecho(id){
  ponerSync("trabajando", "Marcando…");
  try{
    const r = await fetch("/api/encargo-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, quien: quien.id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Hecho");
    pinta();
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
function bloqueEncargos(puesto, fecha, turno, titulo){
  const lista = (encargos || []).filter(e => !e.hecho && e.p === puesto &&
    (e.diario || e.f === fecha) && (!e.turno || !turno || e.turno === turno));
  if(!lista.length) return "";
  let html = "";
  lista.forEach((e, i)=>{
    const k = "enc" + i;
    ENC[k] = e;
    const que = e.que ? `<span class="n">${e.que}</span>` : "";
    const cuando = e.diario ? "hasta que se haga · sale todos los días"
                            : (e.f ? "para el " + bonito(e.f) : "");
    const de = "la puso " + nombreDe(e.q) + (e.h ? " · " + e.h : "");
    const borrar = (quien.puesto === "gerencia")
      ? `<div class="pasarlo"><button class="btn-borrar" data-borrar-enc="${e.id}">Borrar</button></div>`
      : "";
    html += `<div class="item" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${que}
        <span class="extra-de">${cuando} · ${de}</span></span></div>${borrar}</div>`;
  });
  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino: va a SIN HACER.
   La rutina y el «antes de irse» NO se arrastran nunca. */
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
function bloque(titulo, tareas, pre, extra){
  if(!tareas || !tareas.length) return extra || "";
  let html = `<h2 class="bloque">${titulo}<small>${tareas.length} ${
    tareas.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;
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
          DATOS.tienda.productos.map(x=>`<option>${x}</option>`).join("") + `</select></div>`;
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
        <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}</div>`;
  });
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
  const lista = quien.puesto === "tienda"
    ? [["general","General"],["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : quien.puesto === "coordinacion"
    ? [["general","General"],["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : [["general","General"],["turno","Turno"],["calendario","Calendario"]];
  if(!tab) tab = lista[0][0];
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

function pintaCalendario(){
  const trozos = fechaSel.split("-").map(Number);
  const a = trozos[0], m = trozos[1];
  const cuantos = new Date(a, m, 0).getDate();
  const hueco = (new Date(a, m - 1, 1).getDay() + 6) % 7;

  let html = `<div class="cal-cab">
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
    const hay = hayNota || hayEnc;
    const cl = "mes-dia" + (f === DIA ? " hoy" : "") + (f === fechaSel ? " sel" : "") +
               (hay ? " con-nota" : "");
    const punto = hay
      ? `<span class="punto-nota${hayEnc ? " es-encargo" : ""}"></span>` : "";
    html += `<div class="${cl}" data-cf="${f}">${d}${punto}</div>`;
  }
  html += `</div>`;

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
  html += `<div class="nueva-nota fila-tarea">
      <button id="btn-nueva-tarea" class="btn-add-2" type="button">+ Añadir una tarea extra</button>
      <span class="pista">Se le añadirá a sus tareas de ese día y turno</span>
    </div>`;
  if(formTarea){
    const ops = `<option value="tienda"${puestoTarea==="tienda"?" selected":""}>Tienda</option>` +
      `<option value="coordinacion"${puestoTarea==="coordinacion"?" selected":""}>Coordinación</option>` +
      `<option value="gerencia"${puestoTarea==="gerencia"?" selected":""}>Jefa</option>`;
    html += `<div class="nueva-nota">
        <input type="text" id="tarea-txt" maxlength="300"
               placeholder="Qué hay que hacer…" value="${textoTarea}">
        <select id="tarea-puesto">${ops}</select>
        <select id="tarea-turno">
          <option value=""${turnoTarea===""?" selected":""}>Sin turno</option>
          <option value="manana"${turnoTarea==="manana"?" selected":""}>Mañana</option>
          <option value="tarde"${turnoTarea==="tarde"?" selected":""}>Tarde</option>
        </select>
        <button id="tarea-add" class="btn-add" type="button">Añadir</button>
      </div>`;
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
  document.getElementById("tarea-puesto") && document.getElementById("tarea-puesto")
    .addEventListener("change", e=>{ puestoTarea = e.target.value; });
  document.getElementById("tarea-turno") && document.getElementById("tarea-turno")
    .addEventListener("change", e=>{ turnoTarea = e.target.value; });
  document.getElementById("tarea-add") && document.getElementById("tarea-add")
    .addEventListener("click", anadirTareaExtra);
  document.getElementById("btn-nueva-tarea").addEventListener("click", ()=>{
    formTarea = !formTarea;
    pinta();
  });
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

async function anadirTareaExtra(){
  const t = (textoTarea || "").trim();
  if(!t) return;
  const puesto = puestoTarea;
  textoTarea = "";
  formTarea = false;
  await mandarEncargo({ t: t, p: puesto, f: fechaSel, turno: turnoTarea || undefined });
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
  const mias = (encargos || []).filter(e => !e.hecho &&
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  return `<div class="aviso-extra">
      <b>Tienes ${mias.length} ${mias.length===1?"tarea extra":"tareas extra"} hoy</b>
      <span>${mias.map(e => e.t).join(" · ")}</span>
    </div>`;
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
  let html = avisoExtras();
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
    html += bloqueEncargos("gerencia", fechaSel, null, "Tareas extra");
    html += bloqueViene(fechaSel);
    html += bloque("Lo de cada día", DATOS.gerencia.hoy, "gh");
    sumar2(DATOS.gerencia.hoy, "gh");
  } else {
    html += bloqueEncargos("gerencia", fechaSel, null, "Tareas extra");
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

  html += bloque("Las ofertas", DATOS.gerencia.ofertas, "go");

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

  /* las ofertas ya dadas de alta, en orden de fecha.
     El título lleva dentro sus fechas, así que se leen de un vistazo,
     y pueden convivir varias en las mismas fechas. */
  const misOfertas = (encargos || [])
    .filter(e => !e.hecho && String(e.clave || "").startsWith("ofertas:"))
    .sort((a, b) => String(a.f || "").localeCompare(String(b.f || "")) ||
                    String(a.t || "").localeCompare(String(b.t || "")));
  if(misOfertas.length){
    html += `<h2 class="bloque bloque-viene">Ofertas dadas de alta` +
      `<small>${misOfertas.length} · en orden de fecha</small></h2>` +
      `<div class="lista lista-viene">`;
    misOfertas.forEach(e=>{
      html += `<div class="viene-fila">
          <span class="viene-dia">${bonito(e.f)}</span>
          <span class="viene-que">${e.t}</span>
          <span class="viene-quien">${NOMBRE_PUESTO[e.p] || e.p}</span></div>`;
    });
    html += `</div>`;
  }

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

function pinta(){
  if(tab === "general"){ pintaTurnos(); return; }
  if(tab === "calendario"){ pintaCalendario(); return; }
  if(quien.puesto === "gerencia"){
    if(tab === "turno"){ pintaTurnos(); return; }
    if(tab === "calendario"){ pintaCalendario(); return; }
    pintaGerencia(); return;
  }
  let html = avisoExtras(), total = 0, hechos = 0;
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
      html += bloque("Lo de siempre · en este orden", P.rutina, tab[0] + "r");
      html += bloque("Lo de hoy · " + NOMBRE_DIA, P.porDia[W] || [], pre,
                     bloqueEncargos("tienda", fechaSel, tab, ""));
      html += bloquePasadas();
      html += bloqueSinDia(pre);
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
      html += bloque("Rutina · todos los días", DATOS.coordinacion.dia.rutina, "dr");
      html += bloque("Lo de hoy · " + NOMBRE_DIA,
                     DATOS.coordinacion.dia.porDia[W] || [], "dd",
                     bloqueEncargos("coordinacion", fechaSel, null, ""));
      html += bloquePasadas();
      html += bloqueSinDia("dd");
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
  c.querySelectorAll("[data-borrar-enc]").forEach(b=>{
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
window.addEventListener("unhandledrejection", e => {
  const r = e.reason || {};
  const traza = String(r.stack || "").replace(/\s+/g, " ").slice(0, 150);
  ensenarFallo("promesa: " + (r.message || r) + (traza ? "   [" + traza + "]" : ""));

/* el escuchador de las tareas: se pone UNA vez y no se vuelve a tocar */
document.getElementById("cuerpo").addEventListener("click", atenderClic);

/* arranque */
const VERSION = "v-2026-10-23-27";
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
print(f"\n  escrito docs/nube/public/index.html ({len(html):,} caracteres)"  const traza = String(r.stack || "").split(String.fromCharCode(10))
    .slice(1, 3).join("  ·  ");
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
  /* ---- lo que viene ---- */
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
let turnoTarea = "";
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
  quien = { puesto: "gerencia", numero: 1, id: "ge1" };
  try { localStorage.setItem("tienda-quien", JSON.stringify(quien)); } catch(e){}
  entrar();
});

document.getElementById("pin-inp").addEventListener("keydown", e=>{
  if(e.key === "Enter"){ e.preventDefault(); document.getElementById("btn-clave").click(); }
});
document.getElementById("btn-salir").addEventListener("click", async ()=>{
  /* sin reloj: el turno lo pone la plantilla */
  try { localStorage.removeItem("tienda-quien"); } catch(e){}
  quien = null; document.getElementById("app").hidden = true;
  document.getElementById("login").hidden = false; pintarLogin();
});

/* ------------------------------------------------------------------ sincronizar */
function ponerSync(estado, texto){
  estadoSync = estado;
  const p = document.getElementById("punto");
  p.className = "punto " + estado;
  document.getElementById("txt-sync").textContent = texto;
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
/* Una fecha que no vale rompe todo lo que venga detrás. Antes, una fecha
   vacía hacía que el cálculo del turno leyera de `undefined` y la aplicación
   se cayera con «Cannot read properties of undefined (reading '2')». */
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
function tocar(k, valor){
  tocarEn(fechaSel, k, valor);
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

async function encargoHecho(id){
  ponerSync("trabajando", "Marcando…");
  try{
    const r = await fetch("/api/encargo-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, quien: quien.id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Hecho");
    pinta();
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
function bloqueEncargos(puesto, fecha, turno, titulo){
  const lista = (encargos || []).filter(e => !e.hecho && e.p === puesto &&
    (e.diario || e.f === fecha) && (!e.turno || !turno || e.turno === turno));
  if(!lista.length) return "";
  let html = "";
  lista.forEach((e, i)=>{
    const k = "enc" + i;
    ENC[k] = e;
    const que = e.que ? `<span class="n">${e.que}</span>` : "";
    const cuando = e.diario ? "hasta que se haga · sale todos los días"
                            : (e.f ? "para el " + bonito(e.f) : "");
    const de = "la puso " + nombreDe(e.q) + (e.h ? " · " + e.h : "");
    const borrar = (quien.puesto === "gerencia")
      ? `<div class="pasarlo"><button class="btn-borrar" data-borrar-enc="${e.id}">Borrar</button></div>`
      : "";
    html += `<div class="item" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${que}
        <span class="extra-de">${cuando} · ${de}</span></span></div>${borrar}</div>`;
  });
  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino: va a SIN HACER.
   La rutina y el «antes de irse» NO se arrastran nunca. */
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
function bloque(titulo, tareas, pre, extra){
  if(!tareas || !tareas.length) return extra || "";
  let html = `<h2 class="bloque">${titulo}<small>${tareas.length} ${
    tareas.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;
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
          DATOS.tienda.productos.map(x=>`<option>${x}</option>`).join("") + `</select></div>`;
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
        <span class="txt"><b>${t.t}</b>${tag}${n}${quienMarco}</span></div>${sub}</div>`;
  });
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
  const lista = quien.puesto === "tienda"
    ? [["general","General"],["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : quien.puesto === "coordinacion"
    ? [["general","General"],["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : [["general","General"],["turno","Turno"],["calendario","Calendario"]];
  if(!tab) tab = lista[0][0];
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

function pintaCalendario(){
  const trozos = fechaSel.split("-").map(Number);
  const a = trozos[0], m = trozos[1];
  const cuantos = new Date(a, m, 0).getDate();
  const hueco = (new Date(a, m - 1, 1).getDay() + 6) % 7;

  let html = `<div class="cal-cab">
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
    const hay = hayNota || hayEnc;
    const cl = "mes-dia" + (f === DIA ? " hoy" : "") + (f === fechaSel ? " sel" : "") +
               (hay ? " con-nota" : "");
    const punto = hay
      ? `<span class="punto-nota${hayEnc ? " es-encargo" : ""}"></span>` : "";
    html += `<div class="${cl}" data-cf="${f}">${d}${punto}</div>`;
  }
  html += `</div>`;

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
  html += `<div class="nueva-nota fila-tarea">
      <button id="btn-nueva-tarea" class="btn-add-2" type="button">+ Añadir una tarea extra</button>
      <span class="pista">Se le añadirá a sus tareas de ese día y turno</span>
    </div>`;
  if(formTarea){
    const ops = `<option value="tienda"${puestoTarea==="tienda"?" selected":""}>Tienda</option>` +
      `<option value="coordinacion"${puestoTarea==="coordinacion"?" selected":""}>Coordinación</option>` +
      `<option value="gerencia"${puestoTarea==="gerencia"?" selected":""}>Jefa</option>`;
    html += `<div class="nueva-nota">
        <input type="text" id="tarea-txt" maxlength="300"
               placeholder="Qué hay que hacer…" value="${textoTarea}">
        <select id="tarea-puesto">${ops}</select>
        <select id="tarea-turno">
          <option value=""${turnoTarea===""?" selected":""}>Sin turno</option>
          <option value="manana"${turnoTarea==="manana"?" selected":""}>Mañana</option>
          <option value="tarde"${turnoTarea==="tarde"?" selected":""}>Tarde</option>
        </select>
        <button id="tarea-add" class="btn-add" type="button">Añadir</button>
      </div>`;
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
  document.getElementById("tarea-puesto") && document.getElementById("tarea-puesto")
    .addEventListener("change", e=>{ puestoTarea = e.target.value; });
  document.getElementById("tarea-turno") && document.getElementById("tarea-turno")
    .addEventListener("change", e=>{ turnoTarea = e.target.value; });
  document.getElementById("tarea-add") && document.getElementById("tarea-add")
    .addEventListener("click", anadirTareaExtra);
  document.getElementById("btn-nueva-tarea").addEventListener("click", ()=>{
    formTarea = !formTarea;
    pinta();
  });
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

async function anadirTareaExtra(){
  const t = (textoTarea || "").trim();
  if(!t) return;
  const puesto = puestoTarea;
  textoTarea = "";
  formTarea = false;
  await mandarEncargo({ t: t, p: puesto, f: fechaSel, turno: turnoTarea || undefined });
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
  const mias = (encargos || []).filter(e => !e.hecho &&
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  return `<div class="aviso-extra">
      <b>Tienes ${mias.length} ${mias.length===1?"tarea extra":"tareas extra"} hoy</b>
      <span>${mias.map(e => e.t).join(" · ")}</span>
    </div>`;
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
  let html = avisoExtras();
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
    html += bloqueEncargos("gerencia", fechaSel, null, "Tareas extra");
    html += bloqueViene(fechaSel);
    html += bloque("Lo de cada día", DATOS.gerencia.hoy, "gh");
    sumar2(DATOS.gerencia.hoy, "gh");
  } else {
    html += bloqueEncargos("gerencia", fechaSel, null, "Tareas extra");
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

  html += bloque("Las ofertas", DATOS.gerencia.ofertas, "go");

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

  /* las ofertas ya dadas de alta, en orden de fecha.
     El título lleva dentro sus fechas, así que se leen de un vistazo,
     y pueden convivir varias en las mismas fechas. */
  const misOfertas = (encargos || [])
    .filter(e => !e.hecho && String(e.clave || "").startsWith("ofertas:"))
    .sort((a, b) => String(a.f || "").localeCompare(String(b.f || "")) ||
                    String(a.t || "").localeCompare(String(b.t || "")));
  if(misOfertas.length){
    html += `<h2 class="bloque bloque-viene">Ofertas dadas de alta` +
      `<small>${misOfertas.length} · en orden de fecha</small></h2>` +
      `<div class="lista lista-viene">`;
    misOfertas.forEach(e=>{
      html += `<div class="viene-fila">
          <span class="viene-dia">${bonito(e.f)}</span>
          <span class="viene-que">${e.t}</span>
          <span class="viene-quien">${NOMBRE_PUESTO[e.p] || e.p}</span></div>`;
    });
    html += `</div>`;
  }

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

function pinta(){
  if(tab === "general"){ pintaTurnos(); return; }
  if(tab === "calendario"){ pintaCalendario(); return; }
  if(quien.puesto === "gerencia"){
    if(tab === "turno"){ pintaTurnos(); return; }
    if(tab === "calendario"){ pintaCalendario(); return; }
    pintaGerencia(); return;
  }
  let html = avisoExtras(), total = 0, hechos = 0;
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
      html += bloque("Lo de siempre · en este orden", P.rutina, tab[0] + "r");
      html += bloque("Lo de hoy · " + NOMBRE_DIA, P.porDia[W] || [], pre,
                     bloqueEncargos("tienda", fechaSel, tab, ""));
      html += bloquePasadas();
      html += bloqueSinDia(pre);
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
      html += bloque("Rutina · todos los días", DATOS.coordinacion.dia.rutina, "dr");
      html += bloque("Lo de hoy · " + NOMBRE_DIA,
                     DATOS.coordinacion.dia.porDia[W] || [], "dd",
                     bloqueEncargos("coordinacion", fechaSel, null, ""));
      html += bloquePasadas();
      html += bloqueSinDia("dd");
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
  c.querySelectorAll("[data-borrar-enc]").forEach(b=>{
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
window.addEventListener("unhandledrejection", e => {
  const r = e.reason || {};
  const traza = String(r.stack || "").split("\n").slice(1, 3).join("  ·  ");
  ensenarFallo("promesa: " + (r.message || r) + (traza ? "   [" + traza + "]" : ""));
});

/* el escuchador de las tareas: se pone UNA vez y no se vuelve a tocar */
document.getElementById("cuerpo").addEventListener("click", atenderClic);

/* arranque */
const VERSION = "v-2026-10-23-27";
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