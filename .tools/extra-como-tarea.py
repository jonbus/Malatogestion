"""La tarea extra deja de ser un cartel y pasa a ser una tarea más del día.

El aviso de arriba desaparece: las tareas extra se pintan DENTRO de la lista del
día, con las demás, y se marcan y se pasan igual. Un aviso aparte solo informa;
una tarea se hace.
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


# 1 · fuera el cartel de delante de todo
cambia("  let html = avisoExtras(), total = 0, hechos = 0;",
       "  let html = \"\", total = 0, hechos = 0;   /* las extra van dentro de la lista del día */",
       "fuera el cartel (tienda y coordinación)")

cambia("  let html = avisoExtras();",
       "  let html = \"\";   /* las extra van dentro de la lista del día */",
       "fuera el cartel (la Jefa)")

# 2 · la tarea extra, dentro de «Lo de hoy», con el mismo aspecto que las demás
cambia("""    html += `<div class="item ${urgente ? "es-urgente" : ""}${arreglo ? " es-arreglar" : ""}" data-k="${k}">
        <div class="cab-item" onclick="encargoHecho('${e.id}')"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${etiqueta}${que}
        <span class="extra-de">${cuando} · ${de}</span></span></div>${mover}${borrar}</div>`;""",
       """    html += `<div class="item ${urgente ? "es-urgente" : ""}${arreglo ? " es-arreglar" : ""} es-extra" data-k="${k}">
        <div class="cab-item" onclick="encargoHecho('${e.id}')"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${etiqueta}${que}
        <span class="extra-de">${de}</span></span></div>${mover}${borrar}</div>`;""",
       "la tarea extra, como una más del día")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
