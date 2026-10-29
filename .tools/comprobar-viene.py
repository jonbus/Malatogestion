"""Comprueba el bloque «Viene en los próximos días» en la app generada."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/nube/public/index.html", encoding="utf-8").read()

pruebas = [
    ("función bloqueViene", "function bloqueViene"),
    ("la llama la tienda", "bloqueViene(fechaSel)"),
    ("la llama la Jefa", "bloqueViene(DIA)"),
    ("título del bloque", "Viene en los próximos días"),
    ("estilos del bloque", ".viene-fila"),
    ("versión -25", "v-2026-10-23-25"),
    ("el calendario sigue sin listarlas", "Tareas extra para este día"),
]
for nombre, aguja in pruebas:
    if nombre.startswith("el calendario"):
        print(f"  {'MAL  ' if aguja in h else 'OK   '}{nombre} (debe ser OK)")
    else:
        print(f"  {'OK   ' if aguja in h else 'FALTA'}{nombre}")
