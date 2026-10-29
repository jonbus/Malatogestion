"""El formulario para dar de alta un encargo, en el calendario."""
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


FORM = r'''/* ---------------------------------------------------- el alta de un encargo */
let formEncargo = false, encQue = "", encCliente = "", encTipo = "dia",
    encDesde = "", encHasta = "", encDias = [], encAntes = "1", encPide = "coordinacion";

function bloqueFormEncargo(){
  const lunes = proximoLunes();
  const d = encDesde || fechaSel || lunes;
  let html = `<h2 class="bloque">Encargos<small>lo que hay que tener un día</small></h2>`;
  if(!formEncargo){
    return html + `<div class="lista"><div class="nueva-nota fila-tarea">
        <button id="enc-nueva" class="btn-add-2" type="button">+ Añadir un encargo</button>
        <span class="pista">Si hay que pedirlo antes, saldrá un aviso el día de pedirlo</span>
      </div></div>`;
  }
  html += `<div class="lista"><div class="nueva-nota">
      <input type="text" id="enc-que" maxlength="200" placeholder="Qué es (1 txapata, 25 pollos…)"
             value="${encQue}">
      <input type="text" id="enc-cli" maxlength="60" placeholder="Para quién"
             value="${encCliente}" style="flex:0 1 130px">
    </div>
    <div class="nueva-nota">
      <select id="enc-tipo">
        <option value="dia"${encTipo==="dia"?" selected":""}>Un día</option>
        <option value="rango"${encTipo==="rango"?" selected":""}>Todos los días</option>
        <option value="semana"${encTipo==="semana"?" selected":""}>Varios días de la semana</option>
      </select>
      <input type="date" id="enc-desde" value="${d}">
      ${encTipo === "dia" ? "" : `<span class="pista">hasta</span>
        <input type="date" id="enc-hasta" value="${encHasta || d}">`}
    </div>`;
  if(encTipo === "semana"){
    html += `<div class="nueva-nota"><span class="pista">Los días:</span>` +
      DIAS_CORTOS.map((n, i) =>
        `<button class="dia-btn enc-dia${encDias.includes(i) ? " hoy" : ""}" type="button"
                 data-encdia="${i}">${n}</button>`).join("") + `</div>`;
  }
  html += `<div class="nueva-nota">
      <span class="pista">¿Hay que pedirlo?</span>
      <select id="enc-antes">
        <option value="0"${encAntes==="0"?" selected":""}>No, ya está en la tienda</option>
        <option value="1"${encAntes==="1"?" selected":""}>Sí, 1 día antes</option>
        <option value="2"${encAntes==="2"?" selected":""}>Sí, 2 días antes</option>
        <option value="3"${encAntes==="3"?" selected":""}>Sí, 3 días antes</option>
        <option value="7"${encAntes==="7"?" selected":""}>Sí, 1 semana antes</option>
      </select>
      <span class="pista">lo pide</span>
      <select id="enc-pide">
        <option value="coordinacion"${encPide==="coordinacion"?" selected":""}>Coordinación</option>
        <option value="gerencia"${encPide==="gerencia"?" selected":""}>Jefa</option>
        <option value="tienda"${encPide==="tienda"?" selected":""}>Tienda</option>
      </select>
    </div>
    <div class="nueva-nota" style="border:none">
      <button id="enc-add" class="btn-add" type="button"
              onclick="guardarEncargo()">Añadir el encargo</button>
    </div></div>`;
  return html;
}

async function guardarEncargo(){
  const que = (encQue || "").trim();
  if(!que){ ponerSync("error", "Escribe qué es"); return; }
  const d = encDesde || fechaSel;
  const cuerpo = {
    quien: quien.id, que: que, cliente: encCliente, tipo: encTipo,
    desde: d, hasta: encTipo === "dia" ? d : (encHasta || d),
    dias: encTipo === "semana" ? encDias : [],
    antelacion: Number(encAntes) || 0,
    quienPide: encPide
  };
  ponerSync("trabajando", "Guardando el encargo…");
  try{
    const r = await fetch("/api/encargo-fecha", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo)
    });
    const res = await r.json();
    if(!r.ok) throw new Error(res.error || ("HTTP " + r.status));
    encargosFecha = res.encargosFecha || [];
    formEncargo = false; encQue = ""; encCliente = "";
    ponerSync("ok", "Encargo añadido");
  }catch(e){
    ponerSync("error", "No se pudo: " + e.message);
  }
  pinta();
}

'''

cambia("function bloqueSinDia(pre){", FORM + "function bloqueSinDia(pre){",
       "el formulario del encargo")

# se pinta en el calendario, antes de las notas
cambia("  html += `<div class=\"nueva-nota\">\n      <input type=\"text\" id=\"nota-txt\"",
       "  html += bloqueFormEncargo();\n\n  html += `<div class=\"nueva-nota\">\n      <input type=\"text\" id=\"nota-txt\"",
       "el formulario va en el calendario")

# los enganches
cambia('  const at = document.getElementById("arr-txt");',
       '''  const en1 = document.getElementById("enc-nueva");
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
  const at = document.getElementById("arr-txt");''',
       "los enganches del formulario")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
