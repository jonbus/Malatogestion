"""La tarea extra: se tica y se pasa de día con su propia orden dentro."""
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


# el campo de pasar, con su orden dentro
cambia("""      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}"` +
      ` title="Pasarlo a otro día"></div>`;""",
       """      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}"` +
      ` onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)"` +
      ` title="Pasarlo a otro día"></div>`;""",
       "el campo de pasar el día")

# la tarea entera, con su orden dentro para marcarla
cambia("""    html += `<div class="item ${urgente ? "es-urgente" : ""}${arreglo ? " es-arreglar" : ""}" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>""",
       """    html += `<div class="item ${urgente ? "es-urgente" : ""}${arreglo ? " es-arreglar" : ""}" data-k="${k}">
        <div class="cab-item" onclick="encargoHecho('${e.id}')"><span class="caja"></span>""",
       "la tarea se marca con su propia orden")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
