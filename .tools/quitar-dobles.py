"""El botón de abrir el formulario cambiaba el estado dos veces: se quedaba cerrado.

Había DOS manejadores en el mismo botón: uno puesto en el propio botón y otro
añadido aparte. Los dos hacen `formTarea = !formTarea`, así que se anulaban:
true y luego false. El formulario no se abría nunca.

Y lo mismo con otros botones: dos manejadores hacían la acción dos veces.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def quita(viejo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   (no estaba) {etiqueta}")
        return
    t = t.replace(viejo, "", 1)
    print(f"   ok  quitado: {etiqueta}")


# 1 · el que anulaba el botón de abrir el formulario
quita("""  document.getElementById("btn-nueva-tarea").addEventListener("click", ()=>{
    formTarea = !formTarea;
    pinta();
  });
""", "el doble del botón de abrir la tarea extra")

# 2 · los campos de la tarea extra (ya llevan su orden dentro)
quita("""  document.getElementById("tarea-puesto") && document.getElementById("tarea-puesto")
    .addEventListener("change", e=>{ puestoTarea = e.target.value; });
""", "el doble del puesto")

quita("""  document.getElementById("tarea-turno") && document.getElementById("tarea-turno")
    .addEventListener("change", e=>{ turnoTarea = e.target.value; });
""", "el doble del turno")

quita("""  document.getElementById("tarea-tipo") && document.getElementById("tarea-tipo")
    .addEventListener("change", e=>{ tipoTarea = e.target.value; });
""", "el doble del tipo")

quita("""  document.getElementById("tarea-add") && document.getElementById("tarea-add")
    .addEventListener("click", anadirTareaExtra);
""", "el doble del botón de añadir")

# 3 · los del encargo (el botón de abrir ya no cambia el estado, así que no se anula,
#     pero los demás sí hacen la acción dos veces)
quita("""  const en1 = document.getElementById("enc-nueva");
  if(en1) en1.addEventListener("click", ()=>{ formEncargo = true; pinta(); });
  const eq = document.getElementById("enc-que");
  if(eq) eq.addEventListener("input", ()=>{ encQue = eq.value; });
  const ec = document.getElementById("enc-cli");
  if(ec) ec.addEventListener("input", ()=>{ encCliente = ec.value; });
  const et = document.getElementById("enc-tipo");
  if(et) et.addEventListener("change", ()=>{ encTipo = et.value; pinta(); });
  const ed = document.getElementById("enc-desde");
  if(ed) ed.addEventListener("change", ()=>{ encDesde = ed.value; });
  const eh = document.getElementById("enc-hasta");
  if(eh) eh.addEventListener("change", ()=>{ encHasta = eh.value; });
  const ea = document.getElementById("enc-antes");
  if(ea) ea.addEventListener("change", ()=>{ encAntes = ea.value; });
  const ep = document.getElementById("enc-pide");
  if(ep) ep.addEventListener("change", ()=>{ encPide = ep.value; });
  document.querySelectorAll("[data-encdia]").forEach(b=>{
    b.addEventListener("click", ()=>{
      const i = Number(b.dataset.encdia);
      encDias = encDias.includes(i) ? encDias.filter(x => x !== i) : encDias.concat([i]);
      pinta();
    });
  });
""", "los dobles del formulario del encargo")

# 4 · los de guardar y arreglar (la acción se hacía dos veces: dos envíos)
quita("""  document.querySelectorAll(".inp-enc").forEach(inp=>{
    inp.addEventListener("change", async e=>{
      if(!inp.value) return;
      await moverEncargo(inp.dataset.enc, inp.value);
    });
  });
""", "(el de pasar el encargo: se queda, es el único)")

quita("""  const at = document.getElementById("arr-txt");
  if(at){
    at.addEventListener("input", ()=>{ textoArreglo = at.value; });
    at.addEventListener("keydown", e=>{ if(e.key === "Enter"){ e.preventDefault(); anadirArreglo(); } });
  }
  const ab = document.getElementById("arr-add");
  if(ab) ab.addEventListener("click", anadirArreglo);
""", "los dobles de «Para arreglar»")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
