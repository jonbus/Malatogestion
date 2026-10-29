"""Los paneles también en el menú y en la sección de tareas extra.

Ahí se ven las extras y sus botones, pero el panel no se pintaba: parecía que
los botones no hacían nada.
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


# la sección «Tareas extra»
cambia("""function pintaExtra(){
  const c = document.getElementById("cuerpo");
  c.innerHTML = avisoExtras() ||
    `<div class="lista"><p class="pista" style="padding:14px">` +
    `No hay tareas extra para hoy.</p></div>`;""",
       """function pintaExtra(){
  const c = document.getElementById("cuerpo");
  c.innerHTML = panelCascada() + panelEdicion() + (avisoExtras() ||
    `<div class="lista"><p class="pista" style="padding:14px">` +
    `No hay tareas extra para hoy.</p></div>`);""",
       "los paneles en «Tareas extra»")

# el menú del grupo
cambia("""  let html = bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();""",
       """  let html = panelCascada() + panelEdicion() +
    bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();""",
       "los paneles en el menú")

cambia("v-2026-10-26-69", "v-2026-10-26-70", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
