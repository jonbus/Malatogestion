"""Los botones de guardar (recuento, pan, arreglar) valen para todos los puestos.

Estaban enganchados dentro de pintaGerencia, así que en tienda y coordinación
no hacían nada: se podía escribir y no se guardaba.
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


# 1 · se atienden en el escuchador delegado, que vale para todos
cambia("""  /* lo que no es la tarea (menús, campos, botones) no se toca aquí */""",
       """  /* los botones de guardar: van aquí para que valgan en TODOS los puestos.
     Antes vivían en la pantalla de la Jefa, así que en tienda no hacían nada. */
  if(e.target.closest("#rec-guardar")){
    e.stopPropagation(); guardarRecuento(); return;
  }
  if(e.target.closest("#tah-guardar")){
    e.stopPropagation();
    guardarTahona(e.target.closest("#tah-guardar").dataset.cual || "entrada");
    return;
  }
  if(e.target.closest("#arr-add")){
    e.stopPropagation(); anadirArreglo(); return;
  }

  /* lo que no es la tarea (menús, campos, botones) no se toca aquí */""",
       "los tres botones, para todos los puestos")

# 2 · y se quitan de donde estaban (Jefa), para no engancharlos dos veces
cambia("""  const ab = document.getElementById("arr-add");
  if(ab) ab.addEventListener("click", anadirArreglo);
  const tg = document.getElementById("tah-guardar");
  if(tg) tg.addEventListener("click", ()=> guardarTahona(tg.dataset.cual || "entrada"));
  const rg = document.getElementById("rec-guardar");
  if(rg) rg.addEventListener("click", guardarRecuento);
""", "", "se quitan los enganches duplicados")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
