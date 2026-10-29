"""Sugerencias también en «cuando se haga, crear», y el pan sin hornear en el cierre."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ 1 · las sugerencias del hijo
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


cambia("function quitarHijo(i){",
       """/* las mismas sugerencias que el campo de la tarea, pero para un hijo */
let SUGHIJO = {};

async function sugerirHijo(i, v){
  let lista = [];
  if(v && String(v).trim().length >= 2){
    try{
      const r = await fetch("/api/sugerencias", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: v })
      });
      const d = await r.json();
      lista = (d.sugerencias || []).slice(0, 8);
    }catch(e){ lista = []; }
  }
  SUGHIJO[i] = lista;
  const caja = document.getElementById("sugh" + i);
  if(!caja) return;
  caja.style.display = lista.length ? "block" : "none";
  caja.innerHTML = lista.map((_, k) =>
    `<div class="sug-linea" onmousedown="elegirHijo(${i},${k})">${lista[k]}</div>`).join("");
}

function elegirHijo(i, k){
  const txt = (SUGHIJO[i] || [])[k];
  if(!txt) return;
  ponerHijo(i, "que", txt);
  SUGHIJO[i] = [];
  const caja = document.getElementById("sugh" + i);
  if(caja){ caja.style.display = "none"; caja.innerHTML = ""; }
  const inp = document.getElementById("hijoq" + i);
  if(inp) inp.value = txt;
}

function quitarHijo(i){""",
       "las sugerencias del hijo")

cambia("""      <input type="text" maxlength="200" placeholder="Qué hay que hacer después"
             oninput="ponerHijo(${i},'que',this.value)" value="${h.que}"
             style="flex:1 1 190px">""",
       """      <div style="flex:1 1 190px; position:relative">
        <input type="text" id="hijoq${i}" maxlength="200" autocomplete="off"
               placeholder="Qué hay que hacer después"
               oninput="ponerHijo(${i},'que',this.value); sugerirHijo(${i}, this.value)"
               value="${h.que}" style="width:100%">
        <div id="sugh${i}" class="sug-caja" style="position:absolute; left:0; right:0"></div>
      </div>""",
       "el campo del hijo con su desplegable")

# ============================================================ 2 · el pan sin hornear
p2 = r".tools/generar-coordinacion.py"
t2 = open(p2, encoding="utf-8").read()
VIEJO = '    "SAB": [{"t": "Subir Cadagua"},'
NUEVO = '    "SAB": [{"t": "Subir Cadagua"},'
# el cierre de coordinación
i = t2.find('CIERRE')
if i < 0:
    print("   NO ENCONTRADO el cierre de coordinación")
    fallos += 1
else:
    print("   ok  el cierre de coordinación existe (se añade la tarea abajo)")

open(p, "w", encoding="utf-8").write(t)
open(p2, "w", encoding="utf-8").write(t2)
print(f"\n  fallos: {fallos}")
