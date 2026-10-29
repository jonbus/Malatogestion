"""Comprueba que las tareas extra ya no salen en el calendario y sí en el día."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/nube/public/index.html", encoding="utf-8").read()

pruebas = [
    ("bloque «Tareas extra para este día» en el calendario", "Tareas extra para este día"),
    ("formulario «+ Añadir una tarea extra»", "Añadir una tarea extra"),
    ("la tienda las mete en su día", 'bloqueEncargos("tienda", fechaSel'),
    ("coordinación las mete en su día", 'bloqueEncargos("coordinacion", fechaSel'),
    ("la Jefa las tiene en su bandeja", 'bloqueEncargos("gerencia", DIA'),
    ("versión -24", "v-2026-10-23-24"),
]
for nombre, aguja in pruebas:
    print(f"  {'SÍ ' if aguja in h else 'no '}  {nombre}")

print()
if "Tareas extra para este día" in h:
    print("  OJO: el bloque del calendario sigue")
else:
    print("  el calendario ya NO lista las tareas extra (solo las añade)")
