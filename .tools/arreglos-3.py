"""Tres arreglos: destachar, el pan que parece no guardarse, y el texto de arreglar."""
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


cambia_srv("""      const e = estado.encargos.find(x => String(x.id) === String(cuerpo.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      e.hecho = true;""",
           """      const e = estado.encargos.find(x => String(x.id) === String(cuerpo.id));
      if (!e) return { status: 404, body: { ok: false, error: 'no existe esa tarea' } };
      /* se puede marcar y DESMARCAR: si alguien le dio sin querer, se deshace */
      e.hecho = cuerpo.deshacer ? false : true;
      if (e.hecho) { e.hHecho = hora; } else { delete e.hHecho; }""",
           "el encargo se puede desmarcar")

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


# --- 1 · la tachada se puede destachar
cambia("""    html += `<div class="extra-linea ${urgente?"es-urgente":""}${hecho?" hecha":""}" ` +
      `${hecho ? "" : `onclick="encargoHecho('${e.id}')"`}>` +""",
       """    html += `<div class="extra-linea ${urgente?"es-urgente":""}${hecho?" hecha":""}" ` +
      `onclick="encargoHecho('${e.id}', ${hecho ? "true" : "false"})">` +""",
       "la tachada se puede destachar")

cambia("""      (hecho ? "" :
        `<span class="pista">si no da tiempo:</span>` +
        `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
        `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)">`) +
      `</div>`;""",
       """      (hecho ? `<span class="pista">toca para destacharla</span>` :
        `<span class="pista">si no da tiempo:</span>` +
        `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
        `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)">`) +
      `</div>`;""",
       "y dice cómo destacharla")

# --- 2 · encargoHecho acepta deshacer
cambia("""async function encargoHecho(id){
  ponerSync("trabajando", "Marcando…");
  try{
    const r = await fetch("/api/encargo-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, quien: quien.id })
    });""",
       """async function encargoHecho(id, deshacer){
  ponerSync("trabajando", deshacer ? "Deshaciendo…" : "Marcando…");
  try{
    const r = await fetch("/api/encargo-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, quien: quien.id, deshacer: !!deshacer })
    });""",
       "encargoHecho entiende deshacer")

# --- 3 · el pan: decir claro que se guardó
cambia("""    `<button id="tah-guardar" class="btn-add" type="button" ` +
    `data-cual="${cual}" onclick="guardarTahona(this.dataset.cual)">` +
    `Guardar el pan</button></div></div>`;""",
       """    `<button id="tah-guardar" class="btn-add" type="button" ` +
    `data-cual="${cual}" onclick="guardarTahona(this.dataset.cual)">` +
    `Guardar el pan</button>` +
    (dia[`guardado_${cual}`]
      ? `<span class="guardado">✓ guardado a las ${dia[`guardado_${cual}`]}</span>` : "") +
    `</div></div>`;""",
       "el pan dice a qué hora se guardó")

cambia("""    const d = await r.json();
    tahona = d.tahona || {};
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Pan guardado");""",
       """    const d = await r.json();
    tahona = d.tahona || {};
    if(d.hora && tahona[fechaSel]) tahona[fechaSel]["guardado_" + cual] = d.hora;
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Pan guardado");""",
       "la hora del guardado se apunta")

# --- 4 · el texto de «arreglar»
cambia('`<p class="pista" style="padding:0 14px">Apunta aquí lo que veas: un caducado, fruta fea, algo roto.</p></div>`;',
       '`<p class="pista" style="padding:0 14px">Se apunta como una tarea más: se tacha al hacerla,' +
       ` o se pasa a otro día si no da tiempo.</p></div>`;`,
       "el texto de «para arreglar»")

# --- el estilo del «guardado»
cambia("  .extra-txt{flex:1 1 auto}",
       """  .extra-txt{flex:1 1 auto}
  .guardado{font-size:11px; color:var(--verde-oscuro); font-weight:700; margin-left:8px}""",
       "el estilo de «guardado»")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
