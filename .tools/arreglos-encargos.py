"""Encargos con turno, Oficina en el desplegable, y los pollos en coordinación."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------- 1) el nucleo acepta turno
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()
if "turno: c.turno" not in t:
    t = t.replace(
        "        diario: c.diario === true,",
        "        diario: c.diario === true,\n"
        "        turno: ['manana','tarde'].includes(c.turno) ? c.turno : null,")
    open(p, "w", encoding="utf-8").write(t)
    print("  nucleo: acepta turno")

# ---------------------------------------------------- 2) los pollos en coordinación
p = r".tools/generar-coordinacion.py"
t = open(p, encoding="utf-8").read()
if "Limpiar pollos" not in t:
    t = t.replace(
        '    {"t": "Arreglar productos que no estén en buen estado"},',
        '    {"t": "Limpiar pollos", "n": "Mínimo 20 ud"},\n'
        '    {"t": "Arreglar productos que no estén en buen estado"},')
    open(p, "w", encoding="utf-8").write(t)
    print("  coordinación: limpiar pollos añadido")
else:
    print("  coordinación: los pollos ya estaban")
