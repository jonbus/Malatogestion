"""Genera la pantalla de COORDINACIÓN: Apertura (2 patrones) · El día · Cierre."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================ APERTURA
AP_A = [
    {"sec": "BLOQUE 0 · Al llegar — 7:00 (sábado 8:00)", "tareas": [
        {"t": "Quitar la alarma"},
        {"t": "Encender contadora, ordenadores, cajas, balanzas y horno"},
        {"t": "Sacar el carro de la cámara de fruta"},
        {"t": "Sacar la bollería de Malato", "n": "La que sobró del día anterior"},
        {"t": "Preparar la primera hornada: pan y una bandeja de bollería grande"},
        {"t": "Quitar los ventiladores, si hiciera falta"},
    ]},
    {"sec": "BLOQUE 1 · Durante la primera hornada", "tareas": [
        {"t": "Sacar bandejas de bollería de la cámara y colocarlas en el lineal de la caja"},
        {"t": "Decidir si hace falta bollería pequeña y, si sí, apuntarla para la 3.ª hornada"},
        {"t": "Mirar si harán falta empanadillas", "n": "Si sí, 4.ª y 5.ª: tardan dos hornadas"},
        {"t": "Preparar las siguientes bandejas de pan"},
        {"t": "Quitar el pan del día anterior, si hubiera"},
        {"t": "Comprobar la devolución de pan"},
        {"t": "Colocar el carro de la fruta"},
        {"t": "Echar un vistazo rápido a la fruta", "n": "Por si faltara algo antes de abrir"},
        {"t": "Preparar pollo, cerdo, ternera, salchichas, hamburguesas y empanado"},
        {"t": "Guardar el pedido de fruta", "n": "Lunes y viernes"},
        {"t": "Hacer la lista del monta"},
        {"t": "Preparar las cajas de cobro para el día"},
        {"t": "Pintar bollería", "n": "La recién horneada"},
        {"t": "Frentear los yogures"},
        {"t": "Frentear el congelado"},
    ]},
    {"sec": "BLOQUE 2 · Segunda hornada", "tareas": [
        {"t": "Bajar al almacén a preparar el monta"},
    ]},
    {"sec": "BLOQUE 3 · Antes de abrir — 8:00 (sábado 9:00)", "tareas": [
        {"t": "Encender luces"},
        {"t": "Encender música"},
    ]},
    {"sec": "BLOQUE 4 · Una vez abierta la tienda", "tareas": [
        {"t": "Pintar la bollería de Malato"},
        {"t": "Limpiar y ordenar la zona del horno"},
        {"t": "Sacar lo que hace falta reponer, para colocarlo después", "partes": [
            "Expositores de snacks: Matutano, Tosfrit, paquetería variada",
            "Cesto expositor de bolsitas de 1 €",
            "Envasados de charcutería: queso, chorizo, jamón, salchichón, lomo, cecina, membrillo, panceta",
            "Congelado: cubetas y tarrinas",
            "Refrigerado: pizzas, postres de Urki, quesos loncheados, embutidos loncheados"]},
    ]},
]

AP_B = [
    {"sec": "BLOQUE 0 · Al llegar — 8:00", "tareas": [
        {"t": "Quitar la alarma", "n": "La misma que de lunes a sábado"},
        {"t": "Encender contadora, ordenadores, cajas, balanzas y horno"},
        {"t": "Bajar al almacén y subir", "n": "1 caja Mediterránea + 1 caja Baguette"},
        {"t": "Sacar la bollería de Malato", "n": "Si la hubiera: no todos los domingos hay"},
    ]},
    {"sec": "BLOQUE 1 · Primera hornada — 8:00 a 8:30", "tareas": [
        {"t": "Preparar la bollería para la apertura de las 10:00"},
        {"t": "Quitar el pan del día anterior, si lo hubiera"},
        {"t": "Comprobar la devolución de pan"},
        {"t": "Colocar el carro de la fruta"},
        {"t": "Sacar la fruta y verdura para que la coloque la persona de tienda"},
        {"t": "Preparar pollo, cerdo, ternera, salchichas, hamburguesas y empanado"},
        {"t": "Hacer la lista del monta"},
    ]},
    {"sec": "BLOQUE 2 · Segunda hornada — 8:30 a 9:00", "tareas": [
        {"t": "Bajar al almacén a preparar el monta"},
        {"t": "Subir el pan restante"},
        {"t": "Subir panes especiales"},
        {"t": "Frentear la cámara de yogures"},
        {"t": "Sacar lo que hace falta reponer, para colocarlo antes de abrir", "partes": [
            "Expositores de snacks: Matutano, Tosfrit, paquetería variada",
            "Cesto expositor de bolsitas de 1 €",
            "Envasados de charcutería",
            "Congelado: cubetas y tarrinas",
            "Refrigerado: pizzas, postres de Urki, quesos loncheados, embutidos loncheados"]},
    ]},
    {"sec": "BLOQUE 3 · Tercera hornada — 9:00 a 9:30", "tareas": [
        {"t": "Pintar toda la bollería hecha hasta el momento y meterla a la nevera"},
        {"t": "Abrir las cajas de cobro"},
    ]},
    {"sec": "BLOQUE 4 · Cuarta hornada — 9:30 a 10:00", "tareas": [
        {"t": "Pintar la última bandeja de bollería y meterla a la cámara"},
        {"t": "Sacar las bandejas de bollería y montar la grande y la pequeña, "
              "y las tartas y el pastel de arroz"},
        {"t": "Sacar la última bandeja de bollería de la cámara y montarla"},
    ]},
    {"sec": "BLOQUE 5 · Antes de abrir — 9:45", "tareas": [
        {"t": "Actualizar el stock de la cocina y decidir lo que se mete en el asador",
         "n": "9:45 · es una decisión, no una tarea"},
        {"t": "Pintar la bollería de Malato", "n": "Si la hubiera"},
        {"t": "Encender luces"},
        {"t": "Encender tablets"},
        {"t": "Encender música"},
    ]},
]

# ============================================================ EL DÍA
DIA_RUTINA = [
    {"t": "Preparar pedidos"},
    {"t": "Pasar pedidos"},
    {"t": "Mirar si hace falta utillaje y subirlo del almacén"},
    {"t": "Organizar el trabajo del día", "n": "Buscar tarea o clasificar alguna como urgente"},
    {"t": "Hacer pan según necesidades"},
    {"t": "Ordenar Lineal", "n": "Producto-Precio"},
    {"t": "Subir panes especiales"},
    {"t": "Hacer sitio para los pedidos que vayan a llegar hoy"},
    {"t": "Poner precios nuevos o actualizados en los productos"},
    {"t": "Ordenar trastienda"},
    {"t": "Fruta, verdura, carne y empanado: sacar y reponer a lo largo de la mañana"},
    {"t": "Arreglar productos que no estén en buen estado"},
]

DIA_POR_DIA = {
    "LUN": [{"t": "Bajar Cadagua"}],
    "MAR": [{"t": "Subir Cadagua"}],
    "MIE": [{"t": "Bajar Cadagua"}],
    "JUE": [{"t": "Subir Cadagua"},
            {"t": "Sacar pollos congelados"},
            {"t": "Sacar salsa de pollos congelada"},
            {"t": "Ordenar cámara de fruta"}],
    "VIE": [{"t": "Bajar Cadagua"},
            {"t": "Limpiar pollos", "n": "Mínimo 20 ud"},
            {"t": "Preparar bollería de Malato en bandejas de 1-2 €",
             "n": "Se sacan en el cierre, para dejarlas preparadas para la tarde"}],
    "SAB": [{"t": "Subir Cadagua"},
            {"t": "Preparar bollería de Malato en bandejas de 1-2 €"},
            {"t": "Reponer el utillaje de la tienda",
             "n": "Lo necesita la tienda para embandejar la bollería a granel por la tarde"},
            {"t": "Subir la bollería a granel del almacén",
             "n": "Llegó el viernes y se bajó al almacén · la tienda la necesita esta tarde"}],
    "DOM": [{"t": "Subir Cadagua"},
            {"t": "Ordenar cámara de fruta"}],
}

# ============================================================ CIERRE
CIERRE_COORD = [
    {"sec": "CIERRE DE COORDINACIÓN", "tareas": [
        {"t": "Cerrar Caja 3"},
        {"t": "Revisar que la carne esté bien repuesta"},
        {"t": "Revisar que la fruta esté bien repuesta"},
        {"t": "Revisar que la verdura esté bien repuesta"},
        {"t": "Guardar en la cámara frigorífica el pan que no se haya horneado",
         "n": "Para que no se estropee · se hornea mañana"},
    ]},
]

D = {
    "apertura": {"A": {"nombre": "Lunes a sábado", "abre": "8:00 · sábado 9:00", "bloques": AP_A},
                 "B": {"nombre": "Domingos y festivos", "abre": "10:00", "bloques": AP_B,
                       "nota": "La hace UNA sola persona: la coordinadora que entra a las 8:00. "
                               "A las 9:00 entran la cocinera y la persona de tienda, cada una a lo suyo."}},
    "dia": {"rutina": DIA_RUTINA, "porDia": DIA_POR_DIA},
    "cierre": CIERRE_COORD,
}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coordinación · Supermercado Malato</title>
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
         color:#fff; padding:15px 20px; text-shadow:0 1px 2px rgba(0,0,0,.2)}
  .fila-sup{display:flex; align-items:center; gap:14px; flex-wrap:wrap}
  .logo{width:52px; height:52px; flex:0 0 auto; background:#fff; border-radius:12px;
        display:flex; align-items:center; justify-content:center; color:var(--verde-oscuro);
        text-align:center;
        border:none; text-shadow:none; padding:2px}
  .logo img{max-width:100%; max-height:100%; object-fit:contain}
  header h1{margin:0; font-size:20px}
  header .sub{font-size:12.5px; opacity:.95; margin-top:1px}
  .prog{margin-top:12px}
  .prog .txt{display:flex; justify-content:space-between; font-size:12.5px; margin-bottom:5px; opacity:.95}
  .prog .barra{height:9px; background:rgba(255,255,255,.28); border-radius:5px; overflow:hidden}
  .prog .barra i{display:block; height:100%; background:#fff; width:0; transition:width .3s ease; border-radius:5px}
  main{max-width:760px; margin:0 auto; padding:14px 16px 70px}

  .tabs{display:flex; gap:8px; margin-bottom:14px}
  .tab{flex:1; border:2px solid var(--verde); background:#fff; color:var(--verde-oscuro);
       border-radius:11px; padding:10px; font-size:14.5px; font-weight:700; cursor:pointer;
       font-family:inherit}
  .tab[aria-pressed=true]{background:var(--verde); color:#fff}
  .subtab{display:flex; gap:7px; margin-bottom:14px; flex-wrap:wrap}
  .st{border:1px solid var(--borde); background:#fff; border-radius:9px; padding:7px 14px;
      font-size:13px; font-weight:600; cursor:pointer; font-family:inherit; color:var(--verde-oscuro)}
  .st[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}

  .dias{display:flex; gap:5px; overflow-x:auto; padding-bottom:6px; margin-bottom:14px}
  .dia-btn{flex:0 0 auto; border:1px solid var(--borde); background:#fff; border-radius:9px;
           padding:7px 11px; font-size:12.5px; font-weight:600; cursor:pointer;
           font-family:inherit; color:var(--verde-oscuro); min-width:48px; text-align:center}
  .dia-btn[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dia-btn.hoy{box-shadow:0 0 0 2px var(--verde-claro) inset}

  h2.bloque{font-size:15.5px; margin:20px 0 9px; padding-bottom:7px;
            border-bottom:2px solid var(--verde); color:var(--verde-oscuro);
            display:flex; justify-content:space-between; align-items:baseline; gap:10px}
  h2.bloque small{font-weight:400; font-size:11.5px; color:var(--gris)}
  .nota-patron{background:#E8F2FA; border:1px solid #C3DDF0; border-left:4px solid var(--azul);
               border-radius:11px; padding:11px 15px; font-size:13px; color:#14506F; margin-bottom:14px}
  .nota-patron b{color:#0E3D57}

  .lista{background:#fff; border:1px solid var(--borde); border-radius:12px; overflow:hidden}
  .item{border-top:1px solid #F2F7F3}
  .item:first-child{border-top:none}
  .cab-item{display:flex; gap:11px; align-items:flex-start; padding:11px 14px; cursor:pointer}
  .cab-item:hover{background:#FAFDFB}
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
  footer{max-width:760px; margin:0 auto; padding:0 16px 60px; color:var(--gris); font-size:12px}
</style>
</head>
<body>
<header>
  <div class="fila-sup">
    <div class="logo"><img src="__LOGO__" alt="Malato"></div>
    <div><h1>Coordinación</h1><div class="sub" id="sub"></div></div>
  </div>
  <div class="prog">
    <div class="txt"><span id="ptxt">0 de 0</span><span id="ppct">0 %</span></div>
    <div class="barra"><i id="pbar"></i></div>
  </div>
</header>

<main>
  <div class="tabs" id="tabs"></div>
  <div id="subopciones"></div>
  <div id="cuerpo"></div>
</main>

<footer>La apertura la hace coordinación, o gerencia cuando hace de coordinadora.</footer>

<script>
const D = __DATOS__;
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
const HOY = ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date().getDay()];
let tab = "apertura", patron = (HOY === "DOM") ? "B" : "A", dia = HOY;
const hechas = {}, REG = {};

function pintaTabs(){
  const c = document.getElementById("tabs"); c.innerHTML = "";
  [["apertura","Apertura"],["dia","El día"],["cierre","Cierre"]].forEach(([k,n])=>{
    const b = document.createElement("button");
    b.className = "tab"; b.type = "button"; b.textContent = n;
    b.setAttribute("aria-pressed", k === tab);
    b.addEventListener("click", ()=>{ tab = k; pintaTabs(); pinta(); });
    c.appendChild(b);
  });
  const s = document.getElementById("subopciones"); s.innerHTML = "";
  if(tab === "apertura"){
    const d = document.createElement("div"); d.className = "subtab";
    Object.entries(D.apertura).forEach(([k, v])=>{
      const b = document.createElement("button");
      b.className = "st"; b.type = "button";
      b.textContent = v.nombre + " · abre " + v.abre;
      b.setAttribute("aria-pressed", k === patron);
      b.addEventListener("click", ()=>{ patron = k; pintaTabs(); pinta(); });
      d.appendChild(b);
    });
    s.appendChild(d);
  }
  if(tab === "dia"){
    const d = document.createElement("div"); d.className = "dias";
    DIAS.forEach(([k,n])=>{
      const b = document.createElement("button");
      b.className = "dia-btn" + (k === HOY ? " hoy" : "");
      b.type = "button"; b.textContent = n.slice(0,3);
      b.setAttribute("aria-pressed", k === dia);
      b.addEventListener("click", ()=>{ dia = k; pintaTabs(); pinta(); });
      d.appendChild(b);
    });
    s.appendChild(d);
  }
}

function bloque(titulo, tareas, pre){
  if(!tareas || !tareas.length) return "";
  let html = `<h2 class="bloque">${titulo}<small>${tareas.length} ${
    tareas.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;
  tareas.forEach((t, i)=>{
    const k = pre + i; REG[k] = t;
    const partes = t.partes || [];
    const hp = partes.filter((_, j) => hechas[k+"."+j]).length;
    const completa = partes.length ? hp === partes.length : hechas[k];
    const parcial = partes.length && hp > 0 && hp < partes.length;
    let sub = "";
    if(partes.length){
      sub = `<div class="partes">` + partes.map((p, j)=>
        `<div class="parte ${hechas[k+"."+j]?"hecha":""}" data-pk="${k+"."+j}">
           <span class="pc"></span><span>${p}</span></div>`).join("") + `</div>`;
    }
    const tag = partes.length ? `<span class="tag">${hp} / ${partes.length} partes</span>` : "";
    const n = t.n ? `<span class="n">${t.n}</span>` : "";
    html += `<div class="item ${completa?"hecha":""} ${hechas["ab:"+k]?"abierta":""}" data-k="${k}">
        <div class="cab-item"><span class="caja ${parcial?"parcial":""}"></span>
        <span class="txt"><b>${t.t}</b>${tag}${n}</span></div>${sub}</div>`;
  });
  return html + "</div>";
}

function pinta(){
  let html = "", total = 0, hechos = 0;
  const sumar = (tareas, pre) => {
    (tareas||[]).forEach((t, i)=>{
      const k = pre + i, partes = t.partes || [];
      if(partes.length){ total += partes.length;
        partes.forEach((_, j)=>{ if(hechas[k+"."+j]) hechos++; });
      } else { total += 1; if(hechas[k]) hechos++; }
    });
  };

  if(tab === "apertura"){
    const P = D.apertura[patron];
    if(P.nota) html += `<div class="nota-patron"><b>${P.nombre}.</b> ${P.nota}</div>`;
    P.bloques.forEach((b, bi)=>{
      html += bloque(b.sec, b.tareas, patron + bi + "_");
      sumar(b.tareas, patron + bi + "_");
    });
    document.getElementById("sub").textContent = "Apertura · " + P.nombre;
  } else if(tab === "dia"){
    html += bloque("Rutina · todos los días", D.dia.rutina, "dr");
    sumar(D.dia.rutina, "dr");
    html += bloque("Lo de hoy · " + DIAS.find(x=>x[0]===dia)[1], D.dia.porDia[dia] || [], "dd");
    sumar(D.dia.porDia[dia], "dd");
    document.getElementById("sub").textContent = "El día · " + DIAS.find(x=>x[0]===dia)[1];
  } else {
    D.cierre.forEach((s, si)=>{
      html += bloque(s.sec, s.tareas, "c" + si + "_");
      sumar(s.tareas, "c" + si + "_");
    });
    document.getElementById("sub").textContent = "Cierre de coordinación";
  }

  document.getElementById("cuerpo").innerHTML = html;
  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ptxt").textContent = hechos + " de " + total;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";

  const c = document.getElementById("cuerpo");
  c.querySelectorAll(".item").forEach(it=>{
    const k = it.dataset.k;
    it.querySelector(".cab-item").addEventListener("click", e=>{
      if(e.target.closest(".partes")) return;
      const t = REG[k];
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
pintaTabs(); pinta();
</script>
</body>
</html>
"""

_LOGO_URI = "data:image/png;base64," + __import__("base64").b64encode(
    open("docs/marca/logo-o-blanco.png", "rb").read()).decode()
html = HTML.replace("__LOGO__", _LOGO_URI).replace("__DATOS__", json.dumps(D, ensure_ascii=False))
with open("docs/momentos/coordinacion.html", "w", encoding="utf-8") as f:
    f.write(html)
import os
if os.path.exists("docs/momentos/apertura.html"):
    os.remove("docs/momentos/apertura.html")
print(f"  escrito docs/momentos/coordinacion.html ({len(html):,} caracteres)")
print(f"  apertura A: {len(AP_A)} bloques · apertura B: {len(AP_B)} bloques")
print(f"  el dia: {len(DIA_RUTINA)} de rutina · cierre: 4 pasos")
