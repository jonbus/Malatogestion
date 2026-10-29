"""El calendario, con tres botones: encargos, llamadas y tareas.

Al entrar se ve el calendario y los tres botones; cada uno abre lo suyo.
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


# 1 · el estado
cambia("let llamPara = \"\";    /* para qué puesto es la llamada */",
       "let llamPara = \"\";    /* para qué puesto es la llamada */\n"
       "let calBloque = \"\";   /* qué bloque del calendario está abierto */",
       "el estado del calendario")

cambia("function pintaCalendario(){",
       """function abrirCal(k){
  calBloque = (calBloque === k) ? "" : k;
  pinta();
}

function pintaCalendario(){""",
       "abrir y cerrar un bloque del calendario")

# 2 · los tres botones, antes de las notas
cambia("""  html += bloqueLlamada();
  html += bloqueFormEncargo();""",
       """  /* los tres botones: el calendario primero, y luego lo que se quiera hacer */
  html += `<div class="menu-grupo cal-menu">` +
    [["encargos", "Encargos"], ["llamadas", "Llamadas"], ["tareas", "Tareas"]]
      .map(([k, n]) => `<button class="menu-btn${calBloque === k ? " activo" : ""}" ` +
        `type="button" onclick="abrirCal('${k}')"><b>${n}</b></button>`).join("") +
    `</div>`;

  if(calBloque === "llamadas") html += bloqueLlamada();
  if(calBloque === "encargos") html += bloqueFormEncargo();""",
       "los tres botones del calendario")

# 3 · la tarea extra, solo cuando se abre «Tareas»
cambia("""  /* anadir una tarea extra a un puesto para este día */
  html += `<div class="nueva-nota fila-tarea">""",
       """  /* anadir una tarea extra a un puesto para este día */
  if(calBloque === "tareas") html += `<div class="nueva-nota fila-tarea">""",
       "la tarea extra, tras su botón")

cambia("  if(formTarea){\n    const ops =",
       "  if(formTarea && calBloque === \"tareas\"){\n    const ops =",
       "el formulario de la tarea, tras su botón")

# 4 · el estilo del botón abierto
cambia("  .menu-btn:active{background:#F4F1EA}",
       """  .menu-btn:active{background:#F4F1EA}
  .menu-btn.activo{background:var(--verde-oscuro); border-color:var(--verde-oscuro)}
  .menu-btn.activo b{color:#fff}
  .cal-menu{margin:10px 0 4px}""",
       "el botón abierto se marca")

cambia("v-2026-10-26-56", "v-2026-10-26-57", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
