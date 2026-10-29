"""El bloque de las tareas extra: aparte, destacando, y funcionando.

Comprueba que cada tarea tiene SU casilla y SU «si no da tiempo» dentro del
propio HTML, sin depender de ningún escuchador.
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

fallos = 0


def ok(nombre, bien, extra=None):
    global fallos
    print(("  OK   " if bien else "  FALLA") + "  " + nombre +
          ("" if bien or extra is None else "  -> " + str(extra)))
    if not bien:
        fallos += 1


i = js.find("function avisoExtras")
j = js.find("function pintaGerencia")
bloque = js[i:j]

print("  === el bloque de las tareas extra ===")
ok("existe el bloque", i > 0 and j > i)
ok("se pinta arriba del día", "let html = avisoExtras()" in js)
ok("sale en las tres pantallas", js.count("avisoExtras()") >= 3, js.count("avisoExtras()"))

print("\n  === y funciona igual que una tarea del día ===")
ok("cada una lleva su casilla", 'class="caja"' in bloque)
ok("se marca con su propia orden", 'onclick="encargoHecho(' in bloque)
ok("lleva «si no da tiempo»", "si no da tiempo:" in bloque)
ok("y la fecha con su propia orden",
   'onchange="if(this.value) moverEncargo(' in bloque)
ok("no depende de ningún escuchador",
   "addEventListener" not in bloque)

print("\n  === y no sale dos veces ===")
ok("ya no va dentro de la lista del día",
   len(__import__("re").findall(r"bloqueEncargos\\(", js)) == 1)
ok("pero la función sigue existiendo para el futuro",
   "function bloqueEncargos" in js)

print("\n  === los tres tipos se distinguen ===")
ok("urgente", 'tag urgente' in bloque)
ok("para arreglar", 'tag arreglar' in bloque)
ok("dice el turno", "por la tarde" in bloque and "por la mañana" in bloque)
ok("dice quién la puso", "la puso" in bloque)

print("\n  === el color del bloque (el morado) ===")
ok("el bloque tiene su estilo", ".aviso-extra" in open("docs/nube/public/index.html", encoding="utf-8").read())
ok("la casilla es morada", "139,92,246" in open("docs/nube/public/index.html", encoding="utf-8").read())

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
