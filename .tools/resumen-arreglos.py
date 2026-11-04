"""Dos arreglos del resumen.

1 · pintaba la pantalla por su cuenta y luego la vaciaba el que lo llama.
    Ahora devuelve el HTML, como todos los demás.
2 · al volver a encargos no se limpiaba el estado, y se quedaba en el resumen.
3 · y si no hay encargos, enseña los días igual, con «sin encargos».
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    elif t.count(v) == 0:
        print("  NO ENCONTRADO: " + e)
    else:
        print(f"  OJO, aparece {t.count(v)} veces: " + e)


# --- 1 · el resumen devuelve el HTML, no lo pinta él
rep("""  if(!dias.length){
    return html + `<div class="lista"><p class="pista" style="padding:14px">
      Todavía no hay encargos.</p></div>`;
  }""",
    """  if(!dias.length){
    /* aunque no haya nada, se ven los días: hoy y mañana, vacíos */
    const hoy = DIA;
    const manana = diaDeManana().slice(0, 10);
    for(const f of [hoy, manana]){
      html += `<div class="lista"><div class="item">
        <div class="cab-item"><span class="txt"><b>${bonito(f)}</b>
          <span class="n">sin encargos</span></span></div>
      </div></div>`;
    }
    return html;
  }""",
    "el resumen vacío enseña los días")

rep("""    html += `</div></div>`;
  });

  c.innerHTML = html;
}""",
    """    html += `</div></div>`;
  });

  return html;
}""",
    "el resumen devuelve el HTML")

rep("""function pintaResumenEncargos(){
  const c = document.getElementById("cuerpo");
""",
    """function pintaResumenEncargos(){
""",
    "sin coger el cuerpo por su cuenta")

# --- 2 · al entrar en encargos, siempre se limpia
rep('  if(k !== "calendario"){ formEncargo = false; encProveedor = ""; resumenEncargos = false; }',
    '  /* cada vez que se entra, se empieza por los tres botones */\n  formEncargo = false; encProveedor = ""; resumenEncargos = false;',
    "al entrar, siempre se limpia")

rep("v-2026-10-26-93", "v-2026-10-26-94", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
