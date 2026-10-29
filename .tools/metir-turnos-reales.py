"""Sustituye los turnos por los de la plantilla real (PlantillasHorarios.xlsx)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

NUEVO = '''# Los turnos REALES, sacados de PlantillasHorarios.xlsx (carpeta de siempre).
# Cuadran con el documento: tienda 20,33 h/semana · coord. 31,25 y 21,0.
#
# Horas de cada tramo: 11-14,30=3,5 · 9,30-14,30=5 · 10,30-15=4,5 · 17-21,30=4,5
#   9-15=6 · 7-14,30=7,5 · 8-15=7 · 10-15=5 · 7-13,30=6,5 · 9-12=3 · 7-13=6 · 8-10=2

# Los tres turnos de tienda (lunes=0 ... domingo=6)
TURNOS_TIENDA = {
    "A": {"nombre": "Mañanas y sábado",
          "dias": {1: 3.5, 2: 3.5, 3: 5, 4: 3.5, 5: 4.5}},            # 20,0 h
    "B": {"nombre": "Lunes mañana y tardes",
          "dias": {0: 3.5, 1: 4.5, 2: 4.5, 3: 4.5, 4: 4.5}},          # 21,5 h
    "C": {"nombre": "Domingo entero y tardes",
          "dias": {0: 4.5, 5: 4.5, 6: 10.5}},                          # 19,5 h
}
TIENDA_ANCLA = "2026-10-19"          # la semana que se dictó...
TIENDA_SEMANA_ANCLA = 3              # ...era la semana 3 del ciclo
TIENDA_SEMANAS = {
    1: {1: "A", 2: "B", 3: "C"},
    2: {1: "B", 2: "C", 3: "A"},
    3: {1: "C", 2: "A", 3: "B"},
}

# Las cuatro semanas de coordinación, tal cual la hoja
COORD_SEMANAS = {
    1: {1: {0: 7.5, 3: 7.5, 4: 7.5, 5: 7, 6: 6},
        2: {2: 6.5, 3: 3}},
    2: {1: {0: 7.5, 2: 6.5, 3: 7.5, 5: 5, 6: 6},
        2: {3: 3, 4: 7.5, 5: 7, 6: 7}},
    3: {1: {0: 7.5, 2: 6.5, 3: 7.5},
        2: {3: 3, 4: 7.5, 5: 7, 6: 6}},
    4: {1: {2: 6.5, 3: 7.5, 4: 7.5, 5: 7, 6: 7},
        2: {0: 6.5, 3: 3, 4: 6, 5: 5, 6: 6}},
}

# Las cuatro semanas de la oficina (hoja «Turnos Gerencia»)
OFICINA_SEMANAS = {
    1: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5, 4: 7.5, 6: 7},
    2: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5, 4: 7.5},
    3: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5, 4: 7.5, 5: 2, 6: 7},
    4: {0: 7.5, 1: 7.5, 2: 7.5, 3: 7.5},
}
'''

# quitar el bloque viejo de turnos y poner el nuevo
ini = t.index("# ============================================================== TURNOS")
fin = t.index("# El lunes 26/10/2026 empieza la semana 1 de coordinación y oficina.")
t = t[:ini] + NUEVO + "AUSENCIAS = " + t[t.index("AUSENCIAS = ", ini):fin] + t[fin:]

# el ancla del ciclo de coordinación sigue: el 26/10 es semana 1

if t == antes:
    print("  SIN CAMBIOS")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  turnos reales metidos")
