"""Arregla: enganchar() no existía. Y Turnos pasa a una pestaña General."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t
lineas = t.splitlines()

# ---------------------------------------------------- 1) sacar el bloque de enganche
ini = next(i for i, l in enumerate(lineas) if 'c.querySelectorAll(".item")' in l)
prof, fin = 0, ini
for i in range(ini, len(lineas)):
    prof += lineas[i].count("{") - lineas[i].count("}")
    if prof == 0 and i > ini:
        fin = i
        break
bloque = lineas[ini:fin + 1]

# la función, con su propio `c`
cuerpo = "\n".join("  " + l if l.strip() else l for l in bloque)
funcion = ("/* engancha los clics de las tareas. Antes esto vivía solo dentro de\n"
           "   pinta(), y la pantalla de la Jefa llamaba a un `enganchar()` que\n"
           "   no existía: se cortaba y no se podía marcar nada. */\n"
           "function engancharItems(){\n"
           "  const c = document.getElementById(\"cuerpo\");\n"
           + cuerpo + "\n}\n")

# el bloque, fuera de pinta() y sustituido por la llamada
t = "\n".join(lineas[:ini] + ["  engancharItems();"] + lineas[fin + 1:])

# la función, delante de pintaTurnos
t = t.replace("function pintaTurnos(){", funcion + "\nfunction pintaTurnos(){", 1)

# la llamada inventada, por la buena
t = t.replace("  enganchar();", "  engancharItems();")

# ---------------------------------------------------- 2) la pestaña General
t = t.replace(
    '["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],["turnos","Turnos"],["calendario","Calendario"]]',
    '["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],["calendario","Calendario"]]')
t = t.replace(
    '["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],["turnos","Turnos"],["calendario","Calendario"]]',
    '["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],["calendario","Calendario"]]')
t = t.replace('if(tab === "turnos"){ pintaTurnos(); return; }',
              'if(tab === "general"){ pintaTurnos(); return; }')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  engancharItems creado y pestaña General preparada")
