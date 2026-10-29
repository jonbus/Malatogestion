"""La respuesta de la llamada: sale al llamar, y queda registrada."""
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


cambia_srv("    /* -------- mover una tarea extra a otro día",
           """    /* -------- la respuesta de una llamada (y cuándo se llamó) */
    if (ruta.endsWith('/encargo-respuesta') && metodo === 'POST') {
      const c = cuerpo || {};
      if (!c.id) return { status: 400, body: { ok: false, error: 'falta el id' } };
      const estado = await leer();
      const e = estado.encargos.find(x => String(x.id) === String(c.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      if (c.llamado === true && !e.llamadoEn) { e.llamadoEn = hora; }
      if (c.respuesta !== undefined) {
        e.respuesta = String(c.respuesta || '').slice(0, 500) || null;
        e.qRespuesta = marca; e.hRespuesta = hora;
      }
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, encargos: podado.encargos } };
    }

    /* -------- mover una tarea extra a otro día""",
           "el endpoint de la respuesta")

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


FUNCIONES = r'''/* la respuesta de la llamada: sale al llamar y se queda registrada */
function idDeEncargo(id){
  const caja = document.getElementById("resp-" + id);
  return caja ? caja.value : "";
}

async function marcarLlamada(id){
  try{
    await fetch("/api/encargo-respuesta", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, llamado: true, quien: quien.id })
    });
    const d = await fetch("/api/estado").then(x => x.json());
    encargos = d.encargos || encargos;
  }catch(e){ /* si falla, la llamada se hace igual */ }
  pinta();
}

async function guardarRespuesta(id){
  const txt = String(idDeEncargo(id) || "").trim();
  ponerSync("trabajando", "Guardando la respuesta…");
  try{
    const r = await fetch("/api/encargo-respuesta", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, respuesta: txt, quien: quien.id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    encargos = d.encargos || encargos;
    ponerSync("ok", txt ? "Respuesta guardada" : "Respuesta borrada");
  }catch(e){
    ponerSync("error", "No se pudo guardar la respuesta");
  }
  pinta();
}

'''

cambia("function horaAhora(){", FUNCIONES + "function horaAhora(){",
       "las funciones de la respuesta")

# el bloque de la llamada: el enlace avisa y la respuesta aparece
cambia("""        ? `<div class="extra-pasar"><a class="btn-llamar" href="tel:${e.tel}">Llamar</a>` +
          `<span class="pista">${telBonito(e.tel)}${e.motivo ? " · " + e.motivo : ""}</span>` +""",
       """        ? `<div class="extra-pasar"><a class="btn-llamar" href="tel:${e.tel}" ` +
          `onclick="marcarLlamada('${e.id}')">Llamar</a>` +
          `<span class="pista">${telBonito(e.tel)}${e.motivo ? " · " + e.motivo : ""}</span>` +""",
       "el botón avisa de que se llamó")

cambia("""            `${e.antesDe}</span>` : "") + `</div>`
        : "") +""",
       """            `${e.antesDe}</span>` : "") + `</div>` +
          (e.llamadoEn || e.respuesta
            ? `<div class="extra-pasar"><span class="pista">Respuesta:</span>` +
              `<input type="text" maxlength="500" id="resp-${e.id}" ` +
              `placeholder="Lo que dijeron…" value="${(e.respuesta || "").replace(/"/g, "&quot;")}">` +
              `<button class="btn-add-2" type="button" ` +
              `onclick="guardarRespuesta('${e.id}')">Guardar</button></div>`
              + (e.llamadoEn ? `<span class="pista" style="margin-left:27px">llamada hecha${
                  e.hRespuesta ? " · " + e.hRespuesta : ""}</span>` : "")
            : "")
        : "") +""",
       "la respuesta, al llamar")

cambia("v-2026-10-26-52", "v-2026-10-26-53", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
