"""Las tareas extra van DENTRO de las tareas del dia, y dejan de llamarse encargos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# --- 1) bloque() acepta contenido extra, que se pinta DENTRO de la misma lista
t = t.replace(
    "function bloque(titulo, tareas, pre){\n  if(!tareas || !tareas.length) return \"\";",
    "function bloque(titulo, tareas, pre, extra){\n"
    "  if(!tareas || !tareas.length) return extra || \"\";")
t = t.replace(
    "    html += `<div class=\"item ${completa?\"hecha\":\"\"} ${abierta?\"abierta\":\"\"}\" data-k=\"${k}\">\n"
    "        <div class=\"cab-item\"><span class=\"caja ${parcial?\"parcial\":\"\"}\"></span>\n"
    "        <span class=\"txt\"><b>${t.t}</b>${fuera}${cuenta}${n}</span></div>${sub}</div>`;\n"
    "  });\n  return html + \"</div>\";\n}",
    "    html += `<div class=\"item ${completa?\"hecha\":\"\"} ${abierta?\"abierta\":\"\"}\" data-k=\"${k}\">\n"
    "        <div class=\"cab-item\"><span class=\"caja ${parcial?\"parcial\":\"\"}\"></span>\n"
    "        <span class=\"txt\"><b>${t.t}</b>${fuera}${cuenta}${n}</span></div>${sub}</div>`;\n"
    "  });\n  return html + (extra || \"\") + \"</div>\";\n}")

# --- 2) las extra piden id, no indice: se marcan por su id
t = t.replace(
    "const ENC = {};   // encargos en pantalla",
    "const ENC = {};   // tareas extra en pantalla")

# --- 3) el nombre: de encargos a tareas extra
t = t.replace("Encargos del día", "Tareas extra")
t = t.replace("Lo que te han pasado", "Tareas extra")
t = t.replace("+ Encargar una tarea", "+ Añadir una tarea extra")
t = t.replace("Se le aparecerá a ese puesto en su día", "Se le añadirá a sus tareas de ese día y turno")
t = t.replace("Tareas encargadas para este día", "Tareas extra para este día")
t = t.replace("encargarTarea", "anadirTareaExtra")

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  renombrado y preparado para meterlas en la lista")
