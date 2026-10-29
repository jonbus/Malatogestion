"""El disparador: al tachar una tarea, la aplicación lanza su cascada."""
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


FUNCIONES = r'''/* ---------------------------------------------------------- LAS CASCADAS
   Una tarea que, al hacerse, hace nacer la siguiente.
   El hijo NO EXISTE hasta que el padre se hace. */
let cascadas = {};
const TXTENC = {};        /* id del encargo -> su texto, para lanzar la cascada */

async function lanzarCascada(tarea, fecha){
  if(!tarea) return;
  try{
    const r = await fetch("/api/cascada-lanzar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, tarea: tarea, fecha: fecha || fechaSel })
    });
    if(!r.ok) return;
    const d = await r.json();
    if(d.encargos) encargos = d.encargos;
    const nacidos = d.nacidos || [];
    if(nacidos.length){
      ponerSync("ok", "Ha nacido: " + nacidos.map(x => x.t).join(" · "));
      pinta();
    }
  }catch(e){ /* si falla, no se rompe la tarea que sí se marcó */ }
}

'''

cambia("function tocar(k, valor){", FUNCIONES + "function tocar(k, valor){",
       "las funciones de la cascada")

# el disparador al tachar una tarea del día
cambia("""function tocar(k, valor){
  tocarEn(fechaSel, k, valor);""",
       """function tocar(k, valor){
  tocarEn(fechaSel, k, valor);
  /* si esta tarea tiene cascada y se acaba de hacer, nacen las siguientes */
  if(valor && REG[k]) lanzarCascada(REG[k].t, fechaSel);""",
       "el disparador en las tareas del día")

# el disparador al tachar una tarea extra
cambia("""    if(d.encargos) encargos =
      d.encargos || [];""",
       """    if(d.encargos) encargos = d.encargos || [];
    if(!deshacer && TXTENC[id]) lanzarCascada(TXTENC[id], DIA);""",
       "el disparador en las tareas extra")

# el texto de cada extra, para poder lanzar su cascada
cambia("""    const quienLaPuso = nombreDe(e.q);
    const hecho = e.hecho;""",
       """    const quienLaPuso = nombreDe(e.q);
    const hecho = e.hecho;
    TXTENC[e.id] = e.t;""",
       "se guarda el texto de cada extra")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
