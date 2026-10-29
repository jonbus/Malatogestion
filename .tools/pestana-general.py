"""Pestaña General para todos, y pestañas también para la Jefa."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# --- 1) las pestañas de cada puesto
t = t.replace(
    '''  if(quien.puesto === "gerencia") return;

  const lista = quien.puesto === "tienda"
    ? [["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],["calendario","Calendario"]]
    : [["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],["calendario","Calendario"]];''',
    '''  const lista = quien.puesto === "tienda"
    ? [["general","General"],["manana","Mañana"],["tarde","Tarde"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : quien.puesto === "coordinacion"
    ? [["general","General"],["apertura","Apertura"],["dia","El día"],["cierre","Cierre"],
       ["calendario","Calendario"]]
    : [["bandeja","Bandeja"],["general","General"],["calendario","Calendario"]];''')

# --- 2) a dónde va cada pestaña
t = t.replace(
    '  if(quien.puesto === "gerencia"){ pintaGerencia(); return; }',
    '  if(quien.puesto === "gerencia"){\n'
    '    if(tab === "general"){ pintaTurnos(); return; }\n'
    '    if(tab === "calendario"){ pintaCalendario(); return; }\n'
    '    pintaGerencia(); return;\n'
    '  }')

# --- 3) la pestaña general, para todos
t = t.replace('if(tab === "general"){ pintaTurnos(); return; }',
              'if(tab === "general"){ pintaTurnos(); return; }')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  General para todos y pestañas para la Jefa")
