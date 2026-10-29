"""Genera la vista: pestanas de puesto, botones de dia, manana/tarde, barra de
progreso, pendientes y extras por zonas.

La prioridad por "repercusion" esta PENDIENTE: dentro de cada dia se respeta el
orden de las hojas de la propiedad y NO se inventa ninguna prioridad.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("docs/tareas-catalogo.json", encoding="utf-8") as f:
    cat = json.load(f)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tareas · Supermercado Malato</title>
<style>
  :root{
    --verde:#2EC258; --verde-oscuro:#1E9A45; --verde-claro:#5CD47F;
    --verde-suave:#EFFAF2; --tinta:#13251A; --gris:#5E6E63; --borde:#D6EDDD;
    --ambar:#D97706; --ambar-suave:#FFF8E6;
  }
  *{box-sizing:border-box}
  body{margin:0; background:var(--verde-suave); color:var(--tinta);
       font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.5}
  header{background:linear-gradient(135deg,var(--verde) 0%,var(--verde-oscuro) 100%);
         color:#fff; padding:20px 26px; display:flex; align-items:center; gap:20px;
         flex-wrap:wrap; text-shadow:0 1px 2px rgba(0,0,0,.22)}
  .logo{width:78px; height:78px; flex:0 0 auto; background:#fff; border-radius:16px;
        display:flex; align-items:center; justify-content:center; color:var(--verde-oscuro);
        font-weight:700; font-size:11px; text-align:center; padding:6px;
        border:2px dashed var(--verde-claro); text-shadow:none}
  header h1{margin:0; font-size:23px; letter-spacing:-.3px}
  header p{margin:4px 0 0; opacity:.95; font-size:14px}
  main{max-width:1100px; margin:0 auto; padding:20px 18px 40px}

  .pestanas{display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap}
  .pestana{border:2px solid var(--verde); background:#fff; color:var(--verde-oscuro);
           border-radius:11px; padding:10px 20px; font-size:14.5px; font-weight:700;
           cursor:pointer; font-family:inherit}
  .pestana[aria-pressed=true]{background:var(--verde); color:#fff}

  h2.bloque{font-size:19px; margin:30px 0 4px; padding-bottom:8px;
            border-bottom:3px solid var(--verde); display:flex;
            justify-content:space-between; align-items:baseline; gap:12px}
  h2.bloque small{font-weight:400; color:var(--gris); font-size:13px}
  .ayuda{color:var(--gris); font-size:13.5px; margin:8px 0 14px; max-width:800px}

  .dias{display:flex; gap:7px; flex-wrap:wrap; margin-bottom:18px}
  .dia-btn{border:1px solid var(--borde); background:#fff; border-radius:9px;
           padding:9px 16px; font-size:14px; font-weight:600; cursor:pointer;
           font-family:inherit; color:var(--verde-oscuro)}
  .dia-btn:hover{background:var(--verde-suave); border-color:var(--verde-claro)}
  .dia-btn[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dia-btn.hoy::after{content:" · hoy"; font-weight:400; font-size:11.5px; opacity:.85}

  .turno{background:#fff; border:1px solid var(--borde); border-radius:12px;
         margin-bottom:14px; overflow:hidden}
  .turno > h3{margin:0; padding:11px 16px; font-size:15px; background:var(--verde-suave);
              border-bottom:1px solid var(--borde); color:var(--verde-oscuro);
              display:flex; justify-content:space-between; align-items:baseline}
  .turno > h3 span{font-weight:400; color:var(--gris); font-size:12.5px}

  .barra{height:9px; background:#E4F1E8; overflow:hidden}
  .barra i{display:block; height:100%; background:linear-gradient(90deg,var(--verde-claro),var(--verde));
           width:0; transition:width .25s ease}
  .barra-txt{font-size:12px; color:var(--gris); padding:7px 16px 0}

  ul.tareas{margin:0; padding:0; list-style:none}
  ul.tareas li{display:flex; gap:11px; align-items:flex-start; padding:9px 16px;
               border-top:1px solid #F2F7F3; cursor:pointer}
  ul.tareas li:hover{background:#FAFDFB}
  ul.tareas li input{margin:3px 0 0; width:17px; height:17px; accent-color:var(--verde);
                     flex:0 0 auto; cursor:pointer}
  ul.tareas li .txt{flex:1 1 auto; font-size:14px}
  ul.tareas li.hecha .txt{text-decoration:line-through; color:var(--gris)}
  .obs{display:block; font-size:12px; color:var(--verde-oscuro); margin-top:2px}
  .fuera{font-size:10.5px; font-weight:700; color:#8A4B00; background:#FFF3E0;
         border-radius:5px; padding:1px 6px; margin-left:6px}
  .arrastra{font-size:10.5px; font-weight:700; color:#1E6FA8; background:#E8F2FA;
            border-radius:5px; padding:1px 6px; margin-left:6px}

  .pend{background:#fff; border:1px solid var(--borde); border-left:4px solid var(--ambar);
        border-radius:10px; padding:14px 18px}
  .pend p{margin:0; font-size:13.5px; color:var(--gris)}
  .pend b{color:var(--tinta)}

  .zonas{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px}
  .zona{border:1px solid var(--borde); background:#fff; border-radius:999px;
        padding:7px 15px; font-size:13.5px; cursor:pointer; font-family:inherit;
        color:var(--verde-oscuro); font-weight:600}
  .zona:hover{border-color:var(--verde-claro); background:var(--verde-suave)}
  .zona[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .extra{background:#fff; border:1px solid var(--borde); border-radius:11px;
         padding:11px 16px; margin-bottom:8px; display:flex; gap:11px; align-items:flex-start}
  .extra input{margin:4px 0 0; width:17px; height:17px; accent-color:var(--verde); flex:0 0 auto}
  .extra b{font-size:14px}
  .extra span{display:block; font-size:12.5px; color:var(--gris); margin-top:2px}

  .aviso{background:var(--ambar-suave); border:1px solid #F0DCA6; border-left:4px solid var(--ambar);
         border-radius:10px; padding:13px 17px; font-size:13.5px; margin-top:26px}
  .aviso h4{margin:0 0 5px; color:#8A4B00; font-size:14.5px}
  .aviso ul{margin:7px 0 0; padding-left:19px}
  footer{max-width:1100px; margin:0 auto; padding:12px 18px 60px; color:var(--gris); font-size:12.5px}
</style>
</head>
<body>
<header>
  <div class="logo">AQUÍ<br>EL LOGO</div>
  <div>
    <h1>Tareas</h1>
    <p>La base de cada día · más las extras cuando la tienda lo pide</p>
  </div>
</header>

<main>
  <div class="pestanas" id="pestanas"></div>

  <h2 class="bloque">La base semanal <small>la vuestra · cada tarea en su día y su turno</small></h2>
  <p class="ayuda">Elige el día. Dentro van la <b>mañana</b> y la <b>tarde</b> por separado,
     porque no se hace lo mismo. El orden es el de vuestras hojas.</p>
  <div class="dias" id="dias"></div>
  <div id="diaContenido"></div>

  <h2 class="bloque">Pendientes <small>lo que se arrastra y lo que hay que hacer algún día</small></h2>
  <div class="pend">
    <p>Aquí va lo que <b>no dio tiempo a terminar</b>, lo que <b>se arrastra al día siguiente</b>, y
       esas cosas <b>sin importancia pero que hay que hacer en algún momento</b>.</p>
    <p style="margin-top:8px">De momento está vacío: se llenará cuando la aplicación se use.</p>
  </div>

  <h2 class="bloque">Las extras <small>sin día fijo · cuando se necesitan</small></h2>
  <p class="ayuda" id="bancoExplica"></p>
  <div class="zonas" id="zonas"></div>
  <div id="bancoLista"></div>

  <div class="aviso">
    <h4>Pendiente, y lo decide la propiedad</h4>
    <ul>
      <li><b>Los niveles de repercusión</b> (la prioridad). No se decide por asiduidad, sino por
          <b>repercusión en el establecimiento</b>. La aplicación <b>no la inventa</b>: por eso aquí no
          hay ninguna prioridad puesta.</li>
      <li><b>Las tareas de la gerencia</b>, que están por llegar.</li>
      <li><b>La cocina</b> (26 tareas) sin clasificar, y <b>los solapes</b> entre puestos.</li>
      <li><b>El logo</b>, y confirmar el verde.</li>
    </ul>
  </div>
</main>

<footer>Las 94 tareas salen íntegras de vuestras plantillas, más las que ha añadido la propiedad.</footer>

<script>
const CATALOGO = __DATOS__;
const BANCO = CATALOGO.banco || {zonas:[], tareas:[], explicacion:""};
const REGLAS = CATALOGO.reglas || {};
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
const HOY = ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date().getDay()];

let puesto = "tienda";
let dia = HOY;
let zonaSel = null;
const hechas = {};          // clave "puesto|dia|id" -> true

function datosPuesto(){ return CATALOGO.puestos.find(p => p.clave === puesto); }
function clave(id){ return puesto + "|" + dia + "|" + id; }

function pintaPestanas(){
  const c = document.getElementById("pestanas");
  c.innerHTML = "";
  CATALOGO.puestos.forEach(p=>{
    const b = document.createElement("button");
    b.className = "pestana"; b.type = "button";
    b.textContent = p.etiqueta + " (" + p.tareas.length + ")";
    b.setAttribute("aria-pressed", p.clave === puesto);
    b.addEventListener("click", ()=>{ puesto = p.clave; pintaPestanas(); pintaDias(); pintaDia(); });
    c.appendChild(b);
  });
}

function pintaDias(){
  const c = document.getElementById("dias");
  c.innerHTML = "";
  DIAS.forEach(([k, nombre])=>{
    const b = document.createElement("button");
    b.className = "dia-btn" + (k === HOY ? " hoy" : "");
    b.type = "button"; b.textContent = nombre;
    b.setAttribute("aria-pressed", k === dia);
    b.addEventListener("click", ()=>{ dia = k; pintaDias(); pintaDia(); });
    c.appendChild(b);
  });
}

function bloqueTurno(titulo, items, porId){
  const total = items.length;
  if(!total) return "";
  const hechasAqui = items.filter(x => hechas[clave(x.id)]).length;
  const pct = Math.round(100 * hechasAqui / total);
  let filas = "";
  items.forEach(x=>{
    const t = porId[x.id]; if(!t) return;
    const h = hechas[clave(x.id)];
    const fuera = t.en_plantilla === false
      ? '<span class="fuera">FUERA DE PLANTILLA</span>' : "";
    const obs = t.nota ? `<span class="obs">${t.nota}</span>` : "";
    filas += `<li class="${h?"hecha":""}" data-id="${x.id}">
        <input type="checkbox" ${h?"checked":""}>
        <span class="txt">${t.nombre}${fuera}${obs}</span></li>`;
  });
  return `<div class="turno">
      <h3>${titulo}<span>${hechasAqui} de ${total} · ${pct} %</span></h3>
      <div class="barra"><i style="width:${pct}%"></i></div>
      <ul class="tareas">${filas}</ul>
    </div>`;
}

function pintaDia(){
  const p = datosPuesto();
  const porId = {};
  p.tareas.forEach(t => { porId[t.id] = t; });
  const items = (p.semana && p.semana[dia]) || [];
  const manana = items.filter(x => x.t === "M");
  const tarde  = items.filter(x => x.t === "T");
  const sinTurno = items.filter(x => !x.t);

  let html = "";
  if(manana.length || tarde.length){
    html += bloqueTurno("Mañana", manana, porId);
    html += bloqueTurno("Tarde", tarde, porId);
  }
  if(sinTurno.length){
    html += bloqueTurno(manana.length || tarde.length ? "Sin turno asignado" : "Tareas del día",
                        sinTurno, porId);
  }
  if(!html){
    const hechasAqui = 0;
    html = `<div class="turno"><h3>Sin tareas<span>0 de 0</span></h3>
            <p style="padding:14px 16px; color:var(--gris); margin:0">
            Este día no tiene tareas en la plantilla.</p></div>`;
  }
  const cont = document.getElementById("diaContenido");
  cont.innerHTML = html;
  cont.querySelectorAll("ul.tareas li").forEach(li=>{
    li.addEventListener("click", e=>{
      if(e.target.tagName !== "INPUT") return;
      const id = li.dataset.id;
      hechas[clave(id)] = e.target.checked;
      pintaDia();
    });
  });
}

function pintaZonas(){
  document.getElementById("bancoExplica").textContent = BANCO.explicacion || "";
  const c = document.getElementById("zonas");
  c.innerHTML = "";
  BANCO.zonas.forEach(z=>{
    const b = document.createElement("button");
    b.className = "zona"; b.type = "button"; b.textContent = z;
    b.setAttribute("aria-pressed", zonaSel === z);
    b.addEventListener("click", ()=>{ zonaSel = (zonaSel === z) ? null : z; pintaZonas(); });
    c.appendChild(b);
  });
  pintaExtras();
}

function pintaExtras(){
  const c = document.getElementById("bancoLista");
  c.innerHTML = "";
  const lista = BANCO.tareas.filter(t =>
    !zonaSel || t.zonas.includes("*") || t.zonas.includes(zonaSel));
  if(!lista.length){
    c.innerHTML = '<p style="color:var(--gris)">No hay extras para esa zona todavía.</p>';
    return;
  }
  lista.forEach(t=>{
    const donde = t.zonas.includes("*") ? "vale para cualquier zona" : t.zonas.join(", ");
    const d = document.createElement("div");
    d.className = "extra";
    d.innerHTML = `<input type="checkbox"><div><b>${t.nombre}</b>
      <span>${donde}${t.nota ? " · " + t.nota : ""}</span></div>`;
    d.querySelector("input").addEventListener("change", e=>{
      d.style.opacity = e.target.checked ? ".55" : "1";
    });
    c.appendChild(d);
  });
}

pintaPestanas(); pintaDias(); pintaDia(); pintaZonas();
</script>
</body>
</html>
"""

html = HTML.replace("__DATOS__", json.dumps(cat, ensure_ascii=False))
with open("docs/vista-tareas.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"  escrito docs/vista-tareas.html ({len(html):,} caracteres)")
