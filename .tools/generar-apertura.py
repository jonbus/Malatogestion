"""Genera la pantalla del momento 1 · Apertura, con los DOS patrones."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

PATRONES = {
    "A": {
        "nombre": "Lunes a sábado",
        "abre": "8:00 · sábado 9:00",
        "bloques": [
            {"id": "A0", "titulo": "Al llegar", "ancla": "7:00", "ancla_alt": "8:00", "hora": "07:00",
             "pasos": [
                 {"t": "Quitar la alarma"},
                 {"t": "Encender contadora, ordenadores, cajas, balanzas y horno"},
                 {"t": "Sacar el carro de la cámara de fruta"},
                 {"t": "Sacar la bollería de Malato", "n": "La bollería que sobró del día anterior"},
                 {"t": "Preparar la primera hornada: pan y una bandeja de bollería grande"},
                 {"t": "Quitar los ventiladores, si hiciera falta", "cond": True},
             ]},
            {"id": "A1", "titulo": "Durante la primera hornada", "ancla": "7:00 – 7:30",
             "ancla_alt": "8:00 – 8:30", "hora": "07:05",
             "pasos": [
                 {"t": "Sacar bandejas de bollería de la cámara y colocarlas en el lineal de la caja"},
                 {"t": "Decidir si hace falta bollería pequeña", "n": "Si sí → va en la 3.ª hornada"},
                 {"t": "Mirar si harán falta empanadillas", "n": "Si sí → 4.ª y 5.ª, que tardan dos hornadas"},
                 {"t": "Preparar las siguientes bandejas de pan"},
                 {"t": "Quitar el pan del día anterior, si hubiera", "cond": True},
                 {"t": "Comprobar la devolución de pan"},
                 {"t": "Colocar el carro de la fruta"},
                 {"t": "Echar un vistazo rápido a la fruta", "n": "Por si faltara algo indispensable antes de abrir"},
                 {"t": "Preparar pollo, cerdo, ternera, salchichas, hamburguesas y empanado"},
                 {"t": "Guardar el pedido de fruta", "dia": "lunes y viernes"},
                 {"t": "Hacer la lista del monta"},
                 {"t": "Preparar las cajas de cobro para el día", "n": "Inicio del día"},
                 {"t": "Pintar bollería", "n": "La recién horneada"},
             ]},
            {"id": "A2", "titulo": "Segunda hornada", "ancla": "7:30", "ancla_alt": "8:30", "hora": "07:30",
             "pasos": [{"t": "Bajar al almacén a preparar el monta",
                        "n": "Aquí empieza el momento 2 · Preparación"}]},
            {"id": "A3", "titulo": "Antes de abrir", "ancla": "8:00", "ancla_alt": "9:00", "hora": "07:55",
             "pasos": [{"t": "Encender luces"}, {"t": "Encender música"}]},
            {"id": "A4", "titulo": "Una vez abierta la tienda", "ancla": "8:00 – 9:00",
             "ancla_alt": "9:00 – 10:00", "hora": "08:00",
             "pasos": [
                 {"t": "Pintar la bollería de Malato", "n": "La que sobró del día anterior, que aprovechamos"},
                 {"t": "Limpiar y ordenar la zona del horno"},
                 {"t": "Sacar lo que hace falta reponer, para colocarlo después",
                  "sub": ["Expositores de snacks: Matutano, Tosfrit, paquetería variada",
                          "Cesto expositor de bolsitas de 1 €",
                          "Envasados de charcutería: queso, chorizo, jamón, salchichón, lomo, cecina, membrillo, panceta",
                          "Congelado: cubetas y tarrinas",
                          "Refrigerado: pizzas, postres de Urki, quesos loncheados, embutidos loncheados"]},
             ]},
        ],
        "hornadas": [
            {"n": 1, "ini": "7:00", "fin": "7:30", "que": "Pan + bollería grande",
             "detalle": ["3 panes de pan… y una bandeja de bollería grande"],
             "aclaraciones": ["Se mete el pan y una bandeja de bollería grande."]},
            {"n": 2, "ini": "7:30", "fin": "8:00", "que": "Pan", "detalle": [],
             "aclaraciones": ["Al meterla, se baja al almacén a preparar el monta."]},
            {"n": 3, "ini": "8:00", "fin": "8:30", "que": "Bollería pequeña, si hace falta", "detalle": [],
             "aclaraciones": ["Solo si se ha visto que hace falta."]},
            {"n": 4, "ini": "8:30", "fin": "9:00", "que": "Empanadillas, si hacen falta", "detalle": [],
             "aclaraciones": ["Las empanadillas tardan dos hornadas en hacerse."]},
            {"n": 5, "ini": "9:00", "fin": "9:30", "que": "Empanadillas, la segunda hornada suya",
             "detalle": [], "aclaraciones": ["Aquí acaban las empanadillas. Es la última hornada."]},
        ],
        "fin": "A las 9:00 empiezan las tareas del día (sábado, 10:00). Pero la última hornada sale a las 9:30.",
    },
    "B": {
        "nombre": "Domingos y festivos",
        "abre": "10:00",
        "nota": "La hace UNA sola persona: la coordinadora que entra a las 8:00. "
                "A las 9:00 entran la cocinera y la persona de tienda, y cada una va a lo suyo: "
                "la coordinadora de las 9:00 tiene el rol de cocinera, y la persona de tienda el suyo.",
        "bloques": [
            {"id": "B0", "titulo": "Al llegar", "ancla": "8:00", "ancla_alt": "8:00", "hora": "08:00",
             "pasos": [
                 {"t": "Quitar la alarma", "n": "La misma que de lunes a sábado"},
                 {"t": "Encender contadora, ordenadores, cajas, balanzas y horno"},
                 {"t": "Bajar al almacén y subir", "n": "1 caja Mediterránea + 1 caja Baguette"},
                 {"t": "Sacar la bollería de Malato", "cond": "si la hubiera",
                  "n": "No todos los domingos hay"},
             ]},
            {"id": "B1", "titulo": "Primera hornada", "ancla": "8:00 – 8:30",
             "ancla_alt": "8:00 – 8:30", "hora": "08:00",
             "horno": "3 bandejas de pan + 1 bandeja de bollería grande",
             "pasos": [
                 {"t": "Preparar la bollería para la apertura de las 10:00"},
                 {"t": "Quitar el pan del día anterior, si lo hubiera", "cond": True},
                 {"t": "Comprobar la devolución de pan"},
                 {"t": "Colocar el carro de la fruta"},
                 {"t": "Sacar la fruta y verdura para que la coloque la persona de tienda"},
                 {"t": "Preparar pollo, cerdo, ternera, salchichas, hamburguesas y empanado"},
                 {"t": "Hacer la lista del monta"},
             ]},
            {"id": "B2", "titulo": "Segunda hornada", "ancla": "8:30 – 9:00",
             "ancla_alt": "8:30 – 9:00", "hora": "08:30",
             "horno": "2 bandejas de pan + 6 tartas de manzana y 6 pasteles de arroz + mini pain (6×10)",
             "pasos": [
                 {"t": "Bajar al almacén a preparar el monta"},
                 {"t": "Subir el pan restante"},
                 {"t": "Subir panes especiales"},
                 {"t": "Frentear la cámara de yogures"},
                 {"t": "Sacar lo que hace falta reponer, para colocarlo antes de abrir",
                  "sub": ["Expositores de snacks: Matutano, Tosfrit, paquetería variada",
                          "Cesto expositor de bolsitas de 1 €",
                          "Envasados de charcutería: queso, chorizo, jamón, salchichón, lomo, cecina, membrillo, panceta",
                          "Congelado: cubetas y tarrinas",
                          "Refrigerado: pizzas, postres de Urki, quesos loncheados, embutidos loncheados"]},
             ]},
            {"id": "B3", "titulo": "Tercera hornada", "ancla": "9:00 – 9:30",
             "ancla_alt": "9:00 – 9:30", "hora": "09:00",
             "horno": "3 bandejas de pan + 28 mini croissants + 2 columnas de 10 filas de mini pain",
             "pasos": [
                 {"t": "Pintar toda la bollería hecha hasta el momento y meterla a la nevera"},
                 {"t": "Abrir las cajas de cobro"},
             ]},
            {"id": "B4", "titulo": "Cuarta hornada", "ancla": "9:30 – 10:00",
             "ancla_alt": "9:30 – 10:00", "hora": "09:30",
             "horno": "Pan según necesidades · toda la variedad de panes tiene que estar antes de abrir",
             "pasos": [
                 {"t": "Pintar la última bandeja de bollería y meterla a la cámara"},
                 {"t": "Sacar las bandejas de bollería de la cámara y montar la bollería grande y la pequeña, y las tartas y el pastel de arroz"},
                 {"t": "Sacar la última bandeja de bollería de la cámara y montarla"},
             ]},
            {"id": "B5", "titulo": "Antes de abrir", "ancla": "9:45", "ancla_alt": "9:45", "hora": "09:42",
             "pasos": [
                 {"t": "Actualizar el stock de la cocina y decidir lo que se mete en el asador",
                  "n": "9:45 · es una decisión, no una tarea"},
                 {"t": "Pintar la bollería de Malato", "cond": "si la hubiera",
                  "n": "La que sobró del día anterior, cuando hay"},
                 {"t": "Encender luces"},
                 {"t": "Encender tablets"},
                 {"t": "Encender música"},
             ]},
        ],
        "hornadas": [
            {"n": 1, "ini": "8:00", "fin": "8:30", "que": "3 bandejas de pan + bollería grande",
             "detalle": ["3 bandejas de pan", "1 bandeja de bollería grande"],
             "aclaraciones": [
                 "Durante esta hornada se prepara la bollería para la apertura de las 10:00.",
                 "Aquí se saca la fruta y verdura para que la coloque la persona de tienda."]},
            {"n": 2, "ini": "8:30", "fin": "9:00", "que": "2 panes + tartas y arroz + mini pain",
             "detalle": ["2 bandejas de pan",
                         "1 bandeja con 6 tartas de manzana + 6 pasteles de arroz",
                         "1 bandeja de mini pain, 6 columnas × 10 (= 60)"],
             "aclaraciones": ["Al meterla, se baja al almacén a preparar el monta.",
                              "Se suben los panes especiales y se frentea la cámara de yogures."]},
            {"n": 3, "ini": "9:00", "fin": "9:30", "que": "Pan + mini croissants + mini pain",
             "detalle": ["3 bandejas de pan",
                         "1 bandeja con 28 mini croissants",
                         "2 columnas de 10 filas de mini pain"],
             "aclaraciones": [
                 "Los mini croissants fermentan DESDE la primera hornada, con la bandeja encima del horno: fermentan 2 hornadas.",
                 "Se pinta toda la bollería hecha hasta ahora y se mete a la nevera.",
                 "Se abren las cajas de cobro."]},
            {"n": 4, "ini": "9:30", "fin": "10:00", "que": "Pan según necesidades",
             "detalle": ["A partir de aquí, pan según lo que pida la tienda",
                         "Antes de abrir tiene que estar horneada TODA la variedad de panes"],
             "aclaraciones": [
                 "Se pinta la última bandeja y se mete a la cámara.",
                 "Se montan las bandejas de bollería. Aquí van las fotos de cómo quedan montadas."]},
        ],
        "fin": "A las 10:00 abre la tienda. Y a las 9:45 se ha actualizado el stock de la cocina y decidido lo del asador.",
    },
}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Apertura · Supermercado Malato</title>
<style>
  :root{
    --verde:#2EC258; --verde-oscuro:#1E9A45; --verde-claro:#5CD47F;
    --verde-suave:#EFFAF2; --tinta:#13251A; --gris:#5E6E63; --borde:#D6EDDD;
    --azul:#1E6FA8; --ambar:#D97706;
  }
  *{box-sizing:border-box}
  body{margin:0; background:var(--verde-suave); color:var(--tinta);
       font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.5;
       -webkit-tap-highlight-color:transparent}
  header{background:linear-gradient(135deg,var(--verde) 0%,var(--verde-oscuro) 100%);
         color:#fff; padding:16px 20px; text-shadow:0 1px 2px rgba(0,0,0,.2)}
  .fila-sup{display:flex; align-items:center; gap:14px; flex-wrap:wrap}
  .logo{width:54px; height:54px; flex:0 0 auto; background:#fff; border-radius:13px;
        display:flex; align-items:center; justify-content:center; color:var(--verde-oscuro);
        font-weight:700; font-size:9px; text-align:center; padding:5px; border:2px dashed var(--verde-claro);
        text-shadow:none}
  header h1{margin:0; font-size:21px; letter-spacing:-.3px}
  header .sub{font-size:13px; opacity:.95; margin-top:1px}
  .prog{margin-top:13px}
  .prog .txt{display:flex; justify-content:space-between; font-size:12.5px; margin-bottom:5px; opacity:.95}
  .prog .barra{height:9px; background:rgba(255,255,255,.28); border-radius:5px; overflow:hidden}
  .prog .barra i{display:block; height:100%; background:#fff; width:0; transition:width .3s ease; border-radius:5px}
  main{max-width:780px; margin:0 auto; padding:16px 16px 70px}

  .patrones{display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap}
  .patron{border:2px solid var(--verde); background:#fff; color:var(--verde-oscuro);
          border-radius:10px; padding:9px 16px; font-size:13.5px; font-weight:700;
          cursor:pointer; font-family:inherit}
  .patron[aria-pressed=true]{background:var(--verde); color:#fff}
  .pnota{background:#E8F2FA; border:1px solid #C3DDF0; border-left:4px solid var(--azul);
         border-radius:11px; padding:11px 15px; font-size:13px; color:#14506F; margin-bottom:16px}
  .pnota b{color:#0E3D57}
  .patron small{display:block; font-weight:400; font-size:11px; opacity:.85}

  .hornadas{display:flex; gap:7px; overflow-x:auto; padding-bottom:8px; margin-bottom:18px}
  .hornada{flex:0 0 auto; background:#fff; border:1px solid var(--borde); border-radius:11px;
           padding:9px 13px; min-width:132px; cursor:pointer; font-family:inherit;
           text-align:left; position:relative; transition:border-color .15s, transform .1s}
  .hornada:hover{border-color:var(--verde); transform:translateY(-1px)}
  .hornada b{display:block; font-size:12.5px; color:var(--verde-oscuro)}
  .hornada .h{font-size:11.5px; color:var(--gris)}
  .hornada .q{display:block; font-size:10.5px; color:var(--gris); margin-top:2px; line-height:1.3}
  .hornada .info{position:absolute; top:7px; right:8px; font-size:10px; color:var(--verde); font-weight:700}
  .hornada .pista{margin-top:5px; font-size:10px; color:var(--verde-oscuro); font-weight:600}

  .bloque{background:#fff; border:1px solid var(--borde); border-radius:14px; margin-bottom:12px; overflow:hidden}
  .bloque.ahora{border-color:var(--verde); box-shadow:0 0 0 3px rgba(46,194,88,.18)}
  .cab{display:flex; align-items:flex-start; gap:12px; padding:13px 16px; border-bottom:1px solid #F2F7F3}
  .num{width:27px; height:27px; border-radius:50%; background:var(--verde-suave);
       color:var(--verde-oscuro); font-weight:700; font-size:13px; flex:0 0 auto;
       display:flex; align-items:center; justify-content:center; border:1.5px solid var(--borde)}
  .bloque.ahora .num{background:var(--verde); color:#fff; border-color:var(--verde)}
  .cab .tit{flex:1 1 auto}
  .cab .tit b{font-size:15px}
  .cab .tit span{display:block; font-size:12px; color:var(--gris); margin-top:1px}
  .horno{font-size:12px; color:var(--verde-oscuro); background:var(--verde-suave);
         border-radius:7px; padding:6px 10px; margin:0 16px 10px; display:block}
  .ancla{font-size:12px; font-weight:700; color:var(--verde-oscuro); background:var(--verde-suave);
         border-radius:7px; padding:3px 9px; white-space:nowrap}
  .ahora-tag{font-size:10.5px; font-weight:700; color:#fff; background:var(--verde);
             border-radius:6px; padding:2px 7px; margin-left:7px; vertical-align:middle}

  ul.pasos{margin:0; padding:0; list-style:none}
  ul.pasos li{display:flex; gap:11px; align-items:flex-start; padding:10px 16px;
              border-top:1px solid #F5F9F6; cursor:pointer}
  ul.pasos li:first-child{border-top:none}
  ul.pasos li:hover{background:#FAFDFB}
  .caja{width:20px; height:20px; flex:0 0 auto; border-radius:6px; border:2px solid var(--borde);
        margin-top:1px; display:flex; align-items:center; justify-content:center; font-size:12px; color:#fff}
  li.hecha .caja{background:var(--verde); border-color:var(--verde)}
  li.hecha .caja::after{content:"✓"}
  li.hecha .txt{color:var(--gris)}
  li.hecha .txt b{text-decoration:line-through}
  .txt{flex:1 1 auto; font-size:14px}
  .txt b{font-weight:500}
  .n{display:block; font-size:12px; color:var(--gris); margin-top:2px}
  .dia{font-size:10.5px; font-weight:700; color:var(--azul); background:#E8F2FA;
       border-radius:5px; padding:1px 7px; margin-left:6px; white-space:nowrap}
  .cond{font-size:10.5px; font-weight:700; color:var(--ambar); background:#FFF3E0;
        border-radius:5px; padding:1px 7px; margin-left:6px}
  ul.sub{margin:6px 0 0; padding-left:17px}
  ul.sub li{font-size:12.5px; color:var(--gris); padding:1px 0; border:0; cursor:default}

  .fin{background:#E8F2FA; border:1px solid #C3DDF0; border-left:4px solid var(--azul);
       border-radius:11px; padding:13px 16px; font-size:13.5px; color:#14506F; margin-top:18px}
  .fin b{color:#0E3D57}

  .velo{position:fixed; inset:0; background:rgba(10,30,18,.45); display:none;
        align-items:center; justify-content:center; padding:16px; z-index:50}
  .velo.abierto{display:flex}
  .ventana{background:#fff; border-radius:16px; max-width:560px; width:100%;
           max-height:88vh; overflow:auto; box-shadow:0 18px 50px rgba(0,0,0,.28)}
  .ventana .top{background:linear-gradient(135deg,var(--verde),var(--verde-oscuro));
                color:#fff; padding:16px 18px; display:flex; align-items:flex-start; gap:12px}
  .ventana .top h2{margin:0; font-size:18px}
  .ventana .top p{margin:2px 0 0; font-size:12.5px; opacity:.95}
  .cerrar{margin-left:auto; background:rgba(255,255,255,.22); border:1px solid rgba(255,255,255,.55);
          color:#fff; border-radius:9px; width:32px; height:32px; font-size:16px; cursor:pointer;
          font-family:inherit; line-height:1}
  .cuerpo-v{padding:16px 18px 20px}
  .cuerpo-v h4{margin:0 0 7px; font-size:13px; color:var(--verde-oscuro);
               text-transform:uppercase; letter-spacing:.4px}
  .cuerpo-v h4.mt{margin-top:16px}
  .cuerpo-v p.acl{font-size:13.5px; margin:0 0 8px; padding-left:13px; position:relative}
  .cuerpo-v p.acl::before{content:""; position:absolute; left:0; top:8px; width:5px; height:5px;
                          border-radius:50%; background:var(--verde)}
  .cuerpo-v ul.det{margin:0 0 10px; padding-left:18px}
  .cuerpo-v ul.det li{font-size:13.5px; margin-bottom:3px}
  .fotos{display:grid; grid-template-columns:1fr 1fr; gap:9px; margin-bottom:6px}
  .foto{aspect-ratio:4/3; border:2px dashed var(--borde); border-radius:11px;
        display:flex; align-items:center; justify-content:center; text-align:center;
        color:var(--gris); font-size:11.5px; background:var(--verde-suave); padding:8px; cursor:pointer}
  .foto:hover{border-color:var(--verde-claro); color:var(--verde-oscuro)}
  .quien{font-size:11.5px; color:var(--gris); margin-top:14px; padding-top:12px; border-top:1px solid var(--borde)}
  .add{margin-top:12px; border:0; background:var(--verde); color:#fff; border-radius:9px;
       padding:10px 16px; font-size:13.5px; font-weight:600; cursor:pointer; font-family:inherit}
  .add:hover{background:var(--verde-oscuro)}
  footer{max-width:780px; margin:0 auto; padding:0 16px 60px; color:var(--gris); font-size:12px}
</style>
</head>
<body>
<header>
  <div class="fila-sup">
    <div class="logo">AQUÍ<br>EL LOGO</div>
    <div><h1>Apertura</h1><div class="sub" id="sub"></div></div>
  </div>
  <div class="prog">
    <div class="txt"><span id="ptxt">0 de 0 pasos</span><span id="ppct">0 %</span></div>
    <div class="barra"><i id="pbar"></i></div>
  </div>
</header>

<main>
  <div class="patrones" id="patrones"></div>
  <div class="pnota" id="pnota"></div>
  <div class="hornadas" id="hornadas"></div>
  <div id="bloques"></div>
  <div class="fin" id="fin"></div>
</main>

<div class="velo" id="velo">
  <div class="ventana" role="dialog" aria-modal="true">
    <div class="top"><div><h2 id="vTit"></h2><p id="vSub"></p></div>
      <button class="cerrar" id="vCerrar" aria-label="Cerrar">✕</button></div>
    <div class="cuerpo-v" id="vCuerpo"></div>
  </div>
</div>

<footer>Los pasos se quedan a la vista al marcarlos: aquí no se busca «qué me falta», se busca «cómo se hace».</footer>

<script>
const P = __DATOS__;
const hoy = new Date();
const sabado = hoy.getDay() === 6;
const hechas = {};
let patron = sabado ? "A" : (hoy.getDay() === 0 ? "B" : "A");
function minutos(hhmm){ const [h,m]=hhmm.split(":").map(Number); return h*60+m+(sabado?60:0); }
const ahoraMin = hoy.getHours()*60 + hoy.getMinutes();

function pintaPatrones(){
  const c = document.getElementById("patrones"); c.innerHTML = "";
  Object.entries(P).forEach(([k, p])=>{
    const b = document.createElement("button");
    b.className = "patron"; b.type = "button";
    b.innerHTML = `${p.nombre}<small>abre a las ${p.abre}</small>`;
    b.setAttribute("aria-pressed", k === patron);
    b.addEventListener("click", ()=>{ patron = k; pintaPatrones(); pinta(); });
    c.appendChild(b);
  });
  document.getElementById("sub").textContent =
    P[patron].nombre + " · la hace coordinación o gerencia";
  const nt = document.getElementById("pnota");
  if(P[patron].nota){
    nt.innerHTML = "<b>" + P[patron].nombre + ".</b> " + P[patron].nota;
    nt.style.display = "block";
  } else {
    nt.style.display = "none";
  }
}

function abrir(h, p){
  document.getElementById("vTit").textContent = h.n + ".ª hornada";
  document.getElementById("vSub").textContent = h.ini + " – " + h.fin + (sabado ? " (+1 h)" : "");
  let html = "";
  if(h.detalle && h.detalle.length){
    html += "<h4>Qué se mete</h4><ul class='det'>" +
            h.detalle.map(d=>`<li>${d}</li>`).join("") + "</ul>";
  }
  if(h.aclaraciones && h.aclaraciones.length){
    html += "<h4 class='mt'>Aclaraciones</h4>" +
            h.aclaraciones.map(a=>`<p class='acl'>${a}</p>`).join("");
  }
  html += "<h4 class='mt'>Fotos</h4><div class='fotos'>" +
          "<div class='foto'>Aquí iría una foto<br>(pinchar para subir)</div>".repeat(2) + "</div>";
  html += `<button class="add" type="button">＋ Añadir aclaración o foto</button>`;
  html += `<div class="quien">Lo ven todas. Lo pueden cambiar <b>coordinación y gerencia</b>.</div>`;
  document.getElementById("vCuerpo").innerHTML = html;
  document.getElementById("velo").classList.add("abierto");
}
function cerrar(){ document.getElementById("velo").classList.remove("abierto"); }
document.getElementById("vCerrar").addEventListener("click", cerrar);
document.getElementById("velo").addEventListener("click", e=>{ if(e.target.id==="velo") cerrar(); });
document.addEventListener("keydown", e=>{ if(e.key==="Escape") cerrar(); });

function pinta(){
  const p = P[patron];

  const hc = document.getElementById("hornadas"); hc.innerHTML = "";
  p.hornadas.forEach(h=>{
    const b = document.createElement("button");
    b.className = "hornada"; b.type = "button";
    b.innerHTML = `<span class="info">＋</span><b>${h.n}.ª hornada</b>
      <span class="h">${h.ini} – ${h.fin}${sabado ? " (+1 h)" : ""}</span>
      <span class="q">${h.que}</span>
      <span class="pista">Ver fotos y aclaraciones</span>`;
    b.addEventListener("click", ()=>abrir(h, p));
    hc.appendChild(b);
  });

  const cont = document.getElementById("bloques"); cont.innerHTML = "";
  let total = 0, hechos = 0;
  p.bloques.forEach((b, i)=>{
    const ancla = sabado ? (b.ancla_alt || b.ancla) : b.ancla;
    const esAhora = ahoraMin >= minutos(b.hora) &&
                    (i === p.bloques.length - 1 || ahoraMin < minutos(p.bloques[i+1].hora));
    const caja = document.createElement("div");
    caja.className = "bloque" + (esAhora ? " ahora" : "");
    let filas = "";
    b.pasos.forEach((paso, j)=>{
      const k = b.id + "-" + j;
      total++; if (hechas[k]) hechos++;
      const dia = paso.dia ? `<span class="dia">${paso.dia}</span>` : "";
      const cond = paso.cond ? `<span class="cond">${typeof paso.cond === "string" ? paso.cond : "si hiciera falta"}</span>` : "";
      const n = paso.n ? `<span class="n">${paso.n}</span>` : "";
      const sub = paso.sub ? `<ul class="sub">${paso.sub.map(s=>`<li>${s}</li>`).join("")}</ul>` : "";
      filas += `<li class="${hechas[k]?"hecha":""}" data-k="${k}">
          <span class="caja"></span>
          <span class="txt"><b>${paso.t}</b>${dia}${cond}${n}${sub}</span></li>`;
    });
    const horno = b.horno ? `<span class="horno"><b>Al horno:</b> ${b.horno}</span>` : "";
    caja.innerHTML = `<div class="cab">
        <span class="num">${i}</span>
        <span class="tit"><b>${b.titulo}${esAhora?'<span class="ahora-tag">AHORA</span>':""}</b>
          <span>${b.pasos.length} ${b.pasos.length===1?"paso":"pasos"}</span></span>
        <span class="ancla">${ancla}</span>
      </div>${horno}<ul class="pasos">${filas}</ul>`;
    cont.appendChild(caja);
  });

  document.getElementById("ptxt").textContent = hechos + " de " + total + " pasos";
  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";
  document.getElementById("fin").innerHTML = "<b>" + p.fin + "</b>";

  cont.querySelectorAll("li[data-k]").forEach(li=>{
    li.addEventListener("click", ()=>{
      const k = li.dataset.k;
      hechas[k] = !hechas[k];
      pinta();
    });
  });
}
pintaPatrones(); pinta();
</script>
</body>
</html>
"""

html = HTML.replace("__DATOS__", json.dumps(PATRONES, ensure_ascii=False))
with open("docs/momentos/apertura.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"  escrito docs/momentos/apertura.html ({len(html):,} caracteres)")
