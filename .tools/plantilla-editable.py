"""El ✎ en las tareas del día: cambiar el texto y la nota, y que se quede.

No mueve de puesto ni de turno: eso toca el guion y se hace aparte.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ 1 · el servidor
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()


def cambia_srv(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO (srv): {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


cambia_srv("encargosFecha: [], cascadas: {}, nombres: [], proveedores: [] };",
           "encargosFecha: [], cascadas: {}, nombres: [], proveedores: [], plantilla: {} };",
           "estadoVacio con la plantilla")

cambia_srv("      proveedores: Array.isArray(guardado.proveedores) ? guardado.proveedores : []",
           "      proveedores: Array.isArray(guardado.proveedores) ? guardado.proveedores : [],\n"
           "      plantilla: guardado.plantilla && typeof guardado.plantilla === 'object'\n"
           "        ? guardado.plantilla : {}",
           "leer devuelve la plantilla")

cambia_srv("    proveedores: estado.proveedores || [],",
           "    proveedores: estado.proveedores || [],\n"
           "    plantilla: estado.plantilla || {},",
           "podar conserva la plantilla")

cambia_srv("        proveedores: estado.proveedores",
           "        proveedores: estado.proveedores, plantilla: estado.plantilla",
           "el estado la devuelve")

cambia_srv("    /* -------- modificar una tarea extra ya creada */",
           """    /* -------- cambiar el texto o la nota de una tarea del guion */
    if (ruta.endsWith('/plantilla') && metodo === 'POST') {
      const c = cuerpo || {};
      const clave = String(c.clave || '')
        .toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
        .replace(/\\s+/g, ' ').trim().slice(0, 120);
      if (!clave) return { status: 400, body: { ok: false, error: 'falta la tarea' } };
      const estado = await leer();
      if (!estado.plantilla) estado.plantilla = {};
      const t2 = String(c.t || '').trim().slice(0, 300);
      const n2 = c.n === undefined ? undefined : String(c.n || '').trim().slice(0, 300);
      if (!t2) {
        delete estado.plantilla[clave];
      } else {
        const antes = estado.plantilla[clave] || {};
        estado.plantilla[clave] = {
          t: t2,
          n: n2 === undefined ? (antes.n || null) : (n2 || null),
          q: marca, h: hora
        };
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, plantilla: podado.plantilla } };
    }

    /* -------- modificar una tarea extra ya creada */""",
           "el endpoint de la plantilla")

open(p, "w", encoding="utf-8").write(t)

# ============================================================ 2 · la app
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


FUNCIONES = r'''/* ---------------------------------------- cambiar una tarea del GUION
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

'''

cambia("function pintaCalendario(){", FUNCIONES + "function pintaCalendario(){",
       "las funciones de la plantilla")

cambia("      cascadas = d.cascadas || {};",
       "      cascadas = d.cascadas || {};\n      plantilla = d.plantilla || {};\n      aplicarPlantilla();",
       "se aplican al arrancar")

# el ✎ en cada tarea del día
cambia("           lineaCascada(k, t.t) + `</div>`;",
       "           lineaCascada(k, t.t) +\n"
       "           `<div class=\"casc-linea\"><button class=\"btn-add-2\" type=\"button\" ` +\n"
       "           `onclick=\"abrirPlantilla('${k}')\">✎ cambiar</button></div>` + `</div>`;",
       "el ✎ en las tareas del día")

# el panel en las cinco pantallas
cambia("  let html = panelCascada() + panelEdicion(), total = 0, hechos = 0;",
       "  let html = panelPlantilla() + panelCascada() + panelEdicion(), total = 0, hechos = 0;",
       "el panel (tienda y coordinación)")
cambia("  let html = panelCascada() + panelEdicion() + avisoExtras();",
       "  let html = panelPlantilla() + panelCascada() + panelEdicion() + avisoExtras();",
       "el panel (la Jefa)")
cambia("  let html = panelCascada() + panelEdicion() +\n    bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();",
       "  let html = panelPlantilla() + panelCascada() + panelEdicion() +\n"
       "    bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();",
       "el panel (el menú)")
cambia("  c.innerHTML = panelCascada() + panelEdicion() + (avisoExtras() ||",
       "  c.innerHTML = panelPlantilla() + panelCascada() + panelEdicion() + (avisoExtras() ||",
       "el panel (tareas extra)")

cambia("v-2026-10-26-72", "v-2026-10-26-73", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
