"""Las dos piezas: cascada en cualquier tarea, y la lista de las que hay."""
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


BLOQUE = r'''/* ------------------------------------------- cascada de CUALQUIER tarea
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
  const quien = (quien.puesto === "coordinacion" || quien.puesto === "gerencia");
  if(!quien) return "";
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

'''

cambia("function pintaCalendario(){", BLOQUE + "function pintaCalendario(){",
       "las funciones de la cascada de cualquier tarea")

# la lista se carga al arrancar
cambia("      proveedores = d.proveedores || [];",
       "      proveedores = d.proveedores || [];\n      cascadas = d.cascadas || {};",
       "las cascadas se cargan al arrancar")

# el panel, arriba de la pantalla del día
cambia("  let html = \"\", total = 0, hechos = 0;   /* las extra viven en el menú y en su sección */",
       "  let html = panelCascada(), total = 0, hechos = 0;   /* las extra viven en el menú y en su sección */",
       "el panel de la cascada, arriba")

# el cuarto botón del calendario
cambia("""    [["encargos", "Encargos", "📦"], ["llamadas", "Llamadas", "📞"], ["tareas", "Tareas", "✏️"]]""",
       """    [["encargos", "Encargos", "📦"], ["llamadas", "Llamadas", "📞"],
     ["tareas", "Tareas", "✏️"], ["cascadas", "Cascadas", "🔗"]]""",
       "el botón de cascadas")

cambia("""  if(calBloque === "llamadas") html += bloqueLlamada();
  if(calBloque === "encargos") html += bloqueFormEncargo();""",
       """  if(calBloque === "llamadas") html += bloqueLlamada();
  if(calBloque === "encargos") html += bloqueFormEncargo();
  if(calBloque === "cascadas") html += bloqueListaCascadas();""",
       "la lista en el calendario")

cambia("function pintaListaCascadas(){",
       """function bloqueListaCascadas(){
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

function pintaListaCascadas(){""",
       "la lista de cascadas, en su bloque")

# el estilo
cambia("  .menu-dibujo{font-size:22px; line-height:1; margin-bottom:5px}",
       """  .menu-dibujo{font-size:22px; line-height:1; margin-bottom:5px}
  .casc-panel{border:1.5px solid var(--ambar); background:#FFFBF2; border-radius:12px;
              padding:10px 12px; margin:10px 0}
  .casc-linea{display:flex; align-items:center; gap:6px; flex-wrap:wrap;
              margin:2px 0 0 27px; font-size:11.5px; color:var(--gris)}
  .casc-icono{color:var(--ambar); font-weight:800}
  .casc-linea .btn-add-2,.casc-linea .btn-borrar{font-size:10.5px; padding:2px 8px}""",
       "el estilo de la cascada en la tarea")

cambia("v-2026-10-26-61", "v-2026-10-26-62", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
