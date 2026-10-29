"""Cuenta las tareas de gerencia, para el resumen."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

GRUPOS = [
    ("Día a día (lunes a viernes)", 5, "diarias"),
    ("LUNES · Cofresa (antes de las 11:00)", 3, "pasos"),
    ("LUNES · Digasa: contar y pedir al comercial", 2, "pasos"),
    ("LUNES · la oferta manual del comercial", 3, "pasos"),
    ("LUNES · Digasa: el pedido de planta", 6, "pasos"),
    ("MARTES", 5, "tareas"),
    ("CADA MES · relación de horas", 1, "tarea"),
    ("CADA MES · asesoría fiscal", 5, "cosas"),
    ("CADA MES · hipoteca", 1, "tarea"),
    ("CADA MES · extracto bancario", 4, "pasos"),
    ("OFERTAS · preparar (jueves-viernes)", 3, "pasos"),
    ("OFERTAS · lunes del «hasta» (coordinación)", 2, "pasos"),
    ("OFERTAS · lunes del «hasta» (gerencia)", 1, "paso"),
    ("APERTURA · cuando no hay coordinadora", 0, "todo el patrón"),
]

total = 0
for nombre, c, unidad in GRUPOS:
    print(f"  {nombre:<44} {c:>2} {unidad}")
    total += c
print(f"  {'TOTAL':<44} {total:>2}")
print()
print("  Bloques distintos: 7 (día a día · lunes · martes · mes · ofertas · apertura)")
