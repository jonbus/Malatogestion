"""El menú de botones: al entrar en un grupo, botones en vez de pestañas.

Los avisos (pedir hoy, para arreglar, tareas extra) viven EN EL MENÚ, siempre a la
vista (D-284). Cada sección tiene su vuelta atrás.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


MENU = r'''/* ---------------------------------------------------------- EL MENÚ
   Al entrar en un grupo se ven botones, no la lista de tareas.
   De izquierda a derecha y de arriba abajo, como pidió la propiedad (D-284). */
const MENU_POR_PUESTO = {
  tienda: [
    ["calendario", "Calendario"],
    ["panes", "Registro de panes"],
    ["extra", "Tareas extra"],
    ["manana", "Mañana"],
    ["tarde", "Tarde"],
    ["cierre", "Cierre"]
  ],
  coordinacion: [
    ["calendario", "Calendario"],
    ["panes", "Registro de panes"],
    ["extra", "Tareas extra"],
    ["apertura", "Apertura"],
    ["dia", "El día"],
    ["cierre", "Cierre"]
  ]
};

/* cuántas tareas extra quedan sin hacer para este puesto */
function extrasPendientes(){
  return (encargos || []).filter(e => !e.hecho && (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto)).length;
}

function abrirSeccion(k){
  tab = k;
  pinta();
}

function pintaMenu(){
  const c = document.getElementById("cuerpo");
  /* los avisos, siempre arriba (D-284) */
  let html = bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();
  const lista = MENU_POR_PUESTO[quien.puesto] || [];
  html += `<div class="menu-grupo">`;
  lista.forEach(([k, n])=>{
    const cuantas = k === "extra" ? extrasPendientes() : 0;
    html += `<button class="menu-btn${cuantas ? " con-pendientes" : ""}" ` +
      `type="button" onclick="abrirSeccion('${k}')">` +
      `<b>${n}</b>` +
      (cuantas ? `<span class="menu-num">${cuantas}</span>` : "") +
      `</button>`;
  });
  html += `</div>`;
  c.innerHTML = html;
  const s = document.getElementById("sub");
  if(s) s.textContent = quiénCorta();
}

function quiénCorta(){
  return NOMBRE_PUESTO[quien.puesto] + " · " + bonito(fechaSel);
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
  c.innerHTML = avisoExtras() ||
    `<div class="lista"><p class="pista" style="padding:14px">` +
    `No hay tareas extra para hoy.</p></div>`;
  const s = document.getElementById("sub");
  if(s) s.textContent = "Tareas extra · " + bonito(fechaSel);
}

'''

cambia("function pinta(){", MENU + "function pinta(){", "las funciones del menú")

# pinta(): el menú y las dos secciones nuevas
cambia("""function pinta(){
  /* la pestaña «General» es de tienda y coordinación; la Jefa tiene la suya */
  if(tab === "general" && quien.puesto !== "gerencia"){ pintaTurnos(); return; }""",
       """function pinta(){
  /* tienda y coordinación: primero el menú de botones (D-284) */
  if(quien.puesto !== "gerencia"){
    if(!tab || tab === "menu"){ pintaMenu(); return; }
    if(tab === "panes"){ pintaPanes(); return; }
    if(tab === "extra"){ pintaExtra(); return; }
  }
  /* la pestaña «General» es de tienda y coordinación; la Jefa tiene la suya */
  if(tab === "general" && quien.puesto !== "gerencia"){ pintaTurnos(); return; }""",
       "pinta(): menú, panes y extra")

# las pestañas: solo la vuelta al menú (la Jefa sigue con las suyas)
cambia("""  const lista = quien.puesto === "tienda"
    ? [["general","Turno"],["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : quien.puesto === "coordinacion"
    ? [["general","Turno"],["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : [["general","El día"],["turno","Turno"],["calendario","Calendario"]];
  if(!tab) tab = lista[0][0];""",
       """  if(quien.puesto !== "gerencia"){
    /* sin barra de pestañas: un solo botón para volver al menú */
    tab = tab || "menu";
    if(tab === "menu") return;
    const b = document.createElement("button");
    b.className = "tab";
    b.type = "button";
    b.textContent = "◀ Menú";
    b.addEventListener("click", ()=>{ tab = "menu"; pinta(); });
    c.appendChild(b);
    return;
  }
  const lista = [["general","El día"],["turno","Turno"],["calendario","Calendario"]];
  if(!tab) tab = lista[0][0];""",
       "la vuelta al menú")

# el pan sale de la apertura y del cierre (ahora vive en «Registro de panes»)
cambia("      html += bloqueTahona(\"entrada\");            /* el pan que llega */\n", "",
       "el pan sale de la apertura")
cambia("      html += bloqueTahona(\"devolucion\");        /* el pan que se devuelve */\n", "",
       "el pan sale del cierre de tienda")

# las extra ya no van arriba de cada pantalla: van en el menú y en su sección
cambia("  let html = avisoExtras(), total = 0, hechos = 0;   /* las extra, en su bloque aparte */",
       "  let html = \"\", total = 0, hechos = 0;   /* las extra viven en el menú y en su sección */",
       "las extra fuera del día")

# y el estilo de los botones
cambia("  .sug-caja{display:none;",
       """  /* EL MENÚ DEL GRUPO */
  .menu-grupo{display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin:14px 0}
  .menu-btn{position:relative; display:flex; flex-direction:column; align-items:center;
            justify-content:center; min-height:82px; padding:12px 8px; border-radius:14px;
            border:1.5px solid var(--borde); background:#fff; cursor:pointer;
            font-family:inherit; color:var(--tinta)}
  .menu-btn b{font-size:13.5px; font-weight:700; line-height:1.25; text-align:center}
  .menu-btn:active{background:#F4F1EA}
  .menu-btn.con-pendientes{border-color:#C084FC; background:#FBF5FF}
  .menu-num{position:absolute; top:8px; right:9px; min-width:20px; height:20px;
            border-radius:10px; background:#8B5CF6; color:#fff; font-size:11px;
            font-weight:800; display:flex; align-items:center; justify-content:center;
            padding:0 5px}
  @media (min-width: 620px){ .menu-grupo{grid-template-columns:repeat(3, 220px)} }
  .sug-caja{display:none;""",
       "el estilo del menú")

cambia("v-2026-10-26-40", "v-2026-10-26-41", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
