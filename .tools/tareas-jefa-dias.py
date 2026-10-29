"""Tareas nuevas de la Jefa, y cada bloque solo sale su día."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# ---------------------------------------------------- 1) las tareas nuevas
NUEVAS = '''
# Los miércoles: adelantar los pedidos
GER_MIERCOLES = [
    {"t": "Digasa · preparar o adelantar el pedido"},
    {"t": "Cofresa · preparar o adelantar el pedido"},
]

# Frutas Tito: los lunes y los viernes
GER_FRUTAS = [
    {"t": "Frutas Tito · precios y etiquetas",
     "partes": ["Precios", "Etiquetas"]},
]

GER_HOY = ['''
t = t.replace("\nGER_HOY = [", NUEVAS, 1)

# al JSON
t = t.replace('"mes": GER_MES, "ofertas": GER_OFERTAS, "festivos": FESTIVOS_2026,',
              '"mes": GER_MES, "ofertas": GER_OFERTAS, "festivos": FESTIVOS_2026,\n'
              '        "miercoles": GER_MIERCOLES, "frutas": GER_FRUTAS,')

# ---------------------------------------------------- 2) cada bloque, su día
t = t.replace(
    'html += bloque("Los lunes · los pedidos", DATOS.gerencia.lunes, "gl");',
    'if(W === "LUN") html += bloque("Los lunes · los pedidos", DATOS.gerencia.lunes, "gl");')
t = t.replace(
    'html += bloque("Los martes · cerrar lo del lunes", DATOS.gerencia.martes, "gm");',
    'if(W === "MAR") html += bloque("Los martes · cerrar lo del lunes",\n'
    '                      DATOS.gerencia.martes, "gm");')
t = t.replace(
    'html += bloque("Abierto este mes", tareas, "gv");',
    'if(W === "MIE") html += bloque("Los miércoles · adelantar los pedidos",\n'
    '                      DATOS.gerencia.miercoles, "gmi");\n'
    '  if(W === "LUN" || W === "VIE") html += bloque("Frutas Tito · precios y etiquetas",\n'
    '                      DATOS.gerencia.frutas, "gf");\n'
    '  html += bloque("Abierto este mes", tareas, "gv");')

# ---------------------------------------------------- 3) el rótulo de «lo de cada día»
t = t.replace('bloque("Lo de cada día · lunes a viernes", DATOS.gerencia.hoy, "gh")',
              'bloque("Lo de cada día", DATOS.gerencia.hoy, "gh")')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  tareas nuevas y cada bloque en su día")
