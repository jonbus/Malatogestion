"""La Jefa también con botones en la pantalla principal, como el resto."""
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


# 1 · los botones de la Jefa
cambia("""  coordinacion: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"],
    ["apertura", "Apertura", "🔑"],
    ["dia", "El día", "📋"],
    ["cierre", "Cierre", "🌙"]
  ]""",
       """  coordinacion: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"],
    ["apertura", "Apertura", "🔑"],
    ["dia", "El día", "📋"],
    ["cierre", "Cierre", "🌙"]
  ],
  gerencia: [
    ["general", "El día", "📋"],
    ["turno", "Turno", "📅"],
    ["calendario", "Calendario", "🗓"],
    ["panes", "Registro de panes", "🍞"],
    ["extra", "Tareas extra", "📌"]
  ]""",
       "los botones de la Jefa")

# 2 · el menú vale para todos
cambia("""  /* tienda y coordinación: primero el menú de botones (D-284) */
  if(quien.puesto !== "gerencia"){
    if(!tab || tab === "menu"){ pintaMenu(); return; }
    if(tab === "panes"){ pintaPanes(); return; }
    if(tab === "extra"){ pintaExtra(); return; }
  }""",
       """  /* el menú de botones, para TODOS (D-284): la Jefa también */
  if(!tab || tab === "menu"){ pintaMenu(); return; }
  if(tab === "panes"){ pintaPanes(); return; }
  if(tab === "extra"){ pintaExtra(); return; }""",
       "el menú para todos")

# 3 · la barra de arriba: también para la Jefa
cambia("""  if(quien.puesto !== "gerencia"){
    /* sin barra de pestañas: un solo botón para volver al menú */
    tab = tab || "menu";
    if(tab === "menu") return;
    const b = document.createElement("button");
    b.className = "tab";
    b.type = "button";
    b.textContent = "◀ Menú";
    b.addEventListener("click", ()=>{ tab = "menu"; pintaTabs(); pinta(); });
    c.appendChild(b);
    return;
  }
  const lista = [["general","El día"],["turno","Turno"],["calendario","Calendario"]];
  if(!tab) tab = lista[0][0];""",
       """  /* sin barra de pestañas: un solo botón para volver al menú, para todos */
  tab = tab || "menu";
  if(tab === "menu") return;
  const b = document.createElement("button");
  b.className = "tab";
  b.type = "button";
  b.textContent = "◀ Menú";
  b.addEventListener("click", ()=>{ tab = "menu"; pintaTabs(); pinta(); });
  c.appendChild(b);
  return;
  const lista = [];""",
       "la vuelta al menú, para todos")

cambia("v-2026-10-26-68", "v-2026-10-26-69", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
