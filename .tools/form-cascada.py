"""El formulario de la cascada, dentro de «Añadir una tarea extra».

Solo lo ven coordinación y la Jefa (D-278). Se pueden poner varios hijos.
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


# ---------------------------------------------------------------- 1 · el estado
cambia('let turnoTarea = "", tipoTarea = "extra";',
       '''let turnoTarea = "", tipoTarea = "extra";
/* la cascada que se está montando: cuando se haga esta tarea, qué nace */
let cascHijos = [];''',
       "el estado de los hijos")

cambia("""function horaAhora(){""",
       """function hijoNuevo(){
  return { que: "", p: "tienda", turno: "", cuando: "0" };
}

function ponerHijo(i, campo, valor){
  if(!cascHijos[i]) return;
  cascHijos[i][campo] = valor;
}

function quitarHijo(i){
  cascHijos = cascHijos.filter((_, j) => j !== i);
  pinta();
}

function anadirHijo(){
  cascHijos = cascHijos.concat([hijoNuevo()]);
  pinta();
}

/* un trozo del formulario de la cascada, para cada hijo */
function filaHijo(h, i){
  const opc = (v, txt, actual) =>
    `<option value="${v}"${actual === v ? " selected" : ""}>${txt}</option>`;
  return `<div class="nueva-nota casc-fila">
      <input type="text" maxlength="200" placeholder="Qué hay que hacer después"
             oninput="ponerHijo(${i},'que',this.value)" value="${h.que}"
             style="flex:1 1 190px">
      <select onchange="ponerHijo(${i},'p',this.value)">
        ${opc("tienda","Tienda",h.p)}${opc("coordinacion","Coordinación",h.p)}${opc("gerencia","Jefa",h.p)}
      </select>
      <select onchange="ponerHijo(${i},'turno',this.value)">
        ${opc("","Sin turno",h.turno)}${opc("manana","Mañana",h.turno)}${opc("tarde","Tarde",h.turno)}
      </select>
      <select onchange="ponerHijo(${i},'cuando',this.value)">
        ${opc("0","Ese día",h.cuando)}${opc("1","Al día siguiente",h.cuando)}
        ${opc("2","En 2 días",h.cuando)}${opc("7","En una semana",h.cuando)}
      </select>
      <button class="btn-borrar" type="button" onclick="quitarHijo(${i})">✕</button>
    </div>`;
}

function horaAhora(){""",
       "las funciones de los hijos")

# ---------------------------------------------------------------- 2 · el formulario
cambia("""        <button id="tarea-add" class="btn-add" type="button" onclick="anadirTareaExtra()">Añadir</button>
      </div>`;""",
       """        <button id="tarea-add" class="btn-add" type="button" onclick="anadirTareaExtra()">Añadir</button>
      </div>` +
      /* la cascada: solo coordinación y la Jefa (D-278) */
      ((quien.puesto === "coordinacion" || quien.puesto === "gerencia")
        ? `<div class="casc-caja">
             <b class="casc-tit">Cuando se haga, crear…</b>` +
           cascHijos.map((h, i) => filaHijo(h, i)).join("") +
           `<div class="nueva-nota" style="border:none">
              <button class="btn-add-2" type="button" onclick="anadirHijo()">+ otra</button>
              <span class="pista">Se creará sola al tachar esta tarea</span>
            </div></div>`
        : "");""",
       "el formulario de la cascada")

# ---------------------------------------------------------------- 3 · guardar la cascada
cambia("""  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined,
                        tipo: tipo });""",
       """  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined,
                        tipo: tipo });
  /* la cascada, si se ha montado alguna */
  const hijos = (cascHijos || []).filter(h => (h.que || "").trim());
  if(hijos.length){
    try{
      await fetch("/api/cascada", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quien: quien.id, tarea: t,
          hijos: hijos.map(h => ({
            que: h.que, p: h.p, turno: h.turno || null, cuando: Number(h.cuando) || 0
          }))
        })
      });
      cascadas[t.toLowerCase().trim()] = hijos;
    }catch(e){ /* si la cascada falla, la tarea ya está puesta */ }
  }
  cascHijos = [];""",
       "la cascada se guarda con la tarea")

# ---------------------------------------------------------------- 4 · el estilo
cambia("  .guardado{font-size:11px; color:var(--verde-oscuro); font-weight:700; margin-left:8px}",
       """  .guardado{font-size:11px; color:var(--verde-oscuro); font-weight:700; margin-left:8px}
  .casc-caja{border-left:3px solid var(--ambar); background:#FFFBF2; border-radius:0 10px 10px 0;
             padding:8px 12px; margin:8px 0}
  .casc-tit{display:block; font-size:11px; letter-spacing:.05em; color:#8A4B00;
            text-transform:uppercase; margin-bottom:4px}
  .casc-fila{gap:6px}
  .casc-fila select{font-size:11.5px; padding:5px 6px}""",
       "el estilo de la cascada")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
