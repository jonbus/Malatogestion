"""Poder MODIFICAR una tarea extra ya creada.

Antes solo se podía crear y borrar: si te equivocabas en el puesto o en el turno,
había que borrarla y volver a escribirla.
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


cambia_srv("    /* -------- la respuesta de una llamada (y cuándo se llamó) */",
           """    /* -------- modificar una tarea extra ya creada */
    if (ruta.endsWith('/encargo-editar') && metodo === 'POST') {
      const c = cuerpo || {};
      if (!c.id) return { status: 400, body: { ok: false, error: 'falta el id' } };
      const estado = await leer();
      const e = estado.encargos.find(x => String(x.id) === String(c.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      if (c.t !== undefined) {
        const txt = String(c.t || '').trim().slice(0, 300);
        if (txt) e.t = txt;
      }
      if (c.p !== undefined && ['tienda', 'coordinacion', 'gerencia'].includes(c.p)) e.p = c.p;
      if (c.turno !== undefined) e.turno = ['manana', 'tarde'].includes(c.turno) ? c.turno : null;
      if (c.tipo !== undefined) {
        e.tipo = ['extra', 'urgente', 'arreglar', 'llamada'].includes(c.tipo) ? c.tipo : 'extra';
      }
      if (c.f !== undefined && /^\\d{4}-\\d{2}-\\d{2}$/.test(String(c.f))) e.f = String(c.f);
      if (c.motivo !== undefined) e.motivo = String(c.motivo || '').slice(0, 200) || null;
      e.qEditado = marca; e.hEditado = hora;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargos: podado.encargos } };
    }

    /* -------- la respuesta de una llamada (y cuándo se llamó) */""",
           "el endpoint para modificar")

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


FUNCIONES = r'''/* ------------------------------------------------ modificar una tarea extra */
let editando = "";      /* el id de la tarea que se está modificando */

function abrirEdicion(id){
  editando = (editando === id) ? "" : id;
  pinta();
}

function panelEdicion(){
  if(!editando) return "";
  const e = (encargos || []).find(x => String(x.id) === String(editando));
  if(!e){ editando = ""; return ""; }
  const opc = (v, txt, act) => `<option value="${v}"${act === v ? " selected" : ""}>${txt}</option>`;
  return `<div class="casc-panel">
      <b class="casc-tit">Modificar la tarea</b>
      <div class="nueva-nota">
        <input type="text" id="ed-t" maxlength="300" value="${(e.t || "").replace(/"/g, "&quot;")}">
      </div>
      <div class="nueva-nota">
        <select id="ed-p">${opc("tienda", "Tienda", e.p)}${opc("coordinacion", "Coordinación", e.p)}${opc("gerencia", "Jefa", e.p)}</select>
        <select id="ed-turno">${opc("", "Sin turno", e.turno || "")}${opc("manana", "Mañana", e.turno)}${opc("tarde", "Tarde", e.turno)}</select>
        <select id="ed-tipo">${opc("extra", "Extra", e.tipo)}${opc("urgente", "Urgente", e.tipo)}${opc("arreglar", "Para arreglar", e.tipo)}</select>
        <input type="date" id="ed-f" value="${e.f || fechaSel}">
      </div>
      <div class="nueva-nota" style="border:none">
        <button class="btn-add" type="button" onclick="guardarEdicion('${e.id}')">Guardar los cambios</button>
        <button class="btn-add-2" type="button" onclick="abrirEdicion('${e.id}')">Cancelar</button>
      </div></div>`;
}

async function guardarEdicion(id){
  const c = {
    id: id, quien: quien.id,
    t: valorDe("ed-t", ""),
    p: valorDe("ed-p", ""),
    turno: valorDe("ed-turno", ""),
    tipo: valorDe("ed-tipo", ""),
    f: valorDe("ed-f", fechaSel)
  };
  ponerSync("trabajando", "Guardando los cambios…");
  try{
    const r = await fetch("/api/encargo-editar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(c)
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    encargos = d.encargos || encargos;
    editando = "";
    ponerSync("ok", "Tarea modificada");
  }catch(e){
    ponerSync("error", "No se pudo modificar");
  }
  pinta();
}

'''

cambia("function pintaCalendario(){", FUNCIONES + "function pintaCalendario(){",
       "las funciones de modificar")

# el botón de modificar, en cada tarea extra
cambia("""      lineaCascada("e_" + e.id, e.t) +""",
       """      `<div class="casc-linea"><button class="btn-add-2" type="button" ` +
      `onclick="abrirEdicion('${e.id}')">✎ modificar</button></div>` +
      lineaCascada("e_" + e.id, e.t) +""",
       "el botón de modificar en cada extra")

# el panel, arriba
cambia("  let html = panelCascada(), total = 0, hechos = 0;",
       "  let html = panelCascada() + panelEdicion(), total = 0, hechos = 0;",
       "el panel de edición (tienda y coordinación)")

cambia("  let html = panelCascada() + avisoExtras();",
       "  let html = panelCascada() + panelEdicion() + avisoExtras();",
       "el panel de edición (la Jefa)")

cambia("v-2026-10-26-66", "v-2026-10-26-67", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
