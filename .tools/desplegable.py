"""El desplegable de sugerencias bajo el campo de la tarea.

Ojo: NO se repinta la pantalla al escribir — se cambia solo el desplegable.
Si se repintara, se perdería el cursor en cada letra.
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


FUNCIONES = r'''/* ------------------------------------------------ sugerencias al escribir
   Lo que ya se ha escrito alguna vez se ofrece mientras se escribe.
   Se cambia SOLO el desplegable: la pantalla no se repinta, para no perder el cursor. */
let sugerencias = [], sugTiempo = null;

function pintarSugerencias(){
  const caja = document.getElementById("tarea-sug");
  if(!caja) return;
  if(!sugerencias.length){ caja.innerHTML = ""; caja.style.display = "none"; return; }
  caja.style.display = "block";
  caja.innerHTML = sugerencias.map((s, i) =>
    `<div class="sug-linea" onmousedown="elegirSugerencia(${i})">${s}</div>`).join("");
}

async function buscarSugerencias(txt){
  try{
    const r = await fetch("/api/sugerencias", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q: txt })
    });
    const d = await r.json();
    sugerencias = d.sugerencias || [];
  }catch(e){ sugerencias = []; }
  pintarSugerencias();
}

function alEscribirTarea(v){
  textoTarea = v;
  clearTimeout(sugTiempo);
  if(!v || v.trim().length < 2){
    sugerencias = []; pintarSugerencias(); return;
  }
  sugTiempo = setTimeout(()=> buscarSugerencias(v), 220);
}

function elegirSugerencia(i){
  const txt = sugerencias[i];
  if(!txt) return;
  textoTarea = txt;
  sugerencias = [];
  const caja = document.getElementById("tarea-sug");
  if(caja){ caja.innerHTML = ""; caja.style.display = "none"; }
  const inp = document.getElementById("tarea-txt");
  if(inp){ inp.value = txt; inp.focus(); }
}

'''

cambia("function horaAhora(){", FUNCIONES + "function horaAhora(){",
       "las funciones de las sugerencias")

# el campo, con su desplegable debajo
cambia('<input type="text" id="tarea-txt" oninput="textoTarea=this.value" maxlength="300"\n'
       '               placeholder="Qué hay que hacer…" value="${textoTarea}">',
       '<input type="text" id="tarea-txt" oninput="alEscribirTarea(this.value)" maxlength="300"\n'
       '               autocomplete="off" placeholder="Qué hay que hacer…" value="${textoTarea}">\n'
       '        <div id="tarea-sug" class="sug-caja"></div>',
       "el campo y su desplegable")

# el estilo
cambia("  .casc-caja{border-left:3px solid var(--ambar);",
       """  .sug-caja{display:none; position:relative; width:100%; max-height:190px;
            overflow-y:auto; background:#fff; border:1px solid var(--borde);
            border-radius:9px; margin-top:-2px; box-shadow:0 6px 16px rgba(0,0,0,.08); z-index:5}
  .sug-linea{padding:9px 12px; font-size:12.5px; color:var(--tinta); cursor:pointer;
             border-bottom:1px solid #F2F0EC}
  .sug-linea:last-child{border-bottom:none}
  .sug-linea:hover,.sug-linea:active{background:#F7F4EE}
  .casc-caja{border-left:3px solid var(--ambar);""",
       "el estilo del desplegable")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
