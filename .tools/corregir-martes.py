"""Corrige el martes de la Coordinadora 1 y anade las ausencias con cobertura."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# 1) el martes de la semana 1 de la Coordinadora 1 va libre
t = t.replace(
    "    1: {1: {0: 7.5, 1: 7.5, 3: 7.5, 4: 7.5, 5: 7, 6: 7},",
    "    1: {1: {0: 7.5, 3: 7.5, 4: 7.5, 5: 7, 6: 7},")

# 2) las ausencias y quién cubre
t = t.replace(
    '# El lunes 26/10/2026 empieza la semana 1 de coordinación y oficina.\nCICLO_ANCLA = "2026-10-26"',
    '# Quién está de vacaciones y quién lo cubre.\n'
    'AUSENCIAS = [\n'
    '    {"puesto": "coordinacion", "numero": 2, "desde": "2026-10-19",\n'
    '     "hasta": "2026-10-25", "cubre": "Oficina"},\n'
    ']\n\n'
    '# El lunes 26/10/2026 empieza la semana 1 de coordinación y oficina.\n'
    'CICLO_ANCLA = "2026-10-26"')

# 3) meterlas en DATOS
t = t.replace('        "cicloAncla": CICLO_ANCLA,',
              '        "cicloAncla": CICLO_ANCLA,\n        "ausencias": AUSENCIAS,')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  martes corregido + ausencias metidas")
