"""Genera la pantalla "Mi día".

Modelo pedido por la propiedad:
  - El GRUPO es la ACCION (reponer y frentear), con una descripcion de en que consiste.
  - Dentro se despliegan las ZONAS de la tienda, porque en todas se hace lo mismo.
  - Se tica LA ZONA que se ha hecho.
  - Y lo marcado es DEL DIA, no de cada una: quien llega despues ve que zonas quedan
    y continua el trabajo en vez de repetirlo.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("docs/tareas-catalogo.json", encoding="utf-8") as f:
    cat = json.load(f)

# --- BORRADOR: las acciones del dia y las zonas donde se hacen -------------------
ACCIONES = [
    {"nombre": "Reponer y frentear",
     "descripcion": "Que no falte producto y que se vea bien: adelantar lo de delante, "
                    "rellenar los huecos y colocar lo nuevo detrás.",
     "zonas": ["Lineales", "Yogures", "Fruta", "Verdura", "Congelado", "Bebidas",
               "Charcutería", "Pan y bollería", "Txutxes y paquetería"]},
    {"nombre": "Revisar el frío y las cámaras",
     "descripcion": "Comprobar que esté todo cerrado y encendido, y que no falte ni sobre nada.",
     "zonas": ["Cámara fruta", "Cámara pollos", "Congeladores", "Cámaras frigoríficas"]},
    {"nombre": "Revisar fechas y estado",
     "descripcion": "Mirar lo que caduca antes, apartar lo que esté tocado y sacarlo de oferta.",
     "zonas": ["Leche y yogures", "Fruta y verdura", "Charcutería", "Pan y bollería",
               "Congelado", "Txutxes y paquetería"]},
    {"nombre": "Limpiar",
     "descripcion": "Dejar la zona limpia: superficies, cristales, rincones y suelo.",
     "zonas": ["Cocina", "Suelos", "Muebles y baldas", "Cámara fruta", "Cámara pollos",
               "Baño", "Puertas y cristales"]},
    {"nombre": "Ordenar",
     "descripcion": "Que cada cosa esté en su sitio y que el precio de la balda sea el que cobra la caja.",
     "zonas": ["Lineal", "Trastienda", "Cámara fruta", "Cestos", "Almacén"]},
    {"nombre": "Etiquetas y precios",
     "descripcion": "Poner lo que falta, quitar lo que sobra y comprobar que coincide con la caja.",
     "zonas": ["Lineales", "Ofertas", "Etiqueteros", "Cartelería"]},
]

DATOS = {
    "puestos": cat["puestos"],
    "banco": cat.get("banco", {}),
    "acciones": ACCIONES,
    "personas": {
        "tienda": ["Tienda 1", "Tienda 2", "Tienda 3"],
        "coordinadora": ["Coordinadora 1", "Coordinadora 2"],
    },
}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi día · Supermercado Malato</title>
<style>
  :root{
    --verde:#2EC258; --verde-oscuro:#1E9A45; --verde-claro:#5CD47F;
    --verde-suave:#EFFAF2; --tinta:#13251A; --gris:#5E6E63; --borde:#D6EDDD;
    --ambar:#D97706; --rojo:#C62828; --azul:#1E6FA8;
  }
  *{box-sizing:border-box}
  body{margin:0; background:var(--verde-suave); color:var(--tinta);
       font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; line-height:1.5;
       -webkit-tap-highlight-color:transparent}
  .pantalla{min-height:100vh; display:none}
  .pantalla.activa{display:block}

  .entrada{max-width:560px; margin:0 auto; padding:34px 20px 60px}
  .marca{display:flex; align-items:center; gap:16px; margin-bottom:34px}
  .logo{width:70px; height:70px; flex:0 0 auto; background:#fff; border-radius:16px;
        display:flex; align-items:center; justify-content:center; color:var(--verde-oscuro);
        font-weight:700; font-size:10.5px; text-align:center; padding:6px;
        border:2px dashed var(--verde-claro)}
  .marca h1{margin:0; font-size:25px; letter-spacing:-.4px}
  .marca p{margin:2px 0 0; color:var(--gris); font-size:14px}
  .pregunta{font-size:17px; font-weight:600; margin:0 0 14px}
  .grandes{display:grid; grid-template-columns:1fr 1fr; gap:13px; margin-bottom:26px}
  .gente{border:2px solid var(--verde); background:#fff; border-radius:16px;
         padding:26px 14px; font-size:17px; font-weight:700; color:var(--verde-oscuro);
         cursor:pointer; font-family:inherit}
  .gente:hover,.gente[aria-pressed=true]{background:var(--verde); color:#fff}
  .nombres{display:grid; grid-template-columns:1fr 1fr; gap:11px}
  .nombre{border:1px solid var(--borde); background:#fff; border-radius:13px; padding:17px;
          font-size:16px; font-weight:600; cursor:pointer; font-family:inherit; color:var(--tinta)}
  .nombre:hover{border-color:var(--verde); background:var(--verde-suave)}
  .nota{color:var(--gris); font-size:13px; margin-top:18px}

  .barra-sup{background:linear-gradient(135deg,var(--verde),var(--verde-oscuro)); color:#fff;
             padding:14px 18px; display:flex; align-items:center; gap:14px; flex-wrap:wrap;
             text-shadow:0 1px 2px rgba(0,0,0,.2)}
  .barra-sup .quien{font-weight:700; font-size:15px}
  .barra-sup .cuando{font-size:13px; opacity:.95}
  .barra-sup .salir{margin-left:auto; background:rgba(255,255,255,.2);
                    border:1px solid rgba(255,255,255,.5); color:#fff; border-radius:9px;
                    padding:8px 15px; font-size:13.5px; cursor:pointer; font-family:inherit;
                    font-weight:600}
  main{max-width:820px; margin:0 auto; padding:18px 16px 70px}

  .dias{display:flex; gap:6px; overflow-x:auto; padding-bottom:6px; margin-bottom:14px}
  .dia-btn{flex:0 0 auto; border:1px solid var(--borde); background:#fff; border-radius:11px;
           padding:9px 14px; font-size:13.5px; font-weight:600; cursor:pointer;
           font-family:inherit; color:var(--verde-oscuro); min-width:58px; text-align:center}
  .dia-btn b{display:block; font-size:16px}
  .dia-btn[aria-pressed=true]{background:var(--verde); border-color:var(--verde); color:#fff}
  .dia-btn.hoy{box-shadow:0 0 0 2px var(--verde-claro) inset}

  .prog{background:#fff; border:1px solid var(--borde); border-radius:13px; padding:13px 16px;
        margin-bottom:14px}
  .prog .txt{display:flex; justify-content:space-between; font-size:13.5px; margin-bottom:7px}
  .prog .txt b{color:var(--verde-oscuro)}
  .barra{height:11px; background:#E4F1E8; border-radius:6px; overflow:hidden}
  .barra i{display:block; height:100%; background:linear-gradient(90deg,var(--verde-claro),var(--verde));
           width:0; transition:width .3s ease}

  .equipo{background:#E8F2FA; border:1px solid #C3DDF0; border-left:4px solid var(--azul);
          border-radius:11px; padding:11px 15px; font-size:13px; margin-bottom:18px; color:#14506F}
  .equipo b{color:#0E3D57}

  h3.tipo{font-size:15px; margin:22px 0 10px; color:var(--verde-oscuro);
          display:flex; align-items:center; gap:9px}
  .punto{width:10px; height:10px; border-radius:50%; flex:0 0 auto}
  .c-urgente{background:var(--rojo)} .c-diaria{background:var(--gris)} .c-comun{background:var(--verde)}

  .accion{background:#fff; border:1px solid var(--borde); border-radius:13px; margin-bottom:10px;
          overflow:hidden}
  .accion > button.cabeza{width:100%; text-align:left; background:#fff; border:0; cursor:pointer;
        padding:14px 16px; font-family:inherit; display:flex; align-items:flex-start; gap:12px}
  .accion > button.cabeza:hover{background:var(--verde-suave)}
  .cabeza .tit{flex:1 1 auto}
  .cabeza .nom{font-size:15.5px; font-weight:700; color:var(--tinta)}
  .cabeza .desc{display:block; font-size:12.5px; font-weight:400; color:var(--gris); margin-top:3px}
  .cabeza .cuenta{font-size:12.5px; color:var(--gris); background:var(--verde-suave);
                  border-radius:999px; padding:3px 11px; white-space:nowrap; margin-top:2px}
  .cabeza .cuenta.completa{background:var(--verde); color:#fff; font-weight:700}
  .cabeza .flecha{transition:transform .2s; color:var(--gris); font-size:12px; margin-top:4px}
  .accion.abierta .cabeza .flecha{transform:rotate(90deg)}
  .items{display:none; padding:2px 14px 14px; flex-wrap:wrap; gap:8px}
  .accion.abierta .items{display:flex}

  .zona{border:1.5px solid var(--borde); background:#fff; border-radius:999px;
        padding:9px 16px; font-size:13.5px; cursor:pointer; font-family:inherit;
        color:var(--tinta); display:inline-flex; align-items:center; gap:7px}
  .zona:hover{border-color:var(--verde-claro); background:var(--verde-suave)}
  .zona.hecha{background:var(--verde); border-color:var(--verde); color:#fff;
              text-decoration:line-through; opacity:.8}
  .zona.hecha::before{content:"✓"; font-weight:700; text-decoration:none}
  .resumen{width:100%; font-size:12.5px; color:var(--gris); margin-top:4px}
  .resumen b{color:var(--azul)}

  .suelta{background:#fff; border:1px solid var(--borde); border-radius:13px; overflow:hidden}
  .fila{display:flex; gap:12px; align-items:flex-start; padding:13px 16px;
        border-top:1px solid #F2F7F3; cursor:pointer}
  .fila:first-child{border-top:none}
  .fila:hover{background:#FAFDFB}
  .fila.hecha{background:var(--verde-suave)}
  .fila.hecha .t{text-decoration:line-through; color:var(--gris)}
  .check{width:22px; height:22px; flex:0 0 auto; border-radius:7px; border:2px solid var(--borde);
         display:flex; align-items:center; justify-content:center; font-size:13px; color:#fff;
         margin-top:1px}
  .fila.hecha .check{background:var(--verde); border-color:var(--verde)}
  .fila.hecha .check::after{content:"✓"}
  .t{flex:1 1 auto; font-size:14.5px}
  .sub{display:block; font-size:12px; color:var(--gris); margin-top:2px}
  .paso{font-size:11px; font-weight:700; color:var(--azul); background:#E8F2FA;
        border-radius:6px; padding:2px 7px; margin-left:6px; white-space:nowrap}
  .urg{font-size:11px; font-weight:700; color:#fff; background:var(--rojo);
       border-radius:6px; padding:2px 8px; margin-left:6px}

  .cal{display:grid; grid-template-columns:1fr 1fr; gap:13px; margin-top:10px}
  @media(max-width:640px){.cal{grid-template-columns:1fr}.grandes{grid-template-columns:1fr}}
  .cal > div{background:#fff; border:1px solid var(--borde); border-radius:13px; padding:14px 16px}
  .cal h4{margin:0 0 4px; font-size:14.5px; color:var(--verde-oscuro)}
  .cal p{margin:0 0 10px; font-size:12.5px; color:var(--gris)}
  .cal textarea{width:100%; border:1px solid var(--borde); border-radius:9px; padding:10px;
                font-family:inherit; font-size:13.5px; resize:vertical; min-height:76px}
  .quien-lo-ve{font-size:11.5px; color:var(--gris); margin-top:7px; display:block}
  .aviso{background:#FFF8E6; border:1px solid #F0DCA6; border-left:4px solid var(--ambar);
         border-radius:11px; padding:13px 17px; font-size:13.5px; margin-top:26px}
  .aviso h4{margin:0 0 5px; color:#8A4B00; font-size:14.5px}
  .aviso ul{margin:7px 0 0; padding-left:19px}
</style>
</head>
<body>

<section class="pantalla activa" id="p1">
  <div class="entrada">
    <div class="marca">
      <div class="logo">AQUÍ<br>EL LOGO</div>
      <div><h1>Mi día</h1><p>Supermercado Malato</p></div>
    </div>
    <p class="pregunta">¿Quién eres?</p>
    <div class="grandes" id="puestos"></div>
    <div id="zonaNombres"></div>
    <p class="nota">Al elegir tu nombre, <b>queda fichada la entrada</b> de tu jornada.</p>
  </div>
</section>

<section class="pantalla" id="p2">
  <div class="barra-sup">
    <span class="quien" id="quien"></span>
    <span class="cuando" id="cuando"></span>
    <button class="salir" id="salir">Salir</button>
  </div>
  <main>
    <div class="dias" id="dias"></div>
    <div class="prog">
      <div class="txt"><span id="progTxt">0 de 0 hechas</span><b id="progPct">0 %</b></div>
      <div class="barra"><i id="progBar"></i></div>
    </div>
    <div class="equipo" id="equipo"></div>
    <div id="cuerpo"></div>

    <h3 class="tipo"><span class="punto c-comun"></span>Mis apuntes y el calendario</h3>
    <div class="cal">
      <div>
        <h4>Mi calendario</h4>
        <p>Para apuntar lo que tengo que hacer o quiero hacer otro día.</p>
        <textarea placeholder="Escribe aquí tus apuntes…"></textarea>
        <span class="quien-lo-ve">Lo ves tú. <b>Gerencia también puede verlo y cambiarlo.</b></span>
      </div>
      <div>
        <h4>Calendario general</h4>
        <p>Para apuntar lo que haga falta entre todas.</p>
        <textarea placeholder="Escribe aquí lo que sea, para todas…"></textarea>
        <span class="quien-lo-ve">Lo escribe y lo ve <b>todo el mundo</b>.</span>
      </div>
    </div>

    <div class="aviso">
      <h4>Borrador, pendiente de que lo corrijas</h4>
      <ul id="avisos"></ul>
    </div>
  </main>
</section>

<script>
const D = __DATOS__;
const DIAS = [["LUN","Lunes"],["MAR","Martes"],["MIE","Miércoles"],["JUE","Jueves"],
              ["VIE","Viernes"],["SAB","Sábado"],["DOM","Domingo"]];
const HOY = ["DOM","LUN","MAR","MIE","JUE","VIE","SAB"][new Date().getDay()];

let puesto = null, persona = null, dia = HOY;
const hechas = {};
let abiertas = {};

function tareasDe(p, d){
  const items = (p.semana && p.semana[d]) || [];
  const porId = {}; p.tareas.forEach(t => { porId[t.id] = t; });
  return items.map(x => Object.assign({}, porId[x.id], {turno:x.t})).filter(t => t.nombre);
}
/* OJO: la clave NO lleva el nombre de la persona. Lo marcado es DEL DIA, para que
   quien llegue despues vea que zonas quedan y continue en vez de repetir. */
function clave(k){ return puesto + "|" + dia + "|" + k; }

function pintaPuestos(){
  const c = document.getElementById("puestos"); c.innerHTML = "";
  D.puestos.forEach(p=>{
    const b = document.createElement("button");
    b.className = "gente"; b.type = "button"; b.textContent = p.etiqueta;
    b.setAttribute("aria-pressed", puesto === p.clave);
    b.addEventListener("click", ()=>{ puesto = p.clave; pintaPuestos(); pintaNombres(); });
    c.appendChild(b);
  });
}
function pintaNombres(){
  const c = document.getElementById("zonaNombres"); c.innerHTML = "";
  if(!puesto) return;
  const t = document.createElement("p");
  t.className = "pregunta"; t.textContent = "¿Cuál eres?";
  c.appendChild(t);
  const g = document.createElement("div"); g.className = "nombres";
  (D.personas[puesto] || []).forEach(n=>{
    const b = document.createElement("button");
    b.className = "nombre"; b.type = "button"; b.textContent = n;
    b.addEventListener("click", ()=>{ persona = n; entrar(); });
    g.appendChild(b);
  });
  c.appendChild(g);
}

function entrar(){
  document.getElementById("p1").classList.remove("activa");
  document.getElementById("p2").classList.add("activa");
  document.getElementById("quien").textContent = persona;
  document.getElementById("cuando").textContent =
    "Entrada fichada · " + new Date().toLocaleTimeString("es-ES",{hour:"2-digit",minute:"2-digit"});
  dia = HOY; for(const k in hechas) delete hechas[k]; abiertas = {};
  pintaDias(); pintaDia();
}
function salir(){
  document.getElementById("p2").classList.remove("activa");
  document.getElementById("p1").classList.add("activa");
  persona = null; pintaNombres();
}

function pintaDias(){
  const c = document.getElementById("dias"); c.innerHTML = "";
  DIAS.forEach(([k, nombre], i)=>{
    const b = document.createElement("button");
    b.className = "dia-btn" + (k === HOY ? " hoy" : "");
    b.type = "button"; b.innerHTML = `${nombre.slice(0,3)}<b>${i+1}</b>`;
    b.setAttribute("aria-pressed", k === dia);
    b.addEventListener("click", ()=>{ dia = k; pintaDias(); pintaDia(); });
    c.appendChild(b);
  });
}

function pintaDia(){
  const p = D.puestos.find(x => x.clave === puesto);
  const todas = tareasDe(p, dia);
  const cuerpo = document.getElementById("cuerpo");
  cuerpo.innerHTML = "";

  let nHechas = 0, nTotal = 0;

  /* ---------- la urgente la pone coordinacion y baja a las personas de tienda ---------- */
  if(puesto === "tienda"){
    const k = "urg-hoy", h = hechas[clave(k)];
    nTotal++; if(h) nHechas++;
    cuerpo.insertAdjacentHTML("beforeend",
      `<h3 class="tipo"><span class="punto c-urgente"></span>Urgente de hoy</h3>
       <div class="suelta"><div class="fila ${h?"hecha":""}" data-k="${k}">
         <div class="check"></div>
         <div class="t">Tarea urgente de hoy<span class="urg">URGENTE</span>
           <span class="sub">La pone coordinación o gerencia. Aparece aquí sola.</span>
         </div></div></div>`);
  }

  /* ---------- las acciones del dia: el grupo es la accion, dentro van las zonas ---------- */
  cuerpo.insertAdjacentHTML("beforeend",
    `<h3 class="tipo"><span class="punto c-diaria"></span>Las del día, por zonas
      <span style="font-weight:400;font-size:12.5px;color:var(--gris)">
      (pulsa una acción para abrir sus zonas)</span></h3><div id="acciones"></div>`);

  const cont = document.getElementById("acciones");
  let html = "", pendientesGlobal = [];
  D.acciones.forEach(a=>{
    const zonasHechas = a.zonas.filter(z => hechas[clave("acc|" + a.nombre + "|" + z)]);
    const quedan = a.zonas.filter(z => !hechas[clave("acc|" + a.nombre + "|" + z)]);
    nTotal += a.zonas.length; nHechas += zonasHechas.length;
    quedan.forEach(z => pendientesGlobal.push(a.nombre + ": " + z));
    const completa = quedan.length === 0;
    const pills = a.zonas.map(z=>{
      const k = "acc|" + a.nombre + "|" + z;
      const h = hechas[clave(k)];
      return `<button class="zona ${h?"hecha":""}" data-k="${k}">${z}</button>`;
    }).join("");
    const resumen = completa
      ? `<div class="resumen"><b>Completa.</b> No queda ninguna zona.</div>`
      : `<div class="resumen">Quedan <b>${quedan.length}</b>: ${quedan.join(" · ")}</div>`;
    html += `<div class="accion ${abiertas[a.nombre]?"abierta":""}" data-acc="${a.nombre}">
        <button class="cabeza" type="button">
          <span class="tit"><span class="nom">${a.nombre}</span>
            <span class="desc">${a.descripcion}</span></span>
          <span class="cuenta ${completa?"completa":""}">${zonasHechas.length} / ${a.zonas.length}</span>
          <span class="flecha">▶</span>
        </button>
        <div class="items">${pills}${resumen}</div>
      </div>`;
  });
  cont.innerHTML = html;

  /* ---------- lo demas de la base de ese dia ---------- */
  const resto = todas.filter(t => !/Frentear y Reponer|Reponer y colocar|Reponer leche|Reponer bebidas|Reponer y colocar chuches|Reponer y colocar paquetería|Apuntar Pan|Tirar cartones/.test(t.nombre));
  if(resto.length){
    const hh = resto.filter(t => hechas[clave(t.id)]).length;
    nTotal += resto.length; nHechas += hh;
    cuerpo.insertAdjacentHTML("beforeend",
      `<h3 class="tipo"><span class="punto c-comun"></span>Lo demás de este día
        <span style="font-weight:400;font-size:12.5px;color:var(--gris)">(${hh} de ${resto.length})</span></h3>
       <div class="suelta">${resto.map(t=>{
         const h = hechas[clave(t.id)];
         const paso = /[Tt]ickar/.test(t.nombre) ? '<span class="paso">luego: comprobar que pase</span>' : "";
         const obs = t.nota ? `<span class="sub">${t.nota}</span>` : "";
         return `<div class="fila ${h?"hecha":""}" data-k="${t.id}">
            <div class="check"></div><div class="t">${t.nombre}${paso}${obs}</div></div>`;
       }).join("")}</div>`);
  }

  const pct = nTotal ? Math.round(100 * nHechas / nTotal) : 0;
  document.getElementById("progTxt").textContent = nHechas + " de " + nTotal + " hechas";
  document.getElementById("progPct").textContent = pct + " %";
  document.getElementById("progBar").style.width = pct + "%";

  const eq = document.getElementById("equipo");
  if(pendientesGlobal.length){
    eq.innerHTML = `<b>Quedan ${pendientesGlobal.length} zonas sin hacer hoy.</b>
      Lo que marque cualquiera lo ven las demás: así se continúa el trabajo donde lo dejó
      la anterior, en vez de repetirlo.`;
    eq.style.display = "block";
  }else{
    eq.innerHTML = "<b>Está todo hecho.</b> No queda ninguna zona por hacer.";
    eq.style.display = "block";
  }

  cuerpo.querySelectorAll(".accion > .cabeza").forEach(b=>{
    b.addEventListener("click", ()=>{
      const a = b.parentElement, n = a.dataset.acc;
      abiertas[n] = !abiertas[n];
      a.classList.toggle("abierta");
    });
  });
  cuerpo.querySelectorAll(".zona, .fila").forEach(b=>{
    b.addEventListener("click", ()=>{
      const k = b.dataset.k;
      hechas[clave(k)] = !hechas[clave(k)];
      pintaDia();
    });
  });
}

document.getElementById("salir").addEventListener("click", salir);
pintaPuestos(); pintaNombres();

document.getElementById("avisos").innerHTML = [
  "El <b>reparto de zonas en cada acción</b> es un borrador mío: dime qué zonas hay y cuáles van en cada una.",
  "La <b>descripción de cada acción</b> la he escrito yo a partir de las tareas de tus hojas. Corrígela.",
  "La <b>«Tarea urgente de hoy»</b>: falta la pantalla donde la crea la coordinadora.",
  "El <b>logo</b>, y el <b>nombre</b> (ahora pone «Mi día», es solo una idea).",
].map(a => "<li>" + a + "</li>").join("");
</script>
</body>
</html>
"""

html = HTML.replace("__DATOS__", json.dumps(DATOS, ensure_ascii=False))
with open("docs/mi-dia.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"  escrito docs/mi-dia.html ({len(html):,} caracteres)")
