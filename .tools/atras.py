"""El botón de atrás del navegador: que vuelva al paso anterior, no que salga.

La aplicación cambiaba de pantalla sin avisar al navegador. Así, «atrás» se
salía de la aplicación en vez de volver.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


CAPA = r'''/* ------------------------------------------------ EL BOTÓN DE ATRÁS DEL NAVEGADOR
   Cada vez que se cambia de pantalla se avisa al navegador, para que «atrás»
   vuelva al paso anterior y no se salga de la aplicación. */
function guardaVista(){
  try{
    history.pushState(
      { t: tab || "menu", f: fechaSel, p: panCual, e: editando || "", c: tab },
      ""
    );
  }catch(e){}
}

function vuelveVista(s){
  s = s || {};
  tab = s.t || "menu";
  if(s.f) fechaSel = s.f;
  if(s.p) panCual = s.p;
  editando = s.e || "";
  pintaTabs();
  pinta();
}

window.addEventListener("popstate", function(ev){
  vuelveVista(ev.state);
});

function abrirSeccion(k){'''

rep("function abrirSeccion(k){", CAPA, "la capa del historial")

rep("""function abrirSeccion(k){
  tab = k;
  pintaTabs();

  /* sin esto no aparece el boton de volver */
  pinta();
}""",
    """function abrirSeccion(k){
  tab = k;
  pintaTabs();

  /* sin esto no aparece el boton de volver */
  pinta();
  guardaVista();
}""",
    "abrirSeccion avisa al navegador")

rep("""b.addEventListener("click", ()=>{ tab = "menu"; pintaTabs(); pinta(); });""",
    """b.addEventListener("click", ()=>{ tab = "menu"; pintaTabs(); pinta(); guardaVista(); });""",
    "el botón de volver al menú")

rep("""  fechaSel = d.toISOString().slice(0, 10);
  pinta();
}""",
    """  fechaSel = d.toISOString().slice(0, 10);
  pinta();
  guardaVista();
}""",
    "mover el día de Zuaza")

rep("""function verPan(c){
  panCual = (c === "devolucion") ? "devolucion" : "entrada";
  pinta();
}""",
    """function verPan(c){
  panCual = (c === "devolucion") ? "devolucion" : "entrada";
  pinta();
  guardaVista();
}""",
    "cambiar de entrada a devolución")

# la primera vista: se deja una huella para que «atrás» no salga de golpe
rep("  entrar();\n});", "  entrar();\n  guardaVista();\n});", "la huella al entrar")

rep("v-2026-10-26-81", "v-2026-10-26-82", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
