"""Genera la pantalla de La persona de tienda, con MAÑANA y TARDE."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- MAÑANA
M_RUTINA = [
    {"t": "Tarea diaria urgente", "n": "La pone coordinación o gerencia"},
    {"t": "Frentear y reponer, siempre ordenado por caducidades",
     "partes": ["Fruta", "Leche", "Yogures", "Congelado"]},
    {"t": "Subir monta"},
    {"t": "Apuntar el pan", "n": "Quizá pase a coordinadoras · ver la ventana del pan"},
    {"t": "Tickar los pedidos que llegan y comprobar que todo pasa"},
    {"t": "Reponer bebidas frías", "n": "No pegar atrás"},
    {"t": "Tarea diaria complementaria", "n": "La pone coordinación o gerencia"},
    {"t": "Cocina: fregar y recoger todo", "n": "Dejar las fregaderas limpias"},
]
M_ANTES = [
    {"t": "Revisar la charcutería",
     "partes": ["Que no queden piezas sin tapar", "Que estén las puertas cerradas"]},
    {"t": "Apagar luces"},
    {"t": "Comprobar las puertas",
     "partes": ["Las de los congeladores, cerradas", "Las de los refrigeradores, cerradas"]},
    {"t": "Tirar basura", "n": "Si está llena"},
    {"t": "Tirar cartones"},
    {"t": "Tirar plásticos"},
    {"t": "El almacén", "n": "Igual que en el cierre de la noche",
     "partes": ["Apagar 2 luces", "Apagar el ventilador",
                "Dejar los dos carros del monta arriba", "Cerrar con llave"]},
    {"t": "Cerrar la puerta del exterior de la tienda",
     "n": "Al terminar la mañana: la tienda cierra de 14:30 a 17:00"},
    {"t": "Apagar los ventiladores y los extractores"},
    {"t": "Poner la alarma"},
    {"t": "Cerrar la persiana"},
]
M_DIA = {
    "LUN": [
        {"t": "Pollos que han sobrado del fin de semana",
         "partes": ["Envasar con salsa los cocinados", "Congelar los frescos", "Congelar la salsa"]},
        {"t": "Contar", "partes": ["Pollos", "Codillos", "Patatas normales", "Patatas bravas"]},
        {"t": "Limpiar la envasadora", "n": "Con un paño y agua · habrá documento"},
        {"t": "Limpiar las fregonas",
         "n": "Dejar con lejía · son varias fregonas · el resto de días solo se sacuden"},
        {"t": "Limpiar el baño"},
        {"t": "Limpiar y desinfectar la cámara de pollos",
         "partes": ["Suelo, puerta derecha", "Suelo, puerta izquierda", "Puertas",
                    "Baldas superiores derecha", "Baldas inferiores derecha",
                    "Baldas superiores izquierda"],
         "producto": True},
    ],
    "MAR": [
        {"t": "Limpiar y desinfectar el horno de pan", "producto": True},
        {"t": "Limpiar y desinfectar la charcutería", "producto": True,
         "partes": ["Exposición", "Zona de almacenaje inferior", "Todos los cristales",
                    "Todas las puertas"]},
        {"t": "Limpiar y desinfectar la mesa de charcutería", "n": "Entera", "producto": True},
    ],
    "MIE": [
        {"t": "Limpiar el suelo debajo del horno de pan"},
        {"t": "Limpiar la zona de bandejas de horno"},
        {"t": "Limpiar el congelado",
         "partes": ["Preparado de paella", "Gambas", "Merluza", "Tarrinas"],
         "n": "Dos cubetas mínimo, ir alternando"},
    ],
    "JUE": [
        {"t": "Colocar el camión y todo el género que ha llegado",
         "n": "Es la tarea del día: llega el camión y con eso se repone todo"},
    ],
    "VIE": [
        {"aviso": "No hay tarea propia. Se termina lo que quedó pendiente a lo largo de la semana."},
    ],
    "SAB": [
        {"t": "Limpiar y desinfectar la charcutería", "producto": True,
         "partes": ["Exposición", "Zona de almacenaje inferior", "Todos los cristales",
                    "Todas las puertas"]},
        {"t": "Limpiar y desinfectar la mesa de charcutería", "n": "Entera", "producto": True},
        {"t": "Revisar toda la fruta y verdura", "n": "Con desplegable · misma estructura que el miércoles por la tarde"},
    ],
    "DOM": [
        {"aviso": "Hay muchos clientes: solo se puede hacer trabajo de caja y reponer lo que dé tiempo."},
    ],
}

# ---------------------------------------------------------------- TARDE
T_RUTINA = [
    {"t": "Reponer, frentear y colocar, respetando caducidades",
     "partes": ["Fruta", "Leche", "Yogures", "Congelado",
                "Zona gominolas y txutxes",
                "Zona snacks: Matutano", "Zona snacks: Tosfrit", "Zona snacks: Paquetería surtida"],
     "n": "Lo mismo que a la mañana, más gominolas y txutxes, más los tres snacks"},
    {"t": "Colocar monta", "n": "El que se ha subido por la mañana"},
    {"t": "Lineales", "partes": ["Frentear", "Rellenar", "Ordenar"]},
    {"t": "Reponer bebidas frías", "n": "No pegar atrás"},
    {"t": "Tarea diaria complementaria", "n": "La pone coordinación o gerencia"},
    {"t": "Vaciar agua cámara fruta", "n": "Las dos bandejas"},
    {"t": "Limpiar las fregonas",
     "n": "Solo se sacuden · son varias fregonas · el lunes por la mañana se dejan con lejía"},
    {"t": "Cocina: fregar y recoger todo", "n": "Dejar las fregaderas limpias"},
    {"t": "Limpiar cajas de cobro", "n": "Con brocha",
     "partes": ["Delante", "Detrás", "Pantalla"]},
]
T_ANTES = [
    # NO se repite aqui lo que ya esta en el cierre de la noche:
    #   apagar luces · comprobar puertas · tirar basura/cartones/plasticos
    {"t": "Revisar la fruta más perecedera",
     "n": "La que esté guardada en el carro, en la cámara de la fruta"},
    {"t": "Revisar la charcutería",
     "partes": ["Que no queden piezas sin tapar", "Que estén las puertas cerradas"]},
]
T_DIA = {
    "LUN": [
        {"t": "Limpiar zona txutxes", "partes": ["Izquierda de caja", "Frente de caja"]},
        {"t": "Limpiar el mueble pan de Zuaza"},
        {"t": "Limpiar el expositor azul", "n": "Junto a caja"},
        {"t": "Limpiar el mueble expositor de madera", "n": "Frente a caja"},
        {"t": "Hacer bolsitas",
         "partes": ["Txutxes 1 €", "Torcidas rojas", "Torcidas negras", "Torcidas mixtas"]},
    ],
    "MAR": [
        {"t": "Limpiar y ordenar la zona de cajas",
         "partes": ["Caja", "Baldas / lineales", "TPV"]},
        {"t": "Limpiar etiqueteros por zonas", "n": "Con trapo húmedo · las zonas, en otro desplegable"},
        {"t": "Hacer bolsitas",
         "partes": ["Txutxes 1 €", "Torcidas rojas", "Torcidas negras", "Torcidas mixtas"]},
    ],
    "MIE": [
        {"t": "Limpiar el microondas y las baldas donde está",
         "n": "Por dentro y por fuera · el micro y las baldas de alrededor"},
        {"t": "Centrar agua"},
        {"t": "Reponer utillaje", "n": "Con una casilla con todo lo que hay que reponer"},
        {"t": "Limpiar el mueble de bandejas del horno", "n": "Cesto de mimbre incluido"},
        {"t": "Limpiar los congeladores por fuera",
         "partes": ["Los bordes", "Los frentes", "Entre cristales"]},
        {"t": "Revisar toda la verdura y fruta",
         "n": "Lo mismo que el sábado por la mañana: aparece en los dos sitios con la misma estructura"},
    ],
    "JUE": [
        {"t": "Ordenar y colocar la zona de galletas 1 €"},
        {"t": "Limpiar el exterior entero de la cámara de los yogures"},
        {"t": "Limpiar una balda de yogures"},
        {"t": "Fregar la cámara de la fruta"},
        {"t": "Poner cartones en las escaleras", "n": "Felpudo"},
        {"t": "Abrir la puerta del lateral de la tienda"},
    ],
    "VIE": [
        {"aviso": "No hay tarea propia. Se termina lo que quedó pendiente a lo largo de la semana."},
    ],
    "SAB": [
        {"t": "Preparar las bandejas de bollería a granel",
         "n": "Necesita el utillaje y la bollería que coordinación sube por la mañana",
         "avisa": "bolleria",
         "opciones": ["Donettes", "Palmeras surtidas", "Palmeras choco", "Palmeras kinder",
                      "Palmeras coco", "Lazos choco", "Lazos azúcar", "Lazos rayados",
                      "Morenitos", "Varios"]},
        {"t": "Reponer utillaje", "n": "Con una casilla con todo lo que hay que reponer"},
    ],
    "DOM": [
        {"aviso": "Hay muchos clientes: solo se puede hacer trabajo de caja y reponer lo que dé tiempo."},
        {"t": "Fregar la cámara de la fruta"},
        {"t": "Poner cartones en las escaleras", "n": "Felpudo"},
        {"t": "Abrir la puerta del lateral de la tienda"},
    ],
}

# ---------------------------------------------------------------- CIERRE
CIERRE = [
    {"sec": "A LO LARGO DE LA TARDE · antes de las 20:45", "tareas": [
        {"t": "Fregar las escaleras y la entrada (la calle)"},
        {"t": "Fregar la rampa", "n": "Lunes y jueves"},
        {"t": "Cambiar todas las bolsas de basura"},
        {"t": "Limpiar el mueble expositor de pan"},
        {"t": "Limpiar todos los cristales", "partes": [
            "Charcutería",
            "Congelador horizontal: verdura y comida precocinada",
            "Congelador horizontal: pescado",
            "Congelador horizontal: helados impulso",
            "Congelador horizontal: helados paquetería",
            "Cámara refrigeradora: Pepsi",
            "Cámara refrigeradora: Bollería",
            "Cámara refrigeradora: Charcutería envasada",
            "Cámara refrigeradora: Expositor Verdura",
            "Cámara refrigeradora: Expositor Yogures",
            "Cámara expositora de carne (frescos cerdo y pollo) y elaborado"]},
        {"t": "Barrer la tienda"},
        {"t": "Tirar basuras, cartones y plásticos",
         "n": "Los cartones hay que desmontarlos"},
    ]},
    {"sec": "A LAS 20:45 · EL AIRE Y LAS VENTANAS", "tareas": [
        {"t": "Apagar el aire acondicionado cuando sea necesario", "n": "En verano · irá con instrucciones y foto"},
        {"t": "Apagar ventiladores, extractor de cocina y extractor del horno de pan",
         "n": "En verano"},
        {"t": "Encender los extractores de ventilación de la tienda",
         "n": "El resto del año · graduar según necesidades"},
        {"t": "Recoger los toldos", "n": "El de la calle y el del lucernario"},
        {"t": "Abrir o cerrar las ventanas del lucernario", "n": "Según necesidades"},
    ]},
    {"sec": "RECOGER", "tareas": [
        {"t": "Recoger la fruta delicada y las lechugas",
         "n": "A la cámara de fruta de la trastienda, en un carro"},
        {"t": "Recoger la bollería grande y la pequeña"},
        {"t": "Recoger el pan de Zuaza", "n": "Sólo los sábados"},
        {"t": "Quitar la pila de fruta de oferta de al lado de caja", "n": "Sólo los sábados"},
    ]},
    {"sec": "DESINFECTAR", "tareas": [
        {"t": "Desinfectar las tablas de cortar"},
        {"t": "Desinfectar la termoselladora"},
        {"t": "Desinfectar la cortadora",
         "n": "Hay que dejarla desmontada y la tapa se friega"},
        {"t": "Apagar la luz de la charcu",
         "n": "¡MUCHO CUIDADO! El botón de la luz y el de encendido están muy cerca: " +
              "alguna vez se ha apagado entera y se ha perdido género"},
        {"t": "Comprobar que las puertas de congeladores y refrigeradores estén bien cerradas"},
    ]},
    {"sec": "APAGAR LUCES", "tareas": [
        {"t": "Apagar la luz: Cámara bollería / repostería"},
        {"t": "Apagar la luz: Charcu"},
        {"t": "Apagar la luz: Verdura"},
        {"t": "Apagar la luz: Charcutería envasada"},
        {"t": "Apagar la luz: Yogures"},
        {"t": "Apagar la luz: Cámara expositora de carne y elaborado"},
    ]},
    {"sec": "LA CAJA", "tareas": [
        {"t": "Hacer la caja", "n": "Irá con una pestaña de instrucciones"},
    ]},
    {"sec": "APAGAR", "tareas": [
        {"t": "Apagar las balanzas"},
        {"t": "Apagar la tele de las cámaras de videovigilancia"},
        {"t": "Apagar el detector de billetes falsos"},
    ]},
    {"sec": "DEJAR CARGANDO", "tareas": [
        {"t": "Dejar cargando el teléfono"},
        {"t": "Dejar cargando el datáfono"},
        {"t": "Dejar cargando la tablet de la tienda"},
        {"t": "Dejar cargando la tablet de la cocina", "n": "Viernes tarde y sábados tarde"},
    ]},
    {"sec": "PANTALLAS Y SUELO", "tareas": [
        {"t": "Limpiar las pantallas de los ordenadores con un trapo húmedo",
         "n": "Hay uno específico para eso"},
        {"t": "Fregar la tienda",
         "n": "Regain los martes, jueves y sábados · lejía amarilla lunes, miércoles, " +
              "viernes y domingos"},
        {"t": "Echar veneno para las hormigas en la puerta", "n": "En época de verano"},
    ]},
    {"sec": "EL ALMACÉN", "tareas": [
        {"t": "Apagar 2 luces del almacén"},
        {"t": "Apagar el ventilador del almacén"},
        {"t": "Dejar los dos carros del monta arriba"},
        {"t": "Cerrar el almacén con llave"},
    ]},
    {"sec": "CERRAR LA TIENDA", "tareas": [
        {"t": "Cerrar la puerta del exterior de la tienda",
         "n": "Los jueves y domingos por la tarde se deja abierta"},
        {"t": "Poner la alarma de la tienda"},
        {"t": "Cerrar la persiana con las dos cerraduras",
         "n": "La normal y la de seguridad"},
    ]},
]

D = {"manana": {"rutina": M_RUTINA, "antes": M_ANTES, "porDia": M_DIA},
     "tarde": {"rutina": T_RUTINA, "antes": T_ANTES, "porDia": T_DIA},
     "cierre": CIERRE,
     "productos": ["AL28", "Otro (¿cuál?)"]}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La persona de tienda · Supermercado Malato</title>
<style>
  :root{
    --verde:#2EC258; --verde-oscuro:#1E9A45; --verde-claro:#5CD47F;
    --verde-suave:#EFFAF2; --tinta:#13251A; --gris:#5E6E63; --borde:#D6EDDD;
    --azul:#1E6FA8; --ambar:#D97706; --rojo:#C62828;
  }
  *{box-sizing:border-box}
  body{margin:0; background:var(--verde-suave); color:var(--tinta);
       font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.5;
       -webkit-tap-highlight-color:transparent}
  header{background:linear-gradient(135deg,var(--verde) 0%,var(--verde-oscuro) 100%);
         color:#fff; padding:15px 20px; text-shadow:0 1px 2px rgba(0,0,0,.2)}
  .fila-sup{display:flex; align-items:center; gap:14px; flex-wrap:wrap}
  .logo{width:52px; height:52px; flex:0 0 auto; background:#fff; border-radius:12px;
        display:flex; align-items:center; justify-content:center; color:var(--verde-oscuro);
        text-align:center;
        border:none; text-shadow:none; padding:2px}
  header h1{margin:0; font-size:20px; letter-spacing:-.3px}
  header .sub{font-size:12.5px; opacity:.95; margin-top:1px}
  .prog{margin-top:12px}
  .prog .txt{display:flex; justify-content:space-between; font-size:12.5px; margin-bottom:5px; opacity:.95}
  .prog .barra{height:9px; background:rgba(255,255,255,.28); border-radius:5px; overflow:hidden}
  .prog .barra i{display:block; height:100%; background:#fff; width:0; transition:width .3s ease;
                 border-radius:5px}
  main{max-width:760px; margin:0 auto; padding:14px 16px 70px}

  .turnos{display:flex; gap:8px; margin-bottom:14px}
  .turno-btn{flex:1; border:2px solid var(--verde); background:#fff; color:var(--verde-oscuro);
             border-radius:11px; padding:11px; font-size:15px; font-weight:700; cursor:pointer;
             font-family:inherit}
  .turno-btn[aria-pressed=true]{background:var(--verde); color:#fff}

  .dias{display:flex; gap:5px; overflow-x:auto; padding-bottom:6px; margin-bottom:16px}
  .dia-btn{flex:0 0 auto; border:1px solid var(--borde); background:#fff; border-radius:9px;
           padding:7px 11px; font-size:12.5px; font-weight:600; cursor:pointer;
           font-family:inherit; color:var(--verde-oscuro); min-width:48px; text-align:center}
  .dia-btn[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dia-btn.hoy{box-shadow:0 0 0 2px var(--verde-claro) inset}

  h2.bloque{font-size:15.5px; margin:22px 0 9px; padding-bottom:7px;
            border-bottom:2px solid var(--verde); color:var(--verde-oscuro);
            display:flex; justify-content:space-between; align-items:baseline; gap:10px}
  h2.bloque small{font-weight:400; font-size:11.5px; color:var(--gris)}

  .lista{background:#fff; border:1px solid var(--borde); border-radius:12px; overflow:hidden}
  .item{border-top:1px solid #F2F7F3}
  .item:first-child{border-top:none}
  .cab-item{display:flex; gap:11px; align-items:flex-start; padding:11px 14px; cursor:pointer}
  .cab-item:hover{background:#FAFDFB}
  .item.hecha .cab-item{background:var(--verde-suave)}
  .caja{width:20px; height:20px; flex:0 0 auto; border-radius:6px; border:2px solid var(--borde);
        margin-top:1px; display:flex; align-items:center; justify-content:center;
        font-size:11px; color:#fff}
  .item.hecha .caja{background:var(--verde); border-color:var(--verde)}
  .item.hecha .caja::after{content:"✓"}
  .caja.parcial{background:var(--verde-claro); border-color:var(--verde-claro)}
  .caja.parcial::after{content:"–"}
  .txt{flex:1 1 auto; font-size:14px}
  .item.hecha .txt b{text-decoration:line-through; color:var(--gris)}
  .txt b{font-weight:500}
  .n{display:block; font-size:11.5px; color:var(--gris); margin-top:2px}
  .fuera{font-size:10px; font-weight:700; color:#fff; background:var(--gris);
         border-radius:5px; padding:1px 6px; margin-left:6px}
  .tag{font-size:10.5px; font-weight:700; color:var(--azul); background:#E8F2FA;
       border-radius:5px; padding:1px 7px; margin-left:6px; white-space:nowrap}
  .partes{display:none; padding:0 14px 12px 45px}
  .item.abierta .partes{display:block}
  .parte{display:flex; gap:9px; align-items:flex-start; padding:5px 0; cursor:pointer;
         font-size:13px; color:var(--gris)}
  .parte .pc{width:16px; height:16px; flex:0 0 auto; border-radius:5px;
             border:1.5px solid var(--borde); margin-top:2px; display:flex;
             align-items:center; justify-content:center; font-size:9px; color:#fff}
  .parte.hecha .pc{background:var(--verde); border-color:var(--verde)}
  .parte.hecha .pc::after{content:"✓"}
  .parte.hecha{color:var(--tinta); text-decoration:line-through}
  .producto{margin-top:8px; display:flex; gap:8px; align-items:center; flex-wrap:wrap}
  .producto span{font-size:11.5px; color:var(--gris)}
  .producto select{font-family:inherit; font-size:12px; padding:5px 8px; border-radius:7px;
                   border:1px solid var(--borde); background:#fff; color:var(--tinta)}

  .aviso-item{display:flex; gap:11px; padding:11px 14px; font-size:13.5px; color:#8A4B00;
              background:#FFF8E6}
  .aviso{background:#FFF8E6; border:1px solid #F0DCA6; border-left:4px solid var(--ambar);
         border-radius:11px; padding:13px 16px; font-size:13px; margin-top:18px}
  .aviso b{color:#8A4B00}
  .aviso ul{margin:7px 0 0; padding-left:19px}
  footer{max-width:760px; margin:0 auto; padding:0 16px 60px; color:var(--gris); font-size:12px}
</style>
</head>
<body>
<header>
  <div class="fila-sup">
    <div class="logo"><img src="__LOGO__" alt="Malato"></div>
    <div><h1>La persona de tienda</h1><div class="sub" id="sub"></div></div>
  </div>
  <div class="prog">
    <div class="txt"><span id="ptxt">0 de 0</span><span id="ppct">0 %</span></div>
    <div class="barra"><i id="pbar"></i></div>
  </div>
</header>

<main>
  <div class="turnos" id="turnos"></div>
  <div class="dias" id="dias"></div>
  <div id="cuerpo"></div>

  <div class="aviso">
    <b>Pendiente de la propiedad</b>
    <ul>
      <li><b>La lista del desplegable</b> de fruta y verdura.</li>
      <li><b>Las zonas de los etiqueteros</b> (martes tarde).</li>
      <li><b>La casilla de utillaje</b>: qué hay que reponer.</li>
      <li><b>El cierre de la noche</b>, que no es el «antes de irse» de la mañana.</li>
    </ul>
  </div>
</main>

<footer>El orden y las palabras son los de la propiedad. El producto de limpieza es AL28 (si se usa otro, se cambia).</footer>

<script>
const D = __DATOS__;
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
const HOY = ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date().getDay()];
let turno = "manana", dia = HOY;
const hechas = {};

function pintaTurnos(){
  const c = document.getElementById("turnos"); c.innerHTML = "";
  [["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"]].forEach(([k, n])=>{
    const b = document.createElement("button");
    b.className = "turno-btn"; b.type = "button"; b.textContent = n;
    b.setAttribute("aria-pressed", k === turno);
    b.addEventListener("click", ()=>{ turno = k; pintaTurnos(); pinta(); });
    c.appendChild(b);
  });
}
function pintaDias(){
  const c = document.getElementById("dias"); c.innerHTML = "";
  DIAS.forEach(([k, n])=>{
    const b = document.createElement("button");
    b.className = "dia-btn" + (k === HOY ? " hoy" : "");
    b.type = "button"; b.textContent = n.slice(0,3);
    b.setAttribute("aria-pressed", k === dia);
    b.addEventListener("click", ()=>{ dia = k; pintaDias(); pinta(); });
    c.appendChild(b);
  });
}

const REG = {};   // clave -> tarea, para saber si tiene partes al pinchar

function bloque(titulo, tareas, prefijo){
  if(!tareas) tareas = [];
  const reales = tareas.filter(t => !t.aviso);
  let html = `<h2 class="bloque">${titulo}<small>${reales.length} ${
    reales.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;
  if(!tareas.length){
    return html + `<div class="aviso-item">Este día no tiene tareas.</div></div>`;
  }
  tareas.forEach((t, i)=>{
    if(t.aviso){
      html += `<div class="aviso-item">${t.aviso}</div>`;
      return;
    }
    const k = prefijo + i;
    REG[k] = t;
    const partes = t.partes || [];
    const hp = partes.filter((_, j) => hechas[k + "." + j]).length;
    const abierta = hechas["ab:" + k];
    const completa = partes.length ? hp === partes.length : hechas[k];
    const parcial = partes.length && hp > 0 && hp < partes.length;
    let sub = "";
    if(partes.length){
      sub = `<div class="partes">` + partes.map((p, j)=>
        `<div class="parte ${hechas[k+"."+j]?"hecha":""}" data-pk="${k+"."+j}">
           <span class="pc"></span><span>${p}</span></div>`).join("");
      if(t.producto){
        sub += `<div class="producto"><span>Con qué producto:</span><select>` +
          D.productos.map(x=>`<option>${x}</option>`).join("") + `</select></div>`;
      }
      sub += `</div>`;
    }
    const fuera = t.fuera ? `<span class="fuera">${t.fuera}</span>` : "";
    const cuenta = partes.length ? `<span class="tag">${hp} / ${partes.length} partes</span>` : "";
    const n = t.n ? `<span class="n">${t.n}</span>` : "";
    html += `<div class="item ${completa?"hecha":""} ${abierta?"abierta":""}" data-k="${k}">
        <div class="cab-item"><span class="caja ${parcial?"parcial":""}"></span>
        <span class="txt"><b>${t.t}</b>${fuera}${cuenta}${n}</span></div>${sub}</div>`;
  });
  return html + "</div>";
}

function pintaCierre(){
  let total = 0, hechos = 0;
  const pre = "c";
  D.cierre.forEach((s, si)=>(s.tareas||[]).forEach((t, i)=>{
    const k = pre + si + "_" + i, partes = t.partes || [];
    if(partes.length){ total += partes.length;
      partes.forEach((_, j)=>{ if(hechas[k+"."+j]) hechos++; });
    } else { total += 1; if(hechas[k]) hechos++; }
  }));

  let html = "";
  D.cierre.forEach((s, si)=>{
    html += bloque(s.sec, s.tareas, pre + si + "_");
  });
  document.getElementById("cuerpo").innerHTML = html;

  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ptxt").textContent = hechos + " de " + total;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";
  document.getElementById("sub").textContent = "Cierre · " + DIAS.find(x=>x[0]===dia)[1];
  enganchar();
}

function enganchar(){
  const c = document.getElementById("cuerpo");
  c.querySelectorAll(".item").forEach(it=>{
    const k = it.dataset.k;
    const t = REG[k];
    it.querySelector(".cab-item").addEventListener("click", e=>{
      if(e.target.closest(".partes")) return;
      if(t && t.partes && t.partes.length) hechas["ab:"+k] = !hechas["ab:"+k];
      else hechas[k] = !hechas[k];
      pinta();
    });
  });
  c.querySelectorAll(".parte").forEach(p=>{
    p.addEventListener("click", e=>{ e.stopPropagation();
      const pk = p.dataset.pk; hechas[pk] = !hechas[pk]; pinta(); });
  });
}

function pinta(){
  if(turno === "cierre"){ pintaCierre(); return; }
  const P = D[turno];
  let total = 0, hechos = 0;
  const contar = (lista, pre) => (lista||[]).forEach((t, i)=>{
    if(t.aviso) return;
    const k = pre + i, partes = t.partes || [];
    if(partes.length){ total += partes.length;
      partes.forEach((_, j)=>{ if(hechas[k+"."+j]) hechos++; });
    } else { total += 1; if(hechas[k]) hechos++; }
  });
  contar(P.rutina, turno[0] + "r"); contar(P.porDia[dia], turno[0] + "d");
  contar(P.antes, turno[0] + "a");

  document.getElementById("cuerpo").innerHTML =
    bloque("Lo de siempre · en este orden", P.rutina, turno[0] + "r") +
    bloque("Lo de hoy", P.porDia[dia], turno[0] + "d") +
    bloque("Antes de irse", P.antes, turno[0] + "a");

  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ptxt").textContent = hechos + " de " + total;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";
  document.getElementById("sub").textContent =
    (turno === "manana" ? "Mañana" : "Tarde") + " · " + DIAS.find(x=>x[0]===dia)[1];
  enganchar();
}
pintaTurnos(); pintaDias(); pinta();
</script>
</body>
</html>
"""

_LOGO_URI = "data:image/png;base64," + __import__("base64").b64encode(
    open("docs/marca/logo-o-blanco.png", "rb").read()).decode()
html = HTML.replace("__LOGO__", _LOGO_URI).replace("__DATOS__", json.dumps(D, ensure_ascii=False))
with open("docs/momentos/tienda.html", "w", encoding="utf-8") as f:
    f.write(html)
import os
if os.path.exists("docs/momentos/manana-tienda.html"):
    os.remove("docs/momentos/manana-tienda.html")
print(f"  escrito docs/momentos/tienda.html ({len(html):,} caracteres)")
