"""Comprueba las cuentas de HORAS-ANUALES.md."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

SEMANAS = 43.65

PERSONAS = [
    ("Tienda 1", 20.33, 938.5),
    ("Tienda 2", 20.33, 938.5),
    ("Tienda 3", 20.33, 938.5),
    ("Coordinadora 1", 31.25, 1396.8),
    ("Coordinadora 2", 21.00, 938.5),
    ("Gerencia", 39.125, 2034.0),
]

print(f"  semanas al año (1.396,8 / 32 = {1396.8/32:.2f})  ->  {SEMANAS}")
print()
print(f"  {'Persona':<16} {'h/sem':>7} {'al año':>9} {'contrato':>10} {'pendientes':>11}")
print("  " + "-" * 58)

total_equipo = 0.0
for nombre, semanal, contrato in PERSONAS:
    anio = semanal * SEMANAS
    dif = anio - contrato
    print(f"  {nombre:<16} {semanal:>7.2f} {anio:>9.0f} {contrato:>10.1f} {dif:>+11.0f}")
    if nombre != "Gerencia":
        total_equipo += abs(dif)

print("  " + "-" * 58)
print(f"  {'TOTAL equipo (sin gerencia)':<16} {'':>7} {'':>9} {'':>10} {total_equipo:>+11.0f}")

print()
print("  === comprobación del divisor ===")
print(f"  1.396,8 / 32   = {1396.8/32:.2f}  semanas")
print(f"  938,5 / 21,5   = {938.5/21.5:.2f}  semanas  (cuadra)")
print(f"  938,5 / 21,0   = {938.5/21.0:.2f}  semanas")

print()
print("  === el verano que hay que absorber ===")
print(f"  una ausencia de tienda de 30 días: 22 días x 6,5 h = {22*6.5:.0f} h")
print(f"  margen disponible:                                    {total_equipo:.0f} h")
print(f"  cuántas ausencias de tienda cubre:                    {total_equipo/(22*6.5):.1f}")
