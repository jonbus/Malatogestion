"""La app: tipo en el formulario, y tickar + pasar en las tareas extra."""
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


# ---------------------------------------------------------------- 1 · el tipo, en el formulario
cambia("""        <select id="tarea-turno">
          <option value=""${turnoTarea===""?" selected":""}>Sin turno</option>
          <option value="manana"${turnoTarea==="manana"?" selected":""}>Mañana</option>
          <option value="tarde"${turnoTarea==="tarde"?" selected":""}>Tarde</option>
        </select>""",
       """        <select id="tarea-turno">
          <option value=""${turnoTarea===""?" selected":""}>Sin turno</option>
          <option value="manana"${turnoTarea==="manana"?" selected":""}>Mañana</option>
          <option value="tarde"${turnoTarea==="tarde"?" selected":""}>Tarde</option>
        </select>
        <select id="tarea-tipo" title="Extra: cuando se pueda · Urgente: hoy y ya">
          <option value="extra"${tipoTarea==="extra"?" selected":""}>Extra</option>
          <option value="urgente"${tipoTarea==="urgente"?" selected":""}>Urgente</option>
        </select>""",
       "el desplegable de tipo")

cambia('let turnoTarea = "";', 'let turnoTarea = "", tipoTarea = "extra";',
       "la variable del tipo")

cambia("""  document.getElementById("tarea-turno") && document.getElementById("tarea-turno")
    .addEventListener("change", e=>{ turnoTarea = e.target.value; });""",
       """  document.getElementById("tarea-turno") && document.getElementById("tarea-turno")
    .addEventListener("change", e=>{ turnoTarea = e.target.value; });
  document.getElementById("tarea-tipo") && document.getElementById("tarea-tipo")
    .addEventListener("change", e=>{ tipoTarea = e.target.value; });""",
       "el enganche del tipo")

cambia("  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined });",
       "  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined,\n"
       "                        tipo: tipoTarea });",
       "se manda el tipo")

cambia("""  const dondePuesto = NOMBRE_PUESTO[puesto] || puesto;""",
       """  tipoTarea = "extra";
  const dondePuesto = NOMBRE_PUESTO[puesto] || puesto;""",
       "el tipo se reinicia")

# ---------------------------------------------------------------- 2 · la tarea extra: se marca y se pasa
cambia("""    const borrar = (quien.puesto === "gerencia")
      ? `<div class="pasarlo"><button class="btn-borrar" data-borrar-enc="${e.id}">Borrar</button></div>`
      : "";
    html += `<div class="item" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${que}
        <span class="extra-de">${cuando} · ${de}</span></span></div>${borrar}</div>`;""",
       """    const urgente = e.tipo === "urgente";
    const etiqueta = urgente ? `<span class="tag urgente">URGENTE</span>` : "";
    /* se puede pasar a otro día, igual que las del día */
    const mover = `<div class="pasarlo"><span class="pista">Si no da tiempo:</span>` +
      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}"` +
      ` title="Pasarlo a otro día"></div>`;
    const borrar = (quien.puesto === "gerencia")
      ? `<div class="pasarlo"><button class="btn-borrar" data-borrar-enc="${e.id}">Borrar</button></div>`
      : "";
    html += `<div class="item ${urgente ? "es-urgente" : ""}" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${etiqueta}${que}
        <span class="extra-de">${cuando} · ${de}</span></span></div>${mover}${borrar}</div>`;""",
       "la tarea extra se marca y se puede pasar")

# ---------------------------------------------------------------- 3 · mover el encargo
cambia("function bloqueEncargos(puesto, fecha, turno, titulo){",
       """async function moverEncargo(id, f){
  ponerSync("trabajando", "Pasando la tarea…");
  try{
    const r = await fetch("/api/encargo-mover", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, f: f })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    ponerSync("ok", "Pasada al " + bonito(f));
  }catch(e){
    ponerSync("error", "No se pudo pasar");
  }
  pinta();
}

function bloqueEncargos(puesto, fecha, turno, titulo){""",
       "la función que mueve la tarea")

# ---------------------------------------------------------------- 4 · el enganche del «pasarlo»
cambia("  document.querySelectorAll(\"[data-borrar-enc]\").forEach(b=>{",
       """  c.querySelectorAll(".inp-enc").forEach(inp=>{
    inp.addEventListener("change", async e=>{
      if(!inp.value) return;
      await moverEncargo(inp.dataset.enc, inp.value);
    });
  });
  c.querySelectorAll("[data-borrar-enc]").forEach(b=>{""",
       "el enganche del pasarlo")

# ---------------------------------------------------------------- 5 · el estilo de urgente
cambia("  .tag.ausente{background:#FDE7C8; color:#8A4B00}",
       """  .tag.ausente{background:#FDE7C8; color:#8A4B00}
  .item.es-urgente .cab-item{border-left:3px solid var(--rojo); padding-left:9px}
  .tag.urgente{background:#FDE8E6; color:var(--rojo); font-weight:700}""",
       "el estilo de urgente")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
