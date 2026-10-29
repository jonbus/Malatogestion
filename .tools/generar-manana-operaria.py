"""Genera la pantalla de La mañana de tienda."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

RUTINA = [
    {"t": "Fichar", "fuera": "esto desaparecería",
     "n": "Lo hace la aplicación al entrar: no se tica"},
    {"t": "Tarea diaria urgente", "n": "La pone coordinación o gerencia"},
    {"t": "Frentear y reponer, siempre ordenado por caducidades",
     "partes": ["Fruta", "Leche", "Yogures", "Congelado"]},
    {"t": "Subir monta"},
    {"t": "Apuntar el pan", "n": "Quizá pase a coordinadoras. Ver la ventana del pan"},
    {"t": "Tickar los pedidos que llegan y comprobar que todo pasa"},
    {"t": "Reponer bebidas frías", "n": "No pegar atrás"},
    {"t": "Tarea diaria complementaria", "n": "La pone coordinación o gerencia"},
    {"t": "Cocina: fregar y recoger todo", "n": "Dejar las fregaderas limpias"},
]

ANTES = [
    {"t": "Revisar la charcutería",
     "partes": ["Que no queden piezas sin tapar", "Que estén las puertas cerradas"]},
    {"t": "Apagar luces"},
    {"t": "Comprobar las puertas",
     "partes": ["Las de los congeladores, cerradas", "Las de los refrigeradores, cerradas"]},
    {"t": "Tirar basura", "n": "Si está llena"},
    {"t": "Tirar cartones"},
    {"t": "Tirar plásticos"},
]

POR_DIA = {
    "LUN": [
        {"t": "Pollos que han sobrado del fin de semana",
         "partes": ["Envasar con salsa los cocinados", "Congelar los frescos",
                    "Congelar la salsa"]},
        {"t": "Contar",
         "partes": ["Pollos", "Codillos", "Patatas normales", "Patatas bravas"]},
        {"t": "Limpiar la envasadora", "n": "Con un paño y agua · habrá documento de cómo funciona"},
        {"t": "Limpiar las fregonas", "n": "Dejar con lejía"},
        {"t": "Limpiar el baño"},
        {"t": "Limpiar y desinfectar la cámara de pollos",
         "partes": ["Suelo, puerta derecha", "Suelo, puerta izquierda", "Puertas",
                    "Baldas superiores derecha", "Baldas inferiores derecha",
                    "Baldas superiores izquierda"],
         "n": "Se marca qué partes · y con qué producto se ha limpiado"},
    ],
    "MAR": [
        {"t": "Limpiar y desinfectar el horno de pan"},
        {"t": "Limpiar y desinfectar la charcutería",
         "partes": ["Exposición", "Zona de almacenaje inferior",
                    "Todos los cristales", "Todas las puertas"]},
        {"t": "Limpiar y desinfectar la mesa de charcutería", "n": "Entera"},
    ],
    "MIE": [
        {"t": "Limpiar el suelo debajo del horno de pan"},
        {"t": "Limpiar la zona de bandejas de horno"},
        {"t": "Limpiar el congelado",
         "partes": ["Cubetas (dos mínimo, ir alternando)", "Tarrinas"],
         "n": "Desplegable para saber cuáles cubetas"},
    ],
    "JUE": [],
    "VIE": [],
    "SAB": [
        {"t": "Limpiar y desinfectar la charcutería",
         "partes": ["Exposición", "Zona de almacenaje inferior",
                    "Todos los cristales", "Todas las puertas"]},
        {"t": "Limpiar y desinfectar la mesa de charcutería", "n": "Entera"},
        {"t": "Revisar toda la fruta y verdura",
         "n": "Desplegable para que no se olvide nada · la lista la dirá la propiedad"},
    ],
    "DOM": [],
}

D = {"rutina": RUTINA, "antes": ANTES, "porDia": POR_DIA}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La mañana · Supermercado Malato</title>
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
         color:#fff; padding:16px 20px; text-shadow:0 1px 2px rgba(0,0,0,.2)}
  .fila-sup{display:flex; align-items:center; gap:14px; flex-wrap:wrap}
  .logo{width:54px; height:54px; flex:0 0 auto; background:#fff; border-radius:13px;
        display:flex; align-items:center; justify-content:center; color:var(--verde-oscuro);
        font-weight:700; font-size:9px; text-align:center; padding:5px;
        border:2px dashed var(--verde-claro); text-shadow:none}
  header h1{margin:0; font-size:21px; letter-spacing:-.3px}
  header .sub{font-size:13px; opacity:.95; margin-top:1px}
  .prog{margin-top:13px}
  .prog .txt{display:flex; justify-content:space-between; font-size:12.5px; margin-bottom:5px; opacity:.95}
  .prog .barra{height:9px; background:rgba(255,255,255,.28); border-radius:5px; overflow:hidden}
  .prog .barra i{display:block; height:100%; background:#fff; width:0; transition:width .3s ease;
                 border-radius:5px}
  main{max-width:760px; margin:0 auto; padding:16px 16px 70px}

  .dias{display:flex; gap:6px; overflow-x:auto; padding-bottom:6px; margin-bottom:16px}
  .dia-btn{flex:0 0 auto; border:1px solid var(--borde); background:#fff; border-radius:10px;
           padding:8px 13px; font-size:13px; font-weight:600; cursor:pointer;
           font-family:inherit; color:var(--verde-oscuro); min-width:54px; text-align:center}
  .dia-btn[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dia-btn.hoy{box-shadow:0 0 0 2px var(--verde-claro) inset}
  .dia-btn.vacio{opacity:.55}

  h2.bloque{font-size:16px; margin:24px 0 10px; padding-bottom:7px;
            border-bottom:2px solid var(--verde); color:var(--verde-oscuro);
            display:flex; justify-content:space-between; align-items:baseline; gap:10px}
  h2.bloque small{font-weight:400; font-size:12px; color:var(--gris)}
  h2.bloque.peligro{border-bottom-color:var(--ambar)}

  .lista{background:#fff; border:1px solid var(--borde); border-radius:13px; overflow:hidden}
  .item{border-top:1px solid #F2F7F3}
  .item:first-child{border-top:none}
  .cab-item{display:flex; gap:11px; align-items:flex-start; padding:12px 15px; cursor:pointer}
  .cab-item:hover{background:#FAFDFB}
  .item.hecha .cab-item{background:var(--verde-suave)}
  .caja{width:21px; height:21px; flex:0 0 auto; border-radius:6px; border:2px solid var(--borde);
        margin-top:1px; display:flex; align-items:center; justify-content:center;
        font-size:12px; color:#fff}
  .item.hecha .caja{background:var(--verde); border-color:var(--verde)}
  .item.hecha .caja::after{content:"✓"}
  .caja.parcial{background:var(--verde-claro); border-color:var(--verde-claro)}
  .caja.parcial::after{content:"–"}
  .txt{flex:1 1 auto; font-size:14.5px}
  .item.hecha .txt b{text-decoration:line-through; color:var(--gris)}
  .txt b{font-weight:500}
  .n{display:block; font-size:12px; color:var(--gris); margin-top:2px}
  .fuera{font-size:10.5px; font-weight:700; color:#fff; background:var(--gris);
         border-radius:5px; padding:1px 7px; margin-left:6px}
  .partes-tag{font-size:11px; font-weight:700; color:var(--azul); background:#E8F2FA;
              border-radius:5px; padding:1px 7px; margin-left:6px; white-space:nowrap}
  .partes{display:none; padding:0 15px 12px 47px}
  .item.abierta .partes{display:block}
  .parte{display:flex; gap:9px; align-items:flex-start; padding:6px 0; cursor:pointer;
         font-size:13.5px; color:var(--gris)}
  .parte .pc{width:17px; height:17px; flex:0 0 auto; border-radius:5px;
             border:1.5px solid var(--borde); margin-top:2px; display:flex;
             align-items:center; justify-content:center; font-size:10px; color:#fff}
  .parte.hecha .pc{background:var(--verde); border-color:var(--verde)}
  .parte.hecha .pc::after{content:"✓"}
  .parte.hecha{color:var(--tinta); text-decoration:line-through}
  .producto{margin-top:8px; display:flex; gap:8px; align-items:center; flex-wrap:wrap}
  .producto span{font-size:12px; color:var(--gris)}
  .producto select{font-family:inherit; font-size:12.5px; padding:5px 9px; border-radius:8px;
                   border:1px solid var(--borde); background:#fff; color:var(--tinta)}

  .aviso{background:#FFF8E6; border:1px solid #F0DCA6; border-left:4px solid var(--ambar);
         border-radius:11px; padding:13px 16px; font-size:13.5px; margin-top:20px}
  .aviso b{color:#8A4B00}
  .aviso ul{margin:7px 0 0; padding-left:19px}
  footer{max-width:760px; margin:0 auto; padding:0 16px 60px; color:var(--gris); font-size:12px}
</style>
</head>
<body>
<header>
  <div class="fila-sup">
    <div class="logo">AQUÍ<br>EL LOGO</div>
    <div><h1>La mañana</h1><div class="sub" id="sub"></div></div>
  </div>
  <div class="prog">
    <div class="txt"><span id="ptxt">0 de 0</span><span id="ppct">0 %</span></div>
    <div class="barra"><i id="pbar"></i></div>
  </div>
</header>

<main>
  <div class="dias" id="dias"></div>
  <div id="cuerpo"></div>

  <div class="aviso">
    <b>Pendiente de la propiedad</b>
    <ul>
      <li><b>Las tardes</b> y <b>el cierre de la noche</b>.</li>
      <li><b>Jueves, viernes y domingo</b>: no tienen tarea propia dictada. ¿No la tienen, o faltan?</li>
      <li><b>La lista del desplegable</b> de fruta y verdura.</li>
      <li><b>Cuáles son las cubetas</b> del congelado y cómo se alternan.</li>
      <li><b>El producto de limpieza</b>: ¿lista cerrada o texto libre?</li>
    </ul>
  </div>
</main>

<footer>El orden es el que dictó la propiedad. No he reordenado ni fusionado nada.</footer>

<script>
const D = __DATOS__;
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
const HOY = ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date().getDay()];
let dia = HOY;
const hechas = {};

function pintaDias(){
  const c = document.getElementById("dias"); c.innerHTML = "";
  DIAS.forEach(([k, nombre])=>{
    const vacio = !(D.porDia[k] && D.porDia[k].length);
    const b = document.createElement("button");
    b.className = "dia-btn" + (k === HOY ? " hoy" : "") + (vacio ? " vacio" : "");
    b.type = "button"; b.textContent = nombre.slice(0,3);
    b.setAttribute("aria-pressed", k === dia);
    b.addEventListener("click", ()=>{ dia = k; pintaDias(); pinta(); });
    c.appendChild(b);
  });
}

function bloque(titulo, tareas, prefijo, extra){
  if(!tareas || !tareas.length){
    return `<h2 class="bloque">${titulo}</h2>
      <div class="lista"><div class="item"><div class="cab-item" style="cursor:default">
        <span class="txt" style="color:var(--gris)">${extra || "Sin tareas."}</span>
      </div></div></div>`;
  }
  let html = `<h2 class="bloque">${titulo}<small>${tareas.length} ${
    tareas.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;
  tareas.forEach((t, i)=>{
    const k = prefijo + i;
    const partes = t.partes || [];
    const hechasPartes = partes.filter((_, j) => hechas[k + "." + j]).length;
    const abierta = hechas["abierta:" + k];
    const completa = partes.length ? (hechasPartes === partes.length) : hechas[k];
    const parcial = partes.length && hechasPartes > 0 && hechasPartes < partes.length;
    let cuerpoPartes = "";
    if(partes.length){
      cuerpoPartes = `<div class="partes">` + partes.map((p, j)=>{
        const hp = hechas[k + "." + j];
        return `<div class="parte ${hp?"hecha":""}" data-pk="${k + "." + j}">
            <span class="pc"></span><span>${p}</span></div>`;
      }).join("");
      if(t.n && /producto/i.test(t.n)){
        cuerpoPartes += `<div class="producto"><span>Con qué producto:</span>
          <select><option>— elige —</option><option>Lejía</option>
          <option>Desinfectante</option><option>Fregasuelos</option>
          <option>Otro (pendiente de lista)</option></select></div>`;
      }
      cuerpoPartes += `</div>`;
    }
    const marcaFuera = t.fuera ? `<span class="fuera">${t.fuera}</span>` : "";
    const cuenta = partes.length
      ? `<span class="partes-tag">${hechasPartes} / ${partes.length} partes</span>` : "";
    const n = t.n ? `<span class="n">${t.n}</span>` : "";
    html += `<div class="item ${completa?"hecha":""} ${abierta?"abierta":""}" data-k="${k}">
        <div class="cab-item">
          <span class="caja ${parcial?"parcial":""}"></span>
          <span class="txt"><b>${t.t}</b>${marcaFuera}${cuenta}${n}</span>
        </div>
        ${cuerpoPartes}
      </div>`;
  });
  return html + "</div>";
}

function pinta(){
  const c = document.getElementById("cuerpo");
  let total = 0, hechos = 0;
  const contar = (tareas, prefijo)=>{
    (tareas||[]).forEach((t, i)=>{
      const k = prefijo + i;
      const partes = t.partes || [];
      if(partes.length){
        total += partes.length;
        partes.forEach((_, j)=>{ if(hechas[k + "." + j]) hechos++; });
      } else {
        total += 1; if(hechas[k]) hechos++;
      }
    });
  };
  contar(D.rutina, "r"); contar(D.porDia[dia], "d"); contar(D.antes, "a");

  c.innerHTML =
    bloque("Lo de siempre · en este orden", D.rutina, "r") +
    bloque("Lo de hoy", D.porDia[dia], "d",
           "Este día no tiene tarea propia. O no la tiene, o falta por dictar.") +
    bloque("Antes de irse", D.antes, "a");

  const pct = total ? Math.round(100 * hechos / total) : 0;
  document.getElementById("ptxt").textContent = hechos + " de " + total;
  document.getElementById("ppct").textContent = pct + " %";
  document.getElementById("pbar").style.width = pct + "%";

  const nombreDia = DIAS.find(x => x[0] === dia)[1];
  document.getElementById("sub").textContent = "Tienda · " + nombreDia;

  c.querySelectorAll(".item").forEach(it=>{
    const k = it.dataset.k;
    const cab = it.querySelector(".cab-item");
    cab.addEventListener("click", e=>{
      if(e.target.closest(".partes")) return;
      const t = (k[0]==="r" ? D.rutina : k[0]==="d" ? D.porDia[dia] : D.antes)[+k.slice(1)];
      if(t && t.partes && t.partes.length){
        hechas["abierta:" + k] = !hechas["abierta:" + k];
      } else {
        hechas[k] = !hechas[k];
      }
      pinta();
    });
  });
  c.querySelectorAll(".parte").forEach(p=>{
    p.addEventListener("click", e=>{
      e.stopPropagation();
      const pk = p.dataset.pk;
      hechas[pk] = !hechas[pk];
      pinta();
    });
  });
}
pintaDias(); pinta();
</script>
</body>
</html>
"""

html = HTML.replace("__DATOS__", json.dumps(D, ensure_ascii=False))
with open("docs/momentos/manana-tienda.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"  escrito docs/momentos/manana-tienda.html ({len(html):,} caracteres)")
